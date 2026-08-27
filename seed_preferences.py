import uuid

from database import SessionLocal
from models import UserPreference

PREFERENCES = [
    {
        "user_id": "0ab98e57-a514-4d9f-9d0f-43017846e3e2",
        "email": "michael.brown@gmail.com",
        "route": "East Coast Main Line",
        "station": "Stevenage",
        "delay_threshold_minute": 15,
    },
    {
        "user_id": "2b1c3be1-d391-499b-b216-c03ea1704ce5",
        "email": "sophia.martin@gmail.com",
        "route": "Great Northern",
        "station": "Hitchin",
        "delay_threshold_minute": 30,
    },
    {
        "user_id": "4cd51a83-2e07-43d4-89c1-dabbfdca7f9d",
        "email": "daniel.jackson@gmail.com",
        "route": "Great Northern",
        "station": "Peterborough",
        "delay_threshold_minute": 20,
    },
    {
        "user_id": "508bc2a3-ec2e-4321-87fd-6a58afbe1e31",
        "email": "ethan.hall@gmail.com",
        "route": "Thameslink",
        "station": "Farringdon",
        "delay_threshold_minute": 30,
    },
    {
        "user_id": "55727e47-a3e3-4e42-9974-4574ff3b0532",
        "email": "noah.lewis@gmail.com",
        "route": "Thameslink",
        "station": "Luton",
        "delay_threshold_minute": 15,
    },
    {
        "user_id": "5d7bdaef-1b02-4b5f-9a1d-8d8ca1ab0cb9",
        "email": "grace.williams@gmail.com",
        "route": "East Coast Main Line",
        "station": "King's Cross",
        "delay_threshold_minute": 20,
    },
    {
        "user_id": "695a005c-50bf-45cc-b445-fd4ef97b4298",
        "email": "liam.harris@gmail.com",
        "route": "Thameslink",
        "station": "London Bridge",
        "delay_threshold_minute": 5,
    },
    {
        "user_id": "7063b469-bcf3-462c-984d-a41f06f5cbd6",
        "email": "sarah.jones@gmail.com",
        "route": "East Coast Main Line",
        "station": "Hitchin",
        "delay_threshold_minute": 10,
    },
    {
        "user_id": "73dffcc0-d5d7-4887-9ab6-06359c21b536",
        "email": "ava.walker@gmail.com",
        "route": "Thameslink",
        "station": "Bedford",
        "delay_threshold_minute": 20,
    },
    {
        "user_id": "77feae3b-22f3-40e0-a924-808ac1750e5b",
        "email": "john.smith@gmail.com",
        "route": "East Coast Main Line",
        "station": "Peterborough",
        "delay_threshold_minute": 5,
    },
    {
        "user_id": "89d1bf15-ae67-4c3f-b70b-a37d3bd8175d",
        "email": "amelia.clark@gmail.com",
        "route": "Thameslink",
        "station": "St Albans",
        "delay_threshold_minute": 10,
    },
    {
        "user_id": "a6c26479-8cbd-43c7-85a3-97580cd647c1",
        "email": "emma.taylor@gmail.com",
        "route": "Great Northern",
        "station": "King's Cross",
        "delay_threshold_minute": 5,
    },
    {
        "user_id": "bfa40c2b-865c-48a6-8946-1bab71a60f2f",
        "email": "david.wilson@gmail.com",
        "route": "East Coast Main Line",
        "station": "Doncaster",
        "delay_threshold_minute": 30,
    },
    {
        "user_id": "d19bc509-7200-4272-9274-640c3bb7a029",
        "email": "olivia.moore@gmail.com",
        "route": "Great Northern",
        "station": "Hatfield",
        "delay_threshold_minute": 15,
    },
    {
        "user_id": "fa57c577-4d03-4a83-ae78-9cff2588b1ec",
        "email": "james.thomas@gmail.com",
        "route": "Great Northern",
        "station": "Welwyn Garden City",
        "delay_threshold_minute": 10,
    },
    {
        "user_id": "11111111-1111-1111-1111-111111111111",
        "email": "berachaiah.abolaji@gmail.com",
        "route": "Great Northern",
        "station": "Finsbury Park",
        "delay_threshold_minute": 10,
    },
]

db = SessionLocal()

created = 0

for row in PREFERENCES:
    exists = db.query(UserPreference).filter(
        UserPreference.user_id == uuid.UUID(row["user_id"]),
        UserPreference.route == row["route"],
        UserPreference.station == row["station"],
    ).first()

    if exists:
        continue

    db.add(
        UserPreference(
            user_id=uuid.UUID(row["user_id"]),
            email=row["email"],
            route=row["route"],
            station=row["station"],
            delay_threshold_minute=row["delay_threshold_minute"],
        )
    )
    created += 1

db.commit()
db.close()

print(f"Created {created} preferences.")
