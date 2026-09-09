import json
import os
import secrets
from datetime import datetime

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from firebase_admin import auth as firebase_auth
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    create_session_token,
    get_current_user,
    hash_password,
    verify_password,
)
from collections import defaultdict
from sqlalchemy import text
from database import Base, engine, get_db
from models import User, UserPreference, Notification, PushSubscription
from firebase_admin import messaging
from admin_seed import ensure_admin_seed
from admin_auth import get_current_admin, verify_admin_credentials, create_admin_session_token, ADMIN_SESSION_COOKIE
from passlib.hash import bcrypt

FIREBASE_VAPID_KEY = os.environ.get("FIREBASE_VAPID_KEY", "")

FIREBASE_CONFIG_JSON = json.dumps({
    "apiKey": os.environ["FIREBASE_API_KEY"],
    "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
    "projectId": os.environ["FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["FIREBASE_APP_ID"],
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="RailPulse")

# Create tables on startup (fine for sqlite/dev; use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

# Seed/promote the admin account from ADMIN_EMAIL/ADMIN_PASSWORD, if set
with Session(engine) as _admin_seed_db:
    ensure_admin_seed(_admin_seed_db)

if os.environ.get("SEED_DEV_DATA") == "1":
    from dev_seed import run_dev_seed
    run_dev_seed()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ---- Content data (edit here instead of touching the HTML) ----

NAV_LINKS = [
    {"href": "#home", "label": "Home"},
    {"href": "#features", "label": "Features"},
    {"href": "#how-it-works", "label": "How It Works"},
    {"href": "#about", "label": "About"},
    {"href": "#contact", "label": "Contact"},
]

HERO_TEXTS = [
    "Smarter Railway Journeys Begin Here",
    "Real-Time Passenger Intelligence",
    "Automated Delays & Live Tracking",
]

FEATURES = [
    {
        "icon": "🚆",
        "title": "Live Journey Tracking",
        "desc": "Follow your train in real time and stay informed from departure to arrival with live operational updates.",
        "size": "large",
    },
    {
        "icon": "🔔",
        "title": "Instant Alerts",
        "desc": "Receive notifications whenever delays, cancellations, or platform changes affect your journey.",
        "size": "normal",
    },
    {
        "icon": "🌦",
        "title": "Weather Intelligence",
        "desc": "Understand how weather conditions could impact your trip before leaving home.",
        "size": "normal",
    },
    {
        "icon": "❤️",
        "title": "Save Your Favourite Journeys",
        "desc": "Quickly access your regular trips without searching every time. RailPulse keeps monitoring them automatically.",
        "size": "wide",
    },
    {
        "icon": "⚡",
        "title": "Fast Updates",
        "desc": "Information refreshes continuously, helping you react quickly when plans change.",
        "size": "normal",
    },
    {
        "icon": "🛡️",
        "title": "Personalized Experience",
        "desc": "Receive updates for only the journeys that matter to you, reducing unnecessary notifications.",
        "size": "normal",
    },
]

STEPS = [
    {"n": 1, "icon": "👤", "title": "Create Account", "desc": "Sign up in seconds and personalize your railway experience."},
    {"n": 2, "icon": "🚆", "title": "Save Your Journey", "desc": "Add the routes you travel regularly and keep them in one place."},
    {"n": 3, "icon": "🔔", "title": "Receive Alerts", "desc": "Get notified instantly about delays, cancellations, weather, and platform changes."},
    {"n": 4, "icon": "😊", "title": "Enjoy Your Trip", "desc": "Stay informed throughout your journey and travel with greater confidence."},
]

SAVED_JOURNEYS = [
    {"route": "London → Manchester", "freq": "Daily"},
    {"route": "Reading → Oxford", "freq": "Weekdays"},
    {"route": "Bristol → Cardiff", "freq": "Weekly"},
]

FAQS = [
    {
        "q": "Is RailPulse free to use?",
        "a": "Yes. You can create an account, save your journeys, and receive real-time travel updates at no cost.",
    },
    {
        "q": "Do I need an account?",
        "a": "An account allows you to save favourite journeys, receive personalised alerts, and manage your notification preferences.",
    },
    {
        "q": "What information will I receive?",
        "a": "RailPulse keeps you informed with journey status, delays, cancellations, platform updates, and relevant weather information for your saved routes.",
    },
    {
        "q": "Can I save more than one journey?",
        "a": "Yes. You can save multiple journeys and receive updates for each one based on your notification preferences.",
    },
    {
        "q": "Will I receive notifications automatically?",
        "a": "After enabling notifications, RailPulse can alert you about important changes affecting your saved journeys.",
    },
]

TODAY_JOURNEY = {
    "origin": "Euston",
    "origin_time": "09:30",
    "destination": "Manchester Piccadilly",
    "destination_time": "11:42",
    "status": "On Time",
    "progress": 72,
    "platform": 8,
    "weather_temp": "18°C",
    "weather_desc": "Light Rain",
}


@app.get("/", name="home")
async def home(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "nav_links": NAV_LINKS,
            "hero_texts": HERO_TEXTS,
            "features": FEATURES,
            "steps": STEPS,
            "saved_journeys": SAVED_JOURNEYS,
            "faqs": FAQS,
            "journey": TODAY_JOURNEY,
            "current_user": current_user,
        },
    )


# ---------------------------------------------------------------------------
# Auth: sign-up
# ---------------------------------------------------------------------------

@app.get("/auth/sign-up", name="sign_up_page")
async def sign_up_page(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/sign-up.html",
        {"error": None, "form_data": None, "firebase_config_json": FIREBASE_CONFIG_JSON},
    )


@app.post("/auth/sign-up", name="sign_up_submit")
async def sign_up_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    purpose: str = Form(None),
    agree_terms: str = Form(None),
    agree_gdpr: str = Form(None),
    db: Session = Depends(get_db),
):
    form_data = {"first_name": first_name, "last_name": last_name, "email": email}

    def render_error(message: str):
        return templates.TemplateResponse(
            request,
            "auth/sign-up.html",
            {"error": message, "form_data": form_data},
            status_code=400,
        )

    email_normalized = email.strip().lower()

    if not agree_terms or not agree_gdpr:
        return render_error("You must accept the Terms of Service and GDPR consent to continue.")

    if len(password) < 8:
        return render_error("Password must be at least 8 characters long.")

    existing = db.query(User).filter(User.email == email_normalized).first()
    if existing:
        return render_error("An account with that email already exists. Try signing in instead.")

    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email_normalized,
        hashed_password=hash_password(password),
        purpose=purpose,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return render_error("An account with that email already exists. Try signing in instead.")

    response = RedirectResponse(url=request.url_for("dashboard"), status_code=303)
    token = create_session_token(user.id)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return response


