from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import FitnessClass, User
from app.utils.timezone import IST

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == "demo@example.com"))
    if not user:
        user = User(name="Demo User", email="demo@example.com", password_hash=hash_password("DemoPassword123"))
        db.add(user)

    now = datetime.now(IST)
    samples = [
        ("Yoga", "Morning yoga session", "Priya", now + timedelta(days=2, hours=7), now + timedelta(days=2, hours=8), 20),
        ("Zumba", "High-energy dance workout", "Anita", now + timedelta(days=3, hours=18), now + timedelta(days=3, hours=19), 15),
        ("HIIT", "High-intensity interval training", "Rahul", now + timedelta(days=4, hours=7), now + timedelta(days=4, hours=8), 10),
    ]
    for name, description, instructor, start, end, capacity in samples:
        exists = db.scalar(select(FitnessClass).where(FitnessClass.name == name, FitnessClass.start_time == start))
        if not exists:
            db.add(FitnessClass(name=name, description=description, instructor=instructor, start_time=start, end_time=end, capacity=capacity, available_slots=capacity))
    db.commit()
print("Seed completed. Demo login: demo@example.com / DemoPassword123")
