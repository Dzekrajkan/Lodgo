from fastapi import FastAPI, HTTPException, Depends, Response, Request, UploadFile, File, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend import schemas, models
from backend.database import get_db, engine
from backend.auth import email_utils, auth
from backend.config import SECRET_KEY, REDIS_HOST, REDIS_PORT
from backend.celery_app import celery
from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session, selectinload
import redis.asyncio as redis
from datetime import datetime, timezone, date
from jose import jwt
import asyncio
import shutil
import uvicorn
import os

SECRET_KEY = SECRET_KEY
MAX_SIZE = 10 * 1024 * 1024
redis_client: redis.Redis | None = None
app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api/media", StaticFiles(directory="backend/media"), name="media")

@app.on_event("startup")
async def startup_event():
    global redis_client
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        pong = await redis_client.ping()
        if pong:
            celery.send_task("backend.tasks.hotel_rating")
            print("✅ Redis connection established")
        else:
            print("⚠️ Redis connected but not responding to ping")
    except Exception as e:
        redis_client = None
        print(f"❌Error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            await redis_client.connection_pool.disconnect()
            print("🔘 Redis connection closed")
        except asyncio.CancelledError:
            print("⚠️ Shutdown прерван CancelledError")

def get_current_user(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = auth.verify_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@app.post("/api/refresh")
def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="You are not logged in.")
    
    payload = auth.verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    id = payload.get("sub")
    new_access_token = auth.create_access_token({"sub": id})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax"
    )

    return {"success": "Access token refreshed"}

@app.post("/api/login")
async def login(response: Response, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")
    if not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password or login")
    if not user.is_verified:
        raise HTTPException(403, "Email not confirmed")

    access_token = auth.create_access_token({"sub": str(user.id)})
    refresh_token = auth.create_refresh_token({"sub": str(user.id)})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False,
        samesite="lax"
    )

    return {"success": "Logged in successfully"}

@app.post("/api/register")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if user_by_email:
        raise HTTPException(status_code=400, detail="Email is already in use")
    
    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=auth.hash_password(user.password1),
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = auth.create_verification_token(new_user.id)

    await email_utils.send_verification_email(new_user.email, token)

    return {"success": "Registration successful, confirmation email sent to email"}

@app.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", httponly=True, samesite="lax", path="/")
    response.delete_cookie("refresh_token", httponly=True, samesite="lax", path="/")
    return {"success": "Logout successful"}

@app.get("/api/auth/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = auth.verify_token(token)

        if payload["type"] != "email_verify":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = int(payload["sub"])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="The token has expired")
    except:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException("This user does not exist.")
    user.is_verified = True
    db.commit()

    return {"success": "Your email has been confirmed. Now log in to your account."}

@app.get("/api/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/api/facilities")
def get_facilities(db: Session = Depends(get_db)):
    facilities = db.query(models.Facility).all()
    return facilities

@app.post("/api/facilities")
def post_facilities(facilities: schemas.FacilitiesCreate, db: Session = Depends(get_db)):
    new_facilities = models.Facility(
        name = facilities.name
    )
    db.add(new_facilities)
    db.commit()
    db.refresh(new_facilities)
    return new_facilities

@app.post("/api/service")
def post_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    new_service = models.Service(
        hotel_id=service.hotel_id,
        name=service.name,
        price=service.price
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return new_service

@app.get("/api/hotels", response_model=list[schemas.HotelOut])
async def get_hotels(db: Session = Depends(get_db)):
    hotels = db.query(models.Hotel).options(selectinload(models.Hotel.facilities), selectinload(models.Hotel.images)).all()
    for hotel in hotels:
        rating = None
        try:
            if redis_client:
                rating = await redis_client.get(f"hotel:{hotel.id}:rating")
        except Exception:
            rating = None
        if rating == None:
            reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel.id).all()
            if reviews:
                rating = sum(review.rating for review in reviews) / len(reviews)
            else:
                rating = 0
            try:
                if redis_client:
                    await redis_client.set(f"hotel:{hotel.id}:rating", rating)
            except Exception:
                pass
        else:
            rating = float(rating)
        hotel.rating = rating
    return hotels

