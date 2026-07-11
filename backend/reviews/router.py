from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session, selectinload
from backend import models
from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.reviews import schemas

router = APIRouter(prefix="/api", tags=["reviews"])

@router.get("/reviews/{hotel_id}", response_model=list[schemas.ReviewOut])
def get_reviews(hotel_id: int = Path(...), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")

    return db.query(models.Review).filter(models.Review.hotel_id == hotel_id).options(selectinload(models.Review.user)).limit(20).all()

@router.post("/review", response_model=schemas.ReviewOut, status_code=201)
def create_review(review: schemas.ReviewCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == review.hotel_id).first()
    if not hotel:
        raise HTTPException(400, "Such a hotel does not exist.")

    if review.booking_id:
        existing_review = db.query(models.Review).filter(models.Review.booking_id == review.booking_id).first()
        if existing_review:
            raise HTTPException(400, "A review for this reservation already exists.")
        booking = (
            db.query(models.Booking)
            .filter(
                models.Booking.id == review.booking_id,
                models.Booking.status == models.BookingStatus.completed,
                models.Booking.user_id == user.id,
                models.Booking.hotel_id == review.hotel_id,
            )
            .first()
        )
        if not booking:
            raise HTTPException(400, "The booking details are incorrect")
    else:
        completed_bookings = db.query(models.Booking.id).filter(
            models.Booking.user_id == user.id,
            models.Booking.status == models.BookingStatus.completed,
            models.Booking.hotel_id == review.hotel_id,
        )
        used_booking_ids = db.query(models.Review.booking_id).filter(
            models.Review.user_id == user.id, models.Review.hotel_id == review.hotel_id
        )
        free_booking = completed_bookings.filter(~models.Booking.id.in_(used_booking_ids)).first()
        if not free_booking:
            raise HTTPException(400, "There are no completed bookings to review.")
        review.booking_id = free_booking.id

    new_review = models.Review(
        user_id=user.id,
        hotel_id=review.hotel_id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review