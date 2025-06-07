"""Reset test user password."""

from sqlalchemy import create_engine, text
from src.mental_health_coach.auth.security import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///mental_health_coach.db")
engine = create_engine(DATABASE_URL)

# Reset password
hashed_password = get_password_hash("testpassword123")

with engine.connect() as conn:
    conn.execute(text("""
        UPDATE users 
        SET hashed_password = :password, is_verified = 1 
        WHERE email = 'test@example.com'
    """), {"password": hashed_password})
    conn.commit()
    print("Test user password reset to: testpassword123") 