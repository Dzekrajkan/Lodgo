import redis
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from backend import models
from backend.celery_app import celery
from backend.config import REDIS_HOST, REDIS_PORT
from backend.database import SessionLocal

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@celery.task(ignore_result=True)
def hotel_rating():
    db = SessionLocal()
    try:
        results = (
            db.query(models.Review.hotel_id,
                func.avg(models.Review.rating).label("avg_rating"),
                func.count(models.Review.id).label("reviews_count"),
            ).group_by(models.Review.hotel_id).all()
        )

        rated_hotel_ids = set()
        for hotel_id, avg_rating, reviews_count in results:
            redis_client.set(f"hotel:{hotel_id}:rating", float(avg_rating))
            redis_client.set(f"hotel:{hotel_id}:reviews_count", reviews_count)
            rated_hotel_ids.add(hotel_id)

        all_hotel_ids = {row[0] for row in db.query(models.Hotel.id).all()}
        for hotel_id in all_hotel_ids - rated_hotel_ids:
            redis_client.set(f"hotel:{hotel_id}:rating", 0)
            redis_client.set(f"hotel:{hotel_id}:reviews_count", 0)
    finally:
        db.close()

@celery.task(ignore_result=True)
def bookings_cancel():
    db = SessionLocal()
    try:
        ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        bookings = (db.query(models.Booking)
            .filter(
                models.Booking.status == models.BookingStatus.pending,
                models.Booking.created_at <= ten_minutes_ago,
            ).all()
        )
        for booking in bookings:
            booking.status = models.BookingStatus.cancelled
        db.commit()
    finally:
        db.close()

@celery.task(ignore_result=True)
def booking_completed():
    db = SessionLocal()
    try:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        bookings = (db.query(models.Booking)
            .filter(
                models.Booking.status == models.BookingStatus.confirmed,
                models.Booking.date_to < today,
            ).all()
        )
        for booking in bookings:
            booking.status = models.BookingStatus.completed
        db.commit()
    finally:
        db.close()