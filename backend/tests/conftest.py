from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base, get_db
from backend.auth.service import hash_password, create_access_token, create_refresh_token
from backend.main import app
from backend import models
from datetime import datetime
from fastapi.testclient import TestClient
import pytest

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    user = models.User(
        username="test",
        email="test@gmail.com",
        password_hash=hash_password("test1234"),
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    yield user

@pytest.fixture
def authorized_client(client, test_user):
    access_token = create_access_token({"sub": str(test_user.id)})
    refresh_token = create_refresh_token({"sub": str(test_user.id)})
    client.cookies.set("access_token", access_token)
    client.cookies.set("refresh_token", refresh_token)
    yield client

@pytest.fixture(autouse=True)
def mock_send_email():
    with patch("backend.auth.email_utils.send_verification_email", new_callable=AsyncMock):
        yield

@pytest.fixture
def test_hotel(test_db, test_user):
    hotel = models.Hotel(
        owner_id=test_user.id,
        name="pop",
        description="pop pop",
        address="fewefew",
        city="FEFEF",
        country="BFDFBFD",
        latitude="121",
        longitude="322",
        price_per_night=32,
        check_in_time="12:00",
        check_out_time="13:00",
    )

    test_db.add(hotel)
    test_db.commit()
    test_db.refresh(hotel)

    yield hotel

@pytest.fixture
def test_room(test_db, test_hotel):
    room = models.Room(
        hotel_id=test_hotel.id,
        name="ffewfew",
        description="wfwefew",
        price_per_night=21,
        capacity=1,
        quantity=2,
    )

    test_db.add(room)
    test_db.commit()
    test_db.refresh(room)

    yield room

def make_booking(db, user, room, hotel, status=models.BookingStatus.pending, date_from=None, date_to=None, total_price=100):
    booking = models.Booking(
        user_id=user.id,
        room_id=room.id,
        hotel_id=hotel.id,
        guest_first_name="John",
        guest_last_name="Doe",
        guest_email="john@test.com",
        date_from=date_from or datetime(2024, 1, 1),
        date_to=date_to or datetime(2024, 1, 5),
        total_price=total_price,
        status=status,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking