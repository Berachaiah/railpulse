from datetime import datetime

from database import SessionLocal
from models import Notification

db = SessionLocal()

# Clear existing notifications
db.query(Notification).delete()

users = {
    "11111111-1111-1111-1111-111111111111": {
        "email": "berachaiah.abolaji@gmail.com",
        "route": "Great Northern",
        "station": "Finsbury Park",
    },
    "0ab98e57-a514-4d9f-9d0f-43017846e3e2": {
        "email": "michael.brown@gmail.com",
        "route": "East Coast Main Line",
        "station": "Stevenage",
    },
    "77feae3b-22f3-40e0-a924-808ac1750e5b": {
        "email": "john.smith@gmail.com",
        "route": "East Coast Main Line",
        "station": "Peterborough",
    },
    "89d1bf15-ae67-4c3f-b70b-a37d3bd8175d": {
        "email": "amelia.clark@gmail.com",
        "route": "Thameslink",
        "station": "St Albans",
    },
}

# 10 notifications for Berachaiah
for i in range(1, 11):
    db.add(
        Notification(
            user_id="11111111-1111-1111-1111-111111111111",
            email=users["11111111-1111-1111-1111-111111111111"]["email"],
            route="Great Northern",
            station="Finsbury Park",
            message=f"Delay Alert #{i}: Train delayed by {5+i} minutes.",
            delivery_status="Sent",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

# One notification for everyone else
for uid in [
    "0ab98e57-a514-4d9f-9d0f-43017846e3e2",
    "77feae3b-22f3-40e0-a924-808ac1750e5b",
    "89d1bf15-ae67-4c3f-b70b-a37d3bd8175d",
]:
    u = users[uid]
    db.add(
        Notification(
            user_id=uid,
            email=u["email"],
            route=u["route"],
            station=u["station"],
            message="Minor service delay reported.",
            delivery_status="Sent",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

db.commit()
db.close()

print("Notifications seeded successfully.")
