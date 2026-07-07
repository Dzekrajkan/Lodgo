from datetime import date
from typing import Optional, Union
import redis.asyncio as redis
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload
from backend import models
from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.hotels import schemas
from backend.hotels.service import get_hotel_rating, get_redis, save_hotel_image, save_room_image
from backend.schemas import MessageOut

router = APIRouter(prefix="/api", tags=["hotels"])

@router.get("/facilities", response_model=list[schemas.FacilityOut])
def get_facilities(db: Session = Depends(get_db)):
    return db.query(models.Facility).all()

@router.post("/facilities", response_model=schemas.FacilityOut)
def post_facilities(facilities: schemas.FacilitiesCreate, db: Session = Depends(get_db)):
    new_facilities = models.Facility(name=facilities.name)
    db.add(new_facilities)
    db.commit()
    db.refresh(new_facilities)
    return new_facilities

@router.post("/service", response_model=schemas.ServiceOut)
def post_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    new_service = models.Service(hotel_id=service.hotel_id, name=service.name, price=service.price)
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/hotels", response_model=list[schemas.HotelOut])
async def get_hotels(db: Session = Depends(get_db), redis_client: Optional[redis.Redis] = Depends(get_redis)):
    hotels = db.query(models.Hotel).options(selectinload(models.Hotel.facilities), selectinload(models.Hotel.images)).all()
    for hotel in hotels:
        hotel.rating, hotel.reviews_count = await get_hotel_rating(db, redis_client, hotel)
    return hotels

@router.get("/hotels/search", response_model=list[schemas.HotelOut])
async def search_hotels(city: str = Query(...), date_from: date = Query(...), date_to: date = Query(...), guests: int = Query(..., ge=1), db: Session = Depends(get_db), redis_client: Optional[redis.Redis] = Depends(get_redis)):
    if date_from >= date_to:
        raise HTTPException(400, "Please enter a valid date")

    busy_room_ids = (db.query(models.Booking.room_id, func.count(models.Booking.id).label("booked_count"))
        .filter(
            models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]),
            models.Booking.date_from < date_to,
            models.Booking.date_to > date_from,
        ).group_by(models.Booking.room_id).subquery()
    )
    
    available_rooms = (db.query(models.Room).join(models.Hotel).outerjoin(busy_room_ids, models.Room.id == busy_room_ids.c.room_id)
        .filter(
            models.Hotel.city == city,
            models.Room.capacity == guests,
            or_(busy_room_ids.c.booked_count == None, busy_room_ids.c.booked_count < models.Room.quantity),
        ).subquery()
    )
    hotels = (db.query(models.Hotel)
        .join(available_rooms, models.Hotel.id == available_rooms.c.hotel_id).distinct()
        .options(selectinload(models.Hotel.rooms), selectinload(models.Hotel.images)).all()
    )
    for hotel in hotels:
        hotel.rating, hotel.reviews_count = await get_hotel_rating(db, redis_client, hotel)
    return hotels

@router.get("/hotels/{hotel_id}", response_model=schemas.HotelOut)
async def get_hotel(hotel_id: int = Path(...), db: Session = Depends(get_db), redis_client: Optional[redis.Redis] = Depends(get_redis)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).options(selectinload(models.Hotel.facilities)).first()

    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")

    hotel.images = db.query(models.HotelImage).filter(models.HotelImage.hotel_id == hotel_id).all()
    hotel.services = db.query(models.Service).filter(models.Service.hotel_id == hotel_id).all()
    hotel.rating, hotel.reviews_count = await get_hotel_rating(db, redis_client, hotel)

    return hotel

@router.post("/hotels", response_model=schemas.HotelOut)
def create_hotel(hotel: schemas.HotelCreate, db: Session = Depends(get_db)):
    facility_ids = hotel.facility_ids
    service_ids = hotel.service_ids
    facilities = db.query(models.Facility).filter(models.Facility.id.in_(facility_ids)).all()
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

    new_hotel.rating = 0.0
    new_hotel.reviews_count = 0
    return new_hotel