@app.get("/api/hotels/search", response_model=list[schemas.HotelOut])
async def search_hotels(city: str = Query(...), date_from: date = Query(...), date_to: date = Query(...), guests: int = Query(..., ge=1), db: Session = Depends(get_db)):
    if date_from >= date_to:
        raise HTTPException(400, "Please enter a valid date")
    busy_room_ids = db.query(models.Booking.room_id, func.count(models.Booking.id).label("booked_count")).filter(models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]), models.Booking.date_from < date_to, models.Booking.date_to > date_from).group_by(models.Booking.room_id).subquery()
    available_rooms = db.query(models.Room).join(models.Hotel).outerjoin(busy_room_ids, models.Room.id == busy_room_ids.c.room_id).filter(models.Hotel.city == city, models.Room.capacity == guests, or_(busy_room_ids.c.booked_count == None, busy_room_ids.c.booked_count < models.Room.quantity)).subquery()
    hotels = db.query(models.Hotel).join(available_rooms, models.Hotel.id == available_rooms.c.hotel_id).distinct().options(selectinload(models.Hotel.rooms), selectinload(models.Hotel.images)).all()
    for hotel in hotels:
        rating = None
        try:
            if redis_client:
                rating = await redis_client.get(f"hotel:{hotel.id}:rating")
        except Exception:
            rating = None
        if rating == None:
            reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel.id).all()
            if reviews:
                rating = sum(review.rating for review in reviews) / len(reviews)
            else:
                rating = 0
            try:
                if redis_client:
                    await redis_client.set(f"hotel:{hotel.id}:rating", rating)
            except Exception:
                pass
        else:
            rating = float(rating)
        hotel.rating = rating
    return hotels

@app.get("/api/hotels/{hotel_id}", response_model=schemas.HotelOut)
async def get_hotel(hotel_id: int = Path(...), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).options(selectinload(models.Hotel.facilities)).first()
    images = db.query(models.HotelImage).filter(models.HotelImage.hotel_id == hotel_id).all()
    services = db.query(models.Service).filter(models.Service.hotel_id == hotel_id).all()
    rating = None
    reviews_count = None
    try:
        if redis_client:
            rating = await redis_client.get(f"hotel:{hotel.id}:rating")
            reviews_count = await redis_client.get(f"hotel:{hotel.id}:reviews_count")
    except Exception:
        rating = None
        reviews_count = None
    if rating == None:
        reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel.id).all()
        if reviews:
            rating = sum(review.rating for review in reviews) / len(reviews)
            reviews_count = len(reviews)
        else:
            rating = 0
            reviews_count = 0
        try:
            if redis_client:
                await redis_client.set(f"hotel:{hotel.id}:rating", rating)
                await redis_client.set(f"hotel:{hotel.id}:reviews_count", reviews_count)
        except Exception:
            pass
    else:
        rating = float(rating)
        reviews = int(reviews_count)
    hotel.rating = rating
    hotel.reviews_count = reviews_count
    hotel.images = images
    hotel.services = services
    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")
    return hotel

@app.post("/api/hotels")
def create_hotel(hotel: schemas.HotelCreate, db: Session = Depends(get_db)):
    facility_ids = hotel.facility_ids
    facilities = db.query(models.Facility).filter(models.Facility.id.in_(facility_ids)).all()
    service_ids = hotel.service_ids
    services = db.query(models.Service).filter(models.Service.id.in_(service_ids)).all()
    if len(facilities) != len(set(facility_ids)):
        raise HTTPException(status_code=400, detail="One or more amenities were not found.")
    if len(services) != len(set(service_ids)):
        raise HTTPException(status_code=400, detail="One or more services were not found.")
    new_hotel = models.Hotel(
        owner_id=hotel.owner_id,
        name=hotel.name,
        description=hotel.description,
        address=hotel.address,
        city=hotel.city,
        country=hotel.country,
        latitude=hotel.latitude,
        longitude=hotel.longitude,
        price_per_night=hotel.price_per_night,
        check_in_time=hotel.check_in_time,
        check_out_time=hotel.check_out_time,
    )
    new_hotel.facilities = facilities
    new_hotel.services = services

    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel

