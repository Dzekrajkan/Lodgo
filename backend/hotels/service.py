import os
import uuid
from typing import Optional
import redis.asyncio as redis
from fastapi import HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from backend import models

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
HOTEL_MEDIA_ROOT = "backend/media/hotels"
ROOM_MEDIA_ROOT = "backend/media/rooms"

def get_redis(request: Request) -> Optional[redis.Redis]:
    return getattr(request.app.state, "redis_client", None)

async def get_hotel_rating(db: Session, redis_client: Optional[redis.Redis], hotel: models.Hotel,) -> tuple[float, int]:
    rating_raw = None
    count_raw = None

    if redis_client:
        try:
            rating_raw = await redis_client.get(f"hotel:{hotel.id}:rating")
            count_raw = await redis_client.get(f"hotel:{hotel.id}:reviews_count")
        except Exception:
            rating_raw = None
            count_raw = None

    if rating_raw is not None and count_raw is not None:
        return float(rating_raw), int(count_raw)

    reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel.id).all()
    if reviews:
        rating = sum(review.rating for review in reviews) / len(reviews)
        reviews_count = len(reviews)
    else:
        rating = 0.0
        reviews_count = 0

    if redis_client:
        try:
            await redis_client.set(f"hotel:{hotel.id}:rating", rating)
            await redis_client.set(f"hotel:{hotel.id}:reviews_count", reviews_count)
        except Exception:
            pass

    return rating, reviews_count

def save_hotel_image(db: Session, hotel_id: int, file: UploadFile, is_main: bool) -> models.HotelImage:
    if is_main:
        existing_main = db.query(models.HotelImage).filter(models.HotelImage.hotel_id == hotel_id, models.HotelImage.is_main == True).first()
        if existing_main:
            raise HTTPException(400, "The main image of the hotel already exists")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type")

    contents = file.file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(400, "File is too large")

    folder = f"{HOTEL_MEDIA_ROOT}/{hotel_id}"
    os.makedirs(folder, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{folder}/{safe_name}"
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    image_url = f"/media/hotels/{hotel_id}/{safe_name}"
    new_image = models.HotelImage(hotel_id=hotel_id, image_url=image_url, is_main=is_main)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

def save_room_image(db: Session, room_id: int, file: UploadFile, is_main: bool) -> models.RoomImage:
    if is_main:
        existing_main = db.query(models.RoomImage).filter(models.RoomImage.room_id == room_id, models.RoomImage.is_main == True).first()
        if existing_main:
            raise HTTPException(400, "The main image of the room already exists")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type")

    contents = file.file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(400, "File is too large")

    folder = f"{ROOM_MEDIA_ROOT}/{room_id}"
    os.makedirs(folder, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{folder}/{safe_name}"
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    image_url = f"/media/rooms/{room_id}/{safe_name}"
    new_image = models.RoomImage(room_id=room_id, image_url=image_url, is_main=is_main)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image