# ---------------------------------------------------------------------------
# Auth: sign-in
# ---------------------------------------------------------------------------

@app.get("/auth/sign-in", name="sign_in_page")
async def sign_in_page(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/sign-in.html",
        {"error": None, "form_data": None, "firebase_config_json": FIREBASE_CONFIG_JSON},
    )


@app.post("/auth/sign-in", name="sign_in_submit")
async def sign_in_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember: str = Form(None),
    db: Session = Depends(get_db),
):
    email_normalized = email.strip().lower()
    user = db.query(User).filter(User.email == email_normalized).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "auth/sign-in.html",
            {
                "error": "Incorrect email or password.",
                "form_data": {"email": email},
            },
            status_code=400,
        )

    response = RedirectResponse(url=request.url_for("dashboard"), status_code=303)
    token = create_session_token(user.id)
    max_age = SESSION_MAX_AGE if remember else None  # session cookie if "remember" not checked
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return response


@app.get("/auth/sign-out", name="sign_out")
async def sign_out(request: Request):
    response = RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


# ---------------------------------------------------------------------------
# Auth: Google (Firebase)
# ---------------------------------------------------------------------------

@app.post("/auth/google/verify", name="google_verify")
async def google_verify(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    id_token = body.get("idToken")
    if not id_token:
        return JSONResponse({"error": "Missing idToken"}, status_code=400)

    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        return JSONResponse({"error": "Invalid token"}, status_code=401)

    email = decoded.get("email")
    if not email:
        return JSONResponse({"error": "No email on Google account"}, status_code=400)

    email_normalized = email.strip().lower()
    user = db.query(User).filter(User.email == email_normalized).first()

    if not user:
        name_parts = (decoded.get("name") or "").split(" ", 1)
        first_name = name_parts[0].strip() if name_parts and name_parts[0] else "Google"
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ""
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email_normalized,
            # Google-authenticated accounts have no password of their own;
            # store an unusable random hash so hashed_password stays NOT NULL
            # and this value can never match a real password attempt.
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            purpose=None,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email_normalized).first()

    session_token = create_session_token(user.id)
    response = JSONResponse({"redirect": str(request.url_for("dashboard"))})
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return response


