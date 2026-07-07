from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Union, List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload
from backend import models
from backend.auth.dependencies import get_current_user
from backend.bookings import schemas
from backend.bookings import service as booking_service
from backend.database import get_db

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

@router.get("", response_model=Union[List[schemas.BookingsOut], schemas.BookingsOut])
def get_bookings(user: models.User = Depends(get_current_user), status: str = Query("all"), db: Session = Depends(get_db)):
    if status == "all":
        return (
            db.query(models.Booking).filter(models.Booking.user_id == user.id).order_by(models.Booking.created_at)
            .options(selectinload(models.Booking.hotel).selectinload(models.Hotel.images), selectinload(models.Booking.room)).all()
        )

    if status == "last":
        booking = (
            db.query(models.Booking)
            .filter(models.Booking.user_id == user.id, models.Booking.status == models.BookingStatus.confirmed)
            .order_by(desc(models.Booking.created_at))
            .options(selectinload(models.Booking.hotel).selectinload(models.Hotel.images), selectinload(models.Booking.room)).first()
        )

        if not booking:
            return []
        
        return booking
    
    raise HTTPException(400, "Invalid status. Use 'all' or 'last'.")

@router.post("", response_model=schemas.BookingsOut)
def create_bookings(bookings: schemas.BookingsCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return booking_service.create_booking(db, user, bookings)

@router.post("/{id}/cancel", response_model=schemas.BookingStatusOut)
def cancel_bookings(id: int = Path(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = booking_service.get_booking_or_404(db, id)
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

@router.post("/pay", response_model=schemas.BookingStatusOut)
def pay_bookings(pay: schemas.BookingsPay, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = booking_service.get_booking_or_404(db, pay.id)
    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(400, "The reservation has already been cancelled")
    if booking.status == models.BookingStatus.confirmed:
        raise HTTPException(400, "The reservation has already been paid for.")
    if booking.user_id != user.id:
        raise HTTPException(400, "The reservation does not belong to you")
    if len(pay.card_number) < 7 or len(pay.CVC) < 3:
        raise HTTPException(400, "Please enter correct card details")

    booking.status = models.BookingStatus.confirmed
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{id}/completed", response_model=schemas.BookingStatusOut)
def completed_bookings(id: int = Path(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = booking_service.get_booking_or_404(db, id)
    if booking.user_id != user.id:
        raise HTTPException(400, "The reservation does not belong to you")
    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(400, "Reservation cancelled")
    if booking.status != models.BookingStatus.confirmed:
        raise HTTPException(400, "The reservation has not been paid")

    booking.status = models.BookingStatus.completed
    db.commit()
    db.refresh(booking)
    return booking