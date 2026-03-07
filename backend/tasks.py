from backend.database import SessionLocal
from datetime import datetime, timedelta
from backend.celery_app import celery
from backend.config import REDIS_HOST, REDIS_PORT
from backend import models
import redis
import pytz

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
tz = pytz.timezone("Europe/Kiev")

@celery.task
def hotel_rating():
    db = SessionLocal()
    hotels = db.query(models.Hotel).all()
    for hotel in hotels:
        reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel.id).all()
        if reviews:
            rating = sum(r.rating for r in reviews) / len(reviews)
            redis_client.set(f"hotel:{hotel.id}:rating", rating)
            redis_client.set(f"hotel:{hotel.id}:reviews_count", len(reviews))
        else:
            redis_client.set(f"hotel:{hotel.id}:rating", 0)
            redis_client.set(f"hotel:{hotel.id}:reviews_count", 0)
    db.close()

@celery.task
def bookings_cancel():
    db = SessionLocal()
    ten_minutes_ago = datetime.now(tz) - timedelta(minutes=1)
    bookings = db.query(models.Booking).filter(models.Booking.status == models.BookingStatus.pending, models.Booking.created_at <= ten_minutes_ago).all()
    for booking in bookings:
        booking.status = models.BookingStatus.cancelled
    db.commit()
    db.close()

@celery.task
def booking_completed():
    db = SessionLocal()
    today = datetime.now(tz).date()
    bookings = db.query(models.Booking).filter(models.Booking.status == models.BookingStatus.confirmed, models.Booking.date_to < today).all()
    for booking in bookings:
        booking.status = models.BookingStatus.completed
    db.commit()
    db.close()