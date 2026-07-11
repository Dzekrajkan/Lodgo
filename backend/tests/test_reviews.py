from backend import models
from backend.tests.conftest import make_booking

def review_payload(hotel, booking_id=None, rating=5, comment="Great stay"):
    return {
        "hotel_id": hotel.id,
        "booking_id": booking_id,
        "rating": rating,
        "comment": comment,
    }

def test_create_review_success(authorized_client, test_db, test_user, test_room, test_hotel):
    make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.completed)
    res = authorized_client.post("/api/review", json=review_payload(test_hotel))

    assert res.status_code == 201
    data = res.json()
    assert data["rating"] == 5
    assert data["hotel_id"] == test_hotel.id

def test_create_review_unauthenticated(client, test_hotel):
    res = client.post("/api/review", json=review_payload(test_hotel))

    assert res.status_code == 401

def test_create_review_no_completed_booking(authorized_client, test_db, test_user, test_room, test_hotel):
    make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.pending)
    res = authorized_client.post("/api/review", json=review_payload(test_hotel))

    assert res.status_code == 400
    assert res.json()["detail"] == "There are no completed bookings to review."

def test_create_review_duplicate(authorized_client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.completed)

    first = authorized_client.post("/api/review", json=review_payload(test_hotel, booking_id=booking.id))
    assert first.status_code == 201

    second = authorized_client.post("/api/review", json=review_payload(test_hotel, booking_id=booking.id))
    assert second.status_code == 400
    assert second.json()["detail"] == "A review for this reservation already exists."

def test_get_reviews(client, test_db, test_user, test_room, test_hotel):
    booking = make_booking(test_db, test_user, test_room, test_hotel, status=models.BookingStatus.completed)
    review = models.Review(
        user_id=test_user.id,
        hotel_id=test_hotel.id,
        booking_id=booking.id,
        rating=4,
        comment="Nice",
    )
    test_db.add(review)
    test_db.commit()
    res = client.get(f"/api/reviews/{test_hotel.id}")

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["rating"] == 4

def test_get_reviews_hotel_not_found(client):
    res = client.get("/api/reviews/99999")

    assert res.status_code == 400
    assert res.json()["detail"] == "Such a hotel does not exist."