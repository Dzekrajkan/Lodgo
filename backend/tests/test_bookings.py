import pytest
from datetime import datetime
from backend import models
from backend.auth.service import hash_password
from backend.tests.conftest import make_booking

@pytest.fixture
def other_user(test_db):
    user = models.User(
        username="other",
        email="other@gmail.com",
        password_hash=hash_password("test1234"),
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    yield user

def valid_booking_payload(room, hotel, date_from="2024-03-01", date_to="2024-03-05"):
    return {
        "room_id": room.id,
        "hotel_id": hotel.id,
        "date_from": date_from,
        "date_to": date_to,
        "guest_first_name": "John",
        "guest_last_name": "Doe",
        "guest_email": "john@test.com",
        "service_ids": [],
    }

def valid_pay_payload(booking_id, username="test"):
    return {
        "id": booking_id,
        "username": username,
        "card_number": "4111111111111111",
        "card_expiration_date": "12/30",
        "CVC": "123",
    }

def test_create_booking_success(authorized_client, test_room, test_hotel):
    payload = valid_booking_payload(test_room, test_hotel)
    res = authorized_client.post("/api/bookings", json=payload)

    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "pending"
    assert data["total_price"] == 4 * test_room.price_per_night

def test_create_booking_unauthenticated(client, test_room, test_hotel):
    payload = valid_booking_payload(test_room, test_hotel)
    res = client.post("/api/bookings", json=payload)

    assert res.status_code == 401

def test_create_booking_invalid_dates(authorized_client, test_room, test_hotel):
    payload = valid_booking_payload(test_room, test_hotel, date_from="2024-03-05", date_to="2024-03-05")
    res = authorized_client.post("/api/bookings", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "Please enter the correct date"

def test_create_booking_room_not_found(authorized_client, test_hotel, test_room):
    payload = valid_booking_payload(test_room, test_hotel)
    payload["room_id"] = 2
    res = authorized_client.post("/api/bookings", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "This room doesn't exist"

def test_create_booking_no_availability(authorized_client, test_db, test_user, test_room, test_hotel):
    for _ in range(test_room.quantity):
        make_booking(
            test_db,
            test_user,
            test_room,
            test_hotel,
            status=models.BookingStatus.pending,
            date_from=datetime(2024, 4, 1),
            date_to=datetime(2024, 4, 10),
        )
    payload = valid_booking_payload(test_room, test_hotel, date_from="2024-04-05", date_to="2024-04-07")
    res = authorized_client.post("/api/bookings", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "There are no available seats for the selected dates."

def test_get_bookings_all(authorized_client, test_db, test_user, test_room, test_hotel):
    make_booking(test_db, test_user, test_room, test_hotel)
    make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.confirmed)
    res = authorized_client.get("/api/bookings", params={"status": "all"})

    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2

def test_get_bookings_last(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.confirmed)
    res = authorized_client.get("/api/bookings", params={"status": "last"})

    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert data["status"] == "confirmed"

def test_get_bookings_invalid_status(authorized_client):
    res = authorized_client.get("/api/bookings", params={"status": "not-a-real-status"})

    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid status. Use 'all' or 'last'."

def test_cancel_booking_success(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.pending)
    res = authorized_client.post(f"/api/bookings/{booking.id}/cancel")

    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"

def test_cancel_booking_not_owner(authorized_client, test_db, other_user, test_room, test_hotel):
    booking = make_booking(test_db, other_user, test_room, test_hotel, status=models.BookingStatus.pending)
    res = authorized_client.post(f"/api/bookings/{booking.id}/cancel")

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation does not belong to you"

def test_cancel_booking_already_cancelled(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.cancelled)
    res = authorized_client.post(f"/api/bookings/{booking.id}/cancel")

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation has already been cancelled."

def test_cancel_booking_completed(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.completed)
    res = authorized_client.post(f"/api/bookings/{booking.id}/cancel")

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation is already completed"

def test_pay_booking_success(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.pending)
    res = authorized_client.post("/api/bookings/pay", json=valid_pay_payload(booking.id))

    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"

def test_pay_booking_already_paid(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.confirmed)
    res = authorized_client.post("/api/bookings/pay", json=valid_pay_payload(booking.id))

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation has already been paid for."

def test_pay_booking_cancelled(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.cancelled)
    res = authorized_client.post("/api/bookings/pay", json=valid_pay_payload(booking.id))

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation has already been cancelled"

def test_pay_booking_invalid_card(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.pending)
    payload = valid_pay_payload(booking.id)
    payload["card_number"] = "123"
    payload["CVC"] = "1"
    res = authorized_client.post("/api/bookings/pay", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "Please enter correct card details"

def test_pay_booking_not_owner(authorized_client, test_db, other_user, test_room, test_hotel):
    booking = make_booking(test_db, other_user, test_room, test_hotel, status=models.BookingStatus.pending)
    res = authorized_client.post("/api/bookings/pay", json=valid_pay_payload(booking.id))

    assert res.status_code == 400
    assert res.json()["detail"] == "The reservation does not belong to you"