# ---------------------------------------------------------------------------
# Protected dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard", name="dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    prefs = db.query(UserPreference).filter(
    UserPreference.email == current_user.email
).all()
    notifications = db.query(Notification).filter(
    Notification.user_id == current_user.id
).order_by(Notification.id.desc()).all()
    primary = prefs[0] if prefs else None

    return templates.TemplateResponse(
        request,
        "dashboard/dashboard.html",
        {
            "current_user": current_user,
            "tracked_route": primary.route if primary else None,
            "tracked_station": primary.station if primary else None,
            "delay_threshold_minute": primary.delay_threshold_minute if primary else None,
            # No live rail feed yet, so we don't fake a running status or an
            # on-time %. We surface only what Supabase actually knows.
            "board_status": "monitoring",
            "minutes_late": None,
            "tracked_routes_count": len(prefs),
            "active_alerts_count": len(notifications),
            "on_time_pct": None,
            "notifications": notifications[:5],
        },
    )


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

@app.post("/api/push/register", name="push_register")
async def push_register(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "not authenticated"})

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "invalid JSON body"})

    token = (payload.get("token") or "").strip()
    if not token:
        return JSONResponse(status_code=400, content={"error": "missing token"})

    existing = db.query(PushSubscription).filter(PushSubscription.fcm_token == token).first()
    if existing:
        existing.user_id = current_user.id
    else:
        db.add(PushSubscription(user_id=current_user.id, fcm_token=token))
    db.commit()

    return JSONResponse(status_code=200, content={"status": "registered"})


@app.post("/api/push/unregister", name="push_unregister")
async def push_unregister(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "not authenticated"})

    db.query(PushSubscription).filter(PushSubscription.user_id == current_user.id).delete()
    db.commit()

    return JSONResponse(status_code=200, content={"status": "unregistered"})


def send_push_to_user(db: Session, user: User, title: str, body: str, url: str = "/notifications"):
    """Best-effort FCM push to every device the user has registered.
    Never raises -- a push failure should not block notification logging."""
    subs = db.query(PushSubscription).filter(PushSubscription.user_id == user.id).all()
    print(f"[push] found {len(subs)} subscription(s) for user {user.id} ({user.email})")
    for sub in subs:
        try:
            message = messaging.Message(
                data={"title": title, "body": body, "url": url},
                token=sub.fcm_token,
            )
            result = messaging.send(message)
            print(f"[push] sent OK, message id: {result}")
        except messaging.UnregisteredError:
            print(f"[push] token unregistered, deleting: {sub.fcm_token[:20]}...")
            db.delete(sub)
            db.commit()
        except Exception as exc:
            print(f"[push] send failed for user {user.id}: {type(exc).__name__}: {exc}")


