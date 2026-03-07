from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
from backend.auth import auth
from datetime import timedelta, datetime

def seed_data():
    db: Session = SessionLocal()
    user = db.query(models.User).first()

    if not user:
        user = models.User(
            username="test",
            email="test@gmail.com",
            password_hash=auth.hash_password("test1234"),
            is_verified=True,
            is_admin=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    facilities = db.query(models.Facility).all()

    second_user = db.query(models.User).filter_by(email="alex@example.com").first()

    if not second_user:
        second_user = models.User(
            username="alex",
            email="alex@example.com",
            password_hash=auth.hash_password("alex1234"),
            is_verified=True,
            is_admin=False
        )

        db.add(second_user)
        db.commit()
        db.refresh(second_user)

    if not facilities:
        wifi = models.Facility(name="Free WiFi")
        pool = models.Facility(name="Swimming Pool")
        gym = models.Facility(name="Fitness Center")
        parking = models.Facility(name="Free Parking")
        restaurant = models.Facility(name="Restaurant")

        db.add_all([wifi, pool, gym, parking, restaurant])
        db.commit()
    else:
        wifi, pool, gym, parking, restaurant = facilities

    hotels = db.query(models.Hotel).all()

    if not hotels:
        hotel_1 = models.Hotel(
            owner_id=user.id,
            name="Ocean View Resort",
            description="Beautiful seaside resort with panoramic ocean views.",
            address="12 Beach Avenue",
            city="Barcelona",
            country="Spain",
            latitude="41.3851",
            longitude="2.1734",
            price_per_night=180,
            facilities=[wifi, pool, restaurant]
        )
        hotel_2 = models.Hotel(
            owner_id=user.id,
            name="Mountain Escape Lodge",
            description="Cozy mountain lodge perfect for relaxing vacations.",
            address="45 Alpine Road",
            city="Innsbruck",
            country="Austria",
            latitude="47.2692",
            longitude="11.4041",
            price_per_night=140,
            facilities=[wifi, gym, parking]
        )

        db.add_all([hotel_1, hotel_2])
        db.commit()
        db.refresh(hotel_1)
        db.refresh(hotel_2)
        print("Hotels created")
    else:
        hotel_1 = hotels[0]
        hotel_2 = hotels[1]

    if not db.query(models.Room).first():
        rooms = [
            models.Room(
                hotel_id=hotel_1.id,
                name="Standard Double Room",
                description="Comfortable room with a double bed and city view.",
                price_per_night=120,
                capacity=2,
                quantity=5
            ),
            models.Room(
                hotel_id=hotel_1.id,
                name="Deluxe Sea View Room",
                description="Spacious room with balcony and sea view.",
                price_per_night=210,
                capacity=3,
                quantity=3
            ),
            models.Room(
                hotel_id=hotel_2.id,
                name="Family Mountain Suite",
                description="Large suite perfect for families with mountain views.",
                price_per_night=190,
                capacity=4,
                quantity=2
            )
        ]

        db.add_all(rooms)
        db.commit()
        print("Rooms created")

    if not db.query(models.Service).first():
        services = [
            models.Service(
                hotel_id=hotel_1.id,
                name="Airport Transfer",
                price=40
            ),
            models.Service(
                hotel_id=hotel_1.id,
                name="Breakfast Buffet",
                price=15
            ),
            models.Service(
                hotel_id=hotel_2.id,
                name="Spa Access",
                price=30
            ),
            models.Service(
                hotel_id=hotel_2.id,
                name="Mountain Guide Tour",
                price=50
            ),
            models.Service(
                hotel_id=hotel_2.id,
                name="Ski Equipment Rental",
                price=35
            ),
        ]

        db.add_all(services)
        db.commit()
        print("Services created")

    if not db.query(models.Booking).first():
        room_1 = db.query(models.Room).filter_by(hotel_id=hotel_1.id).first()
        room_2 = db.query(models.Room).filter_by(hotel_id=hotel_2.id).first()
        booking_1 = models.Booking(
            user_id=second_user.id,
            hotel_id=hotel_1.id,
            room_id=room_1.id,
            guest_first_name="Alex",
            guest_last_name="Johnson",
            guest_email="alex@example.com",
            date_from=datetime.now() - timedelta(days=10),
            date_to=datetime.now() - timedelta(days=7),
            total_price=360,
            status="completed"
        )
        booking_2 = models.Booking(
            user_id=second_user.id,
            hotel_id=hotel_1.id,
            room_id=room_1.id,
            guest_first_name="Alex",
            guest_last_name="Johnson",
            guest_email="alex@example.com",
            date_from=datetime.now() - timedelta(days=20),
            date_to=datetime.now() - timedelta(days=18),
            total_price=240,
            status="completed"
        )
        booking_3 = models.Booking(
            user_id=second_user.id,
            hotel_id=hotel_2.id,
            room_id=room_2.id,
            guest_first_name="Alex",
            guest_last_name="Johnson",
            guest_email="alex@example.com",
            date_from=datetime.now() - timedelta(days=15),
            date_to=datetime.now() - timedelta(days=12),
            total_price=420,
            status="completed"
        )

        db.add_all([booking_1, booking_2, booking_3])
        db.commit()
        db.refresh(booking_1)
        db.refresh(booking_2)
        db.refresh(booking_3)

    bookings = db.query(models.Booking).all()

    if not db.query(models.Review).first():
        booking_1 = bookings[0]
        booking_2 = bookings[1]
        booking_3 = bookings[2]
        review_1 = models.Review(
            user_id=second_user.id,
            hotel_id=hotel_1.id,
            booking_id=booking_1.id,
            rating=3,
            comment="Good location but the room could be cleaner."
        )
        review_2 = models.Review(
            user_id=second_user.id,
            hotel_id=hotel_1.id,
            booking_id=booking_2.id,
            rating=5,
            comment="Excellent stay! Friendly staff and amazing view."
        )
        review_3 = models.Review(
            user_id=second_user.id,
            hotel_id=hotel_2.id,
            booking_id=booking_3.id,
            rating=2,
            comment="Nice location but the service was disappointing."
        )

        db.add_all([review_1, review_2, review_3])
        db.commit()
        print("Reviews created")

if __name__ == "__main__":
    seed_data()