from auth import hash_password
from database import Base, SessionLocal, engine
from models import User

Base.metadata.create_all(bind=engine)

USERS = [
    {
        "user_id": "0ab98e57-a514-4d9f-9d0f-43017846e3e2",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "2b1c3be1-d391-499b-b216-c03ea1704ce5",
        "first_name": "Sophia",
        "last_name": "Martin",
        "email": "sophia.martin@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "4cd51a83-2e07-43d4-89c1-dabbfdca7f9d",
        "first_name": "Daniel",
        "last_name": "Jackson",
        "email": "daniel.jackson@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "508bc2a3-ec2e-4321-87fd-6a58afbe1e31",
        "first_name": "Ethan",
        "last_name": "Hall",
        "email": "ethan.hall@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "55727e47-a3e3-4e42-9974-4574ff3b0532",
        "first_name": "Noah",
        "last_name": "Lewis",
        "email": "noah.lewis@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "5d7bdaef-1b02-4b5f-9a1d-8d8ca1ab0cb9",
        "first_name": "Grace",
        "last_name": "Williams",
        "email": "grace.williams@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "695a005c-50bf-45cc-b445-fd4ef97b4298",
        "first_name": "Liam",
        "last_name": "Harris",
        "email": "liam.harris@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "7063b469-bcf3-462c-984d-a41f06f5cbd6",
        "first_name": "Sarah",
        "last_name": "Jones",
        "email": "sarah.jones@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "73dffcc0-d5d7-4887-9ab6-06359c21b536",
        "first_name": "Ava",
        "last_name": "Walker",
        "email": "ava.walker@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "77feae3b-22f3-40e0-a924-808ac1750e5b",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "89d1bf15-ae67-4c3f-b70b-a37d3bd8175d",
        "first_name": "Amelia",
        "last_name": "Clark",
        "email": "amelia.clark@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "a6c26479-8cbd-43c7-85a3-97580cd647c1",
        "first_name": "Emma",
        "last_name": "Taylor",
        "email": "emma.taylor@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "bfa40c2b-865c-48a6-8946-1bab71a60f2f",
        "first_name": "David",
        "last_name": "Wilson",
        "email": "david.wilson@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "d19bc509-7200-4272-9274-640c3bb7a029",
        "first_name": "Olivia",
        "last_name": "Moore",
        "email": "olivia.moore@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "fa57c577-4d03-4a83-ae78-9cff2588b1ec",
        "first_name": "James",
        "last_name": "Thomas",
        "email": "james.thomas@gmail.com",
        "password": "RailPulseDev123!",
    },
    {
        "user_id": "11111111-1111-1111-1111-111111111111",
        "first_name": "Berachaiah",
        "last_name": "Abolaji",
        "email": "berachaiah.abolaji@gmail.com",
        "password": "beras123",
    },
]

db = SessionLocal()

created = 0

for row in USERS:
    if db.query(User).filter(User.email == row["email"]).first():
        continue

    db.add(
        User(
            id=row["user_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            hashed_password=hash_password(row["password"]),
            purpose="Testing RailPulse",
            is_active=True,
        )
    )
    created += 1

db.commit()
db.close()

print(f"Created {created} users.")