@app.post("/api/hotels/{hotel_id}/upload-image")
def post_images_hotels(hotel_id: int = Path(...), is_main: bool = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if is_main:
        main_image = db.query(models.HotelImage).filter(models.HotelImage.hotel_id == hotel_id, models.HotelImage.is_main == True).all()
        if main_image:
            raise HTTPException(400, "The main image of the hotel already exists")
    folder = f"backend/media/hotels/{hotel_id}"
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    image_url = f"/media/hotels/{hotel_id}/{file.filename}"
    new_image = models.HotelImage(
        hotel_id=hotel_id,
        image_url=image_url,
        is_main=is_main
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

@app.get("/api/hotels/{hotel_id}/rooms")
def get_rooms(hotel_id: int = Path(...), date_from: date = Query(...), date_to: date = Query(...), guests: int = Query(..., ge=1),  db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(400, "There is no such hotel")
    busy_room_ids = db.query(models.Booking.room_id, func.count(models.Booking.id).label("booked_count")).filter(models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]), models.Booking.date_from < date_to, models.Booking.date_to > date_from).group_by(models.Booking.room_id).subquery()
    rooms = db.query(models.Room, (models.Room.quantity - func.coalesce(busy_room_ids.c.booked_count, 0)).label("available_count")).outerjoin(busy_room_ids, models.Room.id == busy_room_ids.c.room_id).filter(models.Room.hotel_id == hotel_id, models.Room.capacity == guests, or_(busy_room_ids.c.booked_count == None, busy_room_ids.c.booked_count < models.Room.quantity)).all()
    return [
        {
            "id": room.id,
            "hotel_id": hotel_id,
            "name": room.name,
            "description": room.description,
            "capacity": room.capacity,
            "price_per_night": room.price_per_night,
            "quantity": room.quantity,
            "available": available_count
        }
        for room, available_count in rooms
    ]

@app.post("/api/hotels/{hotel_id}/rooms")
def create_room(room: schemas.RoomCreate, hotel_id: int = Path(...), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(400, "There is no such hotel")
    new_room = models.Room(
        hotel_id=room.hotel_id,
        name=room.name,
        description=room.description,
        price_per_night=room.price_per_night,
        capacity=room.capacity,
        quantity=room.quantity
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room

@app.get("/api/bookings")
def get_bookings(user: models.User = Depends(get_current_user), status: str = Query("all"), db: Session = Depends(get_db)):
    if status == "all":
        bookings = db.query(models.Booking).filter(models.Booking.user_id == user.id).order_by(models.Booking.created_at).options(selectinload(models.Booking.hotel).selectinload(models.Hotel.images), selectinload(models.Booking.room)).all()
        if not bookings:
            return None
        return bookings
    if status == "last":
        last_booking = db.query(models.Booking).filter(models.Booking.user_id == user.id, models.Booking.status == models.BookingStatus.confirmed).order_by(desc(models.Booking.created_at)).options(selectinload(models.Booking.hotel).selectinload(models.Hotel.images), selectinload(models.Booking.room)).first()
        if not last_booking:
            return None
        return last_booking
    
@app.post("/api/bookings")
def create_bookings(bookings: schemas.BookingsCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    with db.begin_nested():
        room = db.query(models.Room).filter(models.Room.id == bookings.room_id).with_for_update().first()
        if not room:
            raise HTTPException(400, "This room doesn't exist")
        if bookings.date_from >= bookings.date_to:
            raise HTTPException(400, "Please enter the correct date")
        existing_bookings = db.query(models.Booking).filter(models.Booking.room_id == bookings.room_id, models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]), models.Booking.date_from < bookings.date_to, models.Booking.date_to > bookings.date_from).count()
        if existing_bookings >= room.quantity:
            raise HTTPException(400, "There are no available seats for the selected dates.")
        service_ids = bookings.service_ids
        services = db.query(models.Service).filter(models.Service.id.in_(service_ids)).all()
        if len(services) != len(set(service_ids)):
            raise HTTPException(400, detail="One or more services were not found.")
        if not bookings.guest_first_name or not bookings.guest_last_name or not bookings.guest_email:
            raise HTTPException(400, "Enter all user details")
        total_price_services = sum(service.price for service in services)
        total_price = (bookings.date_to - bookings.date_from).days * room.price_per_night + total_price_services
        new_bookings = models.Booking(
            user_id=user.id,
            room_id=bookings.room_id,
            hotel_id=bookings.hotel_id,
            date_from=bookings.date_from,
            date_to=bookings.date_to,
            guest_first_name=bookings.guest_first_name,
            guest_last_name=bookings.guest_last_name,
            guest_email=bookings.guest_email,
            total_price=total_price
        )
        new_bookings.services = services
        db.add(new_bookings)
    db.commit()
    db.refresh(new_bookings)
    return new_bookings

@app.post("/api/bookings/{id}/cancel")
def cancel_bookings(id: int = Path(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if not booking:
        raise HTTPException(400, "Such armor does not exist.")
    if booking.user_id != user.id:
        raise HTTPException(400, "The reservation does not belong to you")
    if booking.status == models.BookingStatus.completed:
        raise HTTPException(400, "The reservation is already completed")
    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(400, "The reservation has already been cancelled.")
    booking.status = models.BookingStatus.cancelled
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/api/bookings/pay")
def pay_bookings(pay: schemas.BookingsPay, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == pay.id).first()
    if not booking:
        raise HTTPException(400, "Such armor does not exist.")
    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(400, "the reservation has already been cancelled")
    if booking.status == models.BookingStatus.confirmed:
        raise HTTPException(400, "The reservation has already been paid for.")
    if not booking.user_id == user.id:
        raise HTTPException(400, "The reservation does not belong to you")
    if len(pay.card_number) < 7 or len(pay.CVC) < 3:
        raise HTTPException(400, "Please enter correct card details")
    booking.status = models.BookingStatus.confirmed
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/api/bookings/{id}/completed")
def completed_bookings(id: int = Path(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if booking.user_id != user.id:
        raise HTTPException(400, "The reservation does not belong to you")
    if booking.status != models.BookingStatus.confirmed:
        raise HTTPException(400, "The reservation has not been paid")
    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(400, "Reservation canceled")
    booking.status = models.BookingStatus.completed
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/api/favorite")
def get_favorite(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorites = db.query(models.FavoriteHotel).filter(models.FavoriteHotel.user_id == user.id).options(selectinload(models.FavoriteHotel.hotel).selectinload(models.Hotel.images)).all()
    return favorites

@app.post("/api/favorite")
def add_favorite(favorite: schemas.FavoriteHotelCreate, status: str = Query(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == favorite.hotel_id).first()
    if not hotel:
        raise HTTPException(400, "There is no such hotel")
    if status == "add":
        existing = db.query(models.FavoriteHotel).filter(models.FavoriteHotel.user_id == user.id, models.FavoriteHotel.hotel_id == favorite.hotel_id).first()
        if existing:
            return existing
        new_favorite = models.FavoriteHotel(
            user_id=user.id,
            hotel_id=favorite.hotel_id,
        )
        db.add(new_favorite)
        db.commit()
        db.refresh(new_favorite)
        return new_favorite
    elif status == "remove":
        favorite_obj = db.query(models.FavoriteHotel).filter(models.FavoriteHotel.user_id == user.id, models.FavoriteHotel.hotel_id == favorite.hotel_id).first()
        if not favorite_obj:
            raise HTTPException(400, "You don't have this hotel in your favorites.")
        db.delete(favorite_obj)
        db.commit()
        return {"status": "removed"}
    
@app.get("/api/reviews/{hotel_id}", response_model=list[schemas.ReviewOut])
def get_reviews(hotel_id: int = Path(...), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")
    reviews = db.query(models.Review).filter(models.Review.hotel_id == hotel_id).options(selectinload(models.Review.user)).limit(20).all()
    return reviews

@app.post("/api/review")
def create_review(review: schemas.ReviewCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == review.hotel_id).first()
    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")
    if review.booking_id:
        existing_review = db.query(models.Review).filter(models.Review.booking_id == review.booking_id).first()
        if existing_review:
            raise HTTPException(400, "A review for this reservation already exists.")
        booking = db.query(models.Booking).filter(models.Booking.id == review.booking_id, models.Booking.status == models.BookingStatus.completed, models.Booking.user_id == user.id, models.Booking.hotel_id == review.hotel_id).first()
        if not booking:
            raise HTTPException(400, "The booking details are incorrect")
    else:
        completed_bookings = db.query(models.Booking.id).filter(models.Booking.user_id == user.id, models.Booking.status == models.BookingStatus.completed, models.Booking.hotel_id == review.hotel_id)
        used_booking_ids = db.query(models.Review.booking_id).filter(models.Review.user_id == user.id,models.Review.hotel_id == review.hotel_id)
        free_booking = completed_bookings.filter(~models.Booking.id.in_(used_booking_ids)).first()
        if not free_booking:
            raise HTTPException(400, "There are no completed bookings to review.")
        review.booking_id = free_booking.id
    new_review = models.Review(
        user_id=user.id,
        hotel_id=review.hotel_id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)