@app.post("/webhooks/notifications", name="webhook_notifications")
async def webhook_notifications(request: Request, db: Session = Depends(get_db)):
    provided_secret = request.headers.get("X-Webhook-Secret", "")
    expected_secret = os.environ.get("WEBHOOK_SECRET", "")

    if not expected_secret or not secrets.compare_digest(provided_secret, expected_secret):
        return JSONResponse(status_code=401, content={"error": "invalid or missing webhook secret"})

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "invalid JSON body"})

    required_fields = ["email", "route", "station", "message"]
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        return JSONResponse(status_code=400, content={"error": f"missing fields: {missing}"})

    email_normalized = payload["email"].strip().lower()
    user = db.query(User).filter(User.email == email_normalized).first()
    if not user:
        return JSONResponse(status_code=404, content={"error": f"no user found for email {email_normalized}"})

    notification = Notification(
        user_id=user.id,
        email=email_normalized,
        route=payload["route"],
        station=payload["station"],
        message=payload["message"],
        delivery_status=payload.get("delivery_status", "delivered"),
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    send_push_to_user(
        db,
        user,
        title=f"RailPulse: {payload['route']}",
        body=payload["message"],
    )

    return JSONResponse(status_code=201, content={"id": notification.id, "status": "created"})


@app.get("/api/stations")
async def get_stations(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT stanox_no, full_name, crs_code, route_description
            FROM station_codes
            WHERE crs_code IS NOT NULL
            ORDER BY route_description, full_name
        """)
    )
    grouped = defaultdict(list)
    for row in result:
        route = row.route_description or "Other"
        grouped[route].append({
            "stanox_no": row.stanox_no,
            "full_name": row.full_name,
            "crs_code": row.crs_code,
        })
    return grouped

@app.get("/api/stations/search")
async def search_stations(q: str = "", route: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    route = route.strip()
    if len(q) < 2:
        return []
    query = """
        SELECT stanox_no, full_name, crs_code, route_description
        FROM station_codes
        WHERE crs_code IS NOT NULL
          AND (LOWER(full_name) LIKE LOWER(:pattern) OR LOWER(crs_code) LIKE LOWER(:pattern))
    """
    params = {"pattern": f"%{q}%"}
    if route:
        query += " AND route_description = :route"
        params["route"] = route
    query += " ORDER BY full_name LIMIT 20"

    result = db.execute(text(query), params)
    return [
        {
            "stanox_no": row.stanox_no,
            "full_name": row.full_name,
            "crs_code": row.crs_code,
            "route_description": row.route_description or "Other",
        }
        for row in result
    ]


@app.get("/stations", name="stations_browse")
async def stations_browse(request: Request, page: int = 1, q: str = "", route: str = "", db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    per_page = 50
    page = max(page, 1)
    offset = (page - 1) * per_page

    base_query = "FROM station_codes WHERE crs_code IS NOT NULL"
    params = {}
    if q.strip():
        base_query += " AND (LOWER(full_name) LIKE LOWER(:pattern) OR LOWER(crs_code) LIKE LOWER(:pattern))"
        params["pattern"] = f"%{q.strip()}%"
    if route.strip():
        base_query += " AND route_description = :route"
        params["route"] = route.strip()

    total = db.execute(text(f"SELECT COUNT(*) {base_query}"), params).scalar()

    params["limit"] = per_page
    params["offset"] = offset
    rows = db.execute(
        text(f"""
            SELECT stanox_no, full_name, crs_code, route_description
            {base_query}
            ORDER BY full_name
            LIMIT :limit OFFSET :offset
        """),
        params
    ).fetchall()

    total_pages = max((total + per_page - 1) // per_page, 1)

    all_routes = db.execute(
        text("SELECT DISTINCT route_description FROM station_codes WHERE route_description IS NOT NULL ORDER BY route_description")
    ).scalars().all()

    return templates.TemplateResponse(
        request,
        "stations.html",
        {
            "current_user": current_user,
            "stations": rows,
            "page": page,
            "total_pages": total_pages,
            "q": q,
            "route": route,
            "all_routes": all_routes,
        },
    )

@app.get("/preferences", name="preferences")
async def preferences_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    all_routes = db.execute(
        text("SELECT DISTINCT route_description FROM station_codes WHERE route_description IS NOT NULL ORDER BY route_description")
    ).scalars().all()

    return templates.TemplateResponse(
        request,
        "preferences.html",
        {
            "current_user": current_user,
             "tracked_routes": db.query(UserPreference).filter(
                UserPreference.email == current_user.email
            ).all(),
            "all_routes": all_routes,
        },
    )


@app.post("/preferences", name="preferences_submit")
async def preferences_submit(
    request: Request,
    route: str = Form(...),
    station: str = Form(...),
    delay_threshold_minute: int = Form(...),
    notify_delay: str = Form(None),
    notify_cancellation: str = Form(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    db.add(UserPreference(
        user_id=current_user.id,
        email=current_user.email,
        route=route.strip(),
        station=station.strip(),
        delay_threshold_minute=delay_threshold_minute,
        notify_delay=bool(notify_delay),
        notify_cancellation=bool(notify_cancellation),
    ))
    db.commit()
    return RedirectResponse(url=request.url_for("preferences"), status_code=303)

@app.post("/preferences/{pref_id}/delete", name="preferences_delete")
async def preferences_delete(pref_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    db.query(UserPreference).filter(
        UserPreference.id == pref_id,
        UserPreference.email == current_user.email
    ).delete()
    db.commit()
    return RedirectResponse(url=request.url_for("preferences"), status_code=303)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@app.get("/notifications", name="notifications")
async def notifications_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    return templates.TemplateResponse(
        request,
        "notifications.html",
        {
            "current_user": current_user,
             "notifications": db.query(Notification).filter(
                Notification.user_id == current_user.id
            ).order_by(Notification.id.desc()).all(),
        },
    )


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------

@app.get("/account", name="account")
async def account_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    push_registered = db.query(PushSubscription).filter(
        PushSubscription.user_id == current_user.id
    ).first() is not None

    return templates.TemplateResponse(
        request,
        "account.html",
        {
            "current_user": current_user,
             "tracked_routes_count": db.query(UserPreference).filter(
                UserPreference.email == current_user.email
            ).count(),
            "firebase_config_json": FIREBASE_CONFIG_JSON,
            "firebase_vapid_key": FIREBASE_VAPID_KEY,
            "push_registered": push_registered,
        },
    )


@app.post("/account", name="account_submit")
async def account_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url=request.url_for("sign_in_page"), status_code=303)

    current_user.first_name = first_name.strip()
    current_user.last_name = last_name.strip()
    new_email = email.strip().lower()

    if new_email != current_user.email:
        existing = db.query(User).filter(User.email == new_email).first()
        if existing:
            db.rollback()
            return templates.TemplateResponse(
                request,
                "account.html",
                {
                    "current_user": current_user,
                    "tracked_routes_count": db.query(UserPreference).filter(
                        UserPreference.email == current_user.email
                    ).count(),
                    "error": "That email is already in use by another account.",
                },
                status_code=400,
            )
        current_user.email = new_email

    db.commit()

    return RedirectResponse(url=request.url_for("account"), status_code=303)


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.get("/admin/login", name="admin_login_page")
async def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/login.html",
        {"error": None},
    )

@app.post("/admin/login", name="admin_login_submit")
async def admin_login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email_normalized = email.strip().lower()
    user = verify_admin_credentials(db, email_normalized, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Incorrect email or password, or this account has no admin access."},
            status_code=400,
        )

    response = RedirectResponse(url=request.url_for("admin_dashboard"), status_code=303)
    token = create_admin_session_token(user)
    response.set_cookie(
        ADMIN_SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return response

@app.get("/admin/dashboard", name="admin_dashboard")
async def admin_dashboard(request: Request, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "current_admin": current_admin,
            "active_page": "dashboard",
            "total_users": total_users(db),
        },
    )

@app.get("/admin/logout", name="admin_logout")
async def admin_logout(request: Request):
    response = RedirectResponse(url=request.url_for("admin_login_page"), status_code=303)
    response.delete_cookie(ADMIN_SESSION_COOKIE)
    return response

@app.get("/admin/users", name="admin_users")
async def admin_users(request: Request, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.email).all()
    return templates.TemplateResponse("admin/users.html", {"request": request, "current_admin": current_admin, "active_page": "users", "users": users})

@app.post("/admin/users/{user_id}/grant-admin", name="admin_grant")
async def admin_grant(user_id: str, password: str = Form(...), current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(404)
    target.is_admin = True
    target.admin_password_hash = bcrypt.hash(password)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@app.post("/admin/users/{user_id}/revoke-admin", name="admin_revoke")
async def admin_revoke(user_id: str, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(400, "Can't revoke your own admin access.")
    target = db.query(User).filter(User.id == user_id).first()
    target.is_admin = False
    target.admin_password_hash = None
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

from admin_analytics import top_routes, top_stations, total_users

@app.get("/admin/api/analytics/top-routes")
async def api_top_routes(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"data": top_routes(db)}

@app.get("/admin/api/analytics/top-stations")
async def api_top_stations(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"data": top_stations(db)}

# Local dev: uvicorn main:app --reload
