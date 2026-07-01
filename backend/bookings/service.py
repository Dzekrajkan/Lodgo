from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend import models
from backend.bookings.schemas import BookingsCreate

def create_booking(db: Session, user: models.User, data: BookingsCreate) -> models.Booking:
    with db.begin_nested():
        room = db.query(models.Room).filter(models.Room.id == data.room_id).with_for_update().first()
        if not room:
            raise HTTPException(400, "This room doesn't exist")

        if data.date_from >= data.date_to:
            raise HTTPException(400, "Please enter the correct date")

        existing_bookings = (
            db.query(models.Booking)
            .filter(
                models.Booking.room_id == data.room_id,
                models.Booking.status.in_([models.BookingStatus.pending, models.BookingStatus.confirmed]),
                models.Booking.date_from < data.date_to,
                models.Booking.date_to > data.date_from,
            ).count()
        )
        if existing_bookings >= room.quantity:
            raise HTTPException(400, "There are no available seats for the selected dates.")

        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        if len(services) != len(set(data.service_ids)):
            raise HTTPException(400, "One or more services were not found.")

        if not data.guest_first_name or not data.guest_last_name or not data.guest_email:
            raise HTTPException(400, "Enter all user details")

        nights = (data.date_to - data.date_from).days
        total_price = nights * room.price_per_night + sum(service.price for service in services)

        new_booking = models.Booking(
            user_id=user.id,
            room_id=data.room_id,
            hotel_id=data.hotel_id,
            date_from=data.date_from,
            date_to=data.date_to,
            guest_first_name=data.guest_first_name,
            guest_last_name=data.guest_last_name,
            guest_email=data.guest_email,
            total_price=total_price,
        )
        new_booking.services = services
        db.add(new_booking)

    db.commit()
    db.refresh(new_booking)
    return new_booking

def get_booking_or_404(db: Session, booking_id: int) -> models.Booking:
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(400, "Such booking does not exist.")
    return booking