@router.post("/hotels/{hotel_id}/upload-image", response_model=schemas.HotelImageOut)
def post_images_hotels(hotel_id: int = Path(...), is_main: bool = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    return save_hotel_image(db, hotel_id, file, is_main)


@router.get("/hotels/{hotel_id}/rooms", response_model=list[schemas.RoomAvailabilityOut])
def get_rooms(hotel_id: int = Path(...), date_from: date = Query(...), date_to: date = Query(...), guests: int = Query(..., ge=1), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(400, "There is no such hotel")

    busy_room_ids = (db.query(models.Booking.room_id, func.count(models.Booking.id).label("booked_count"))
        .filter(
            models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]),
            models.Booking.date_from < date_to,
            models.Booking.date_to > date_from,
        ).group_by(models.Booking.room_id).subquery()
    )
    rooms = (db.query(models.Room, (models.Room.quantity - func.coalesce(busy_room_ids.c.booked_count, 0)).label("available_count"))
        .outerjoin(busy_room_ids, models.Room.id == busy_room_ids.c.room_id)
        .options(selectinload(models.Room.images))
        .filter(
            models.Room.hotel_id == hotel_id,
            models.Room.capacity == guests,
            or_(busy_room_ids.c.booked_count == None, busy_room_ids.c.booked_count < models.Room.quantity),
        ).all()
    )
    return [
        {
            "id": room.id,
            "hotel_id": hotel_id,
            "name": room.name,
            "description": room.description,
            "capacity": room.capacity,
            "price_per_night": room.price_per_night,
            "quantity": room.quantity,
            "available": available_count,
            "images": room.images,
        }
        for room, available_count in rooms
    ]


@router.post("/hotels/{hotel_id}/rooms", response_model=schemas.RoomOut)
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
        quantity=room.quantity,
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@router.post("/hotels/{hotel_id}/rooms/{room_id}/upload-image", response_model=schemas.RoomImageOut)
def post_images_rooms(hotel_id: int = Path(...), room_id: int = Path(...), is_main: bool = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id, models.Room.hotel_id == hotel_id).first()
    if not room:
        raise HTTPException(400, "There is no such room")
    return save_room_image(db, room_id, file, is_main)


@router.get("/favorite", response_model=list[schemas.FavoriteHotelOut])
def get_favorite(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (db.query(models.FavoriteHotel)
        .filter(models.FavoriteHotel.user_id == user.id)
        .options(selectinload(models.FavoriteHotel.hotel).selectinload(models.Hotel.images)).all()
    )

@router.post("/favorite", response_model=Union[schemas.FavoriteHotelOut, MessageOut])
def add_favorite(favorite: schemas.FavoriteHotelCreate, status: str = Query(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == favorite.hotel_id).first()
    if not hotel:
        raise HTTPException(400, "There is no such hotel")

    if status == "add":
        existing = (db.query(models.FavoriteHotel)
            .filter(models.FavoriteHotel.user_id == user.id, models.FavoriteHotel.hotel_id == favorite.hotel_id).first()
        )
        if existing:
            return existing
        new_favorite = models.FavoriteHotel(
            user_id=user.id, 
            hotel_id=favorite.hotel_id
        )
        db.add(new_favorite)
        db.commit()
        db.refresh(new_favorite)
        return new_favorite

    if status == "remove":
        favorite_obj = (db.query(models.FavoriteHotel)
            .filter(models.FavoriteHotel.user_id == user.id, models.FavoriteHotel.hotel_id == favorite.hotel_id).first()
        )
        if not favorite_obj:
            raise HTTPException(400, "You don't have this hotel in your favorites.")
        db.delete(favorite_obj)
        db.commit()
        return {"success": "removed"}
    
    raise HTTPException(400, "Invalid status. Use 'add' or 'remove'.")