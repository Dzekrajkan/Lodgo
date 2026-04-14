# Lodgo

Lodgo is a pet project that is a hotel booking website. The backend of the site is written in Python 3.11 with the FastAPI library, and the frontend is written in React-ts.  
The site includes login, registration, hotel search/filtering (mainly the search is based on the rooms available in the hotel), review writing, booking, payment, and cancellation of your booking.

## Table of Contents
  * [Overview](#overview)
  * [Installation and Setup](#installation-and-setup)

## Overview

Now we will go through how the main features of the site work, which are available to the user.

1. **Hotel search works through 4 parameters (city, check-in time, check-out time, number of guests). First, we search for hotels by city, then we check whether there are any available rooms in this hotel for the dates entered by the user. After that, we filter the remaining hotels by the maximum number of guests that can stay in the room. Below is the code snippet responsible for this:**
  ```python
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
  ```
  2. **How booking payment, cancellation, and completion work. Booking cancellation happens automatically with Celery if the user does not pay for the booking within 10 minutes. Booking payment happens through simple data validation: if everything is correct, then the booking status is changed to paid (I decided that for a pet project, making it more complicated is not necessary). Booking completion works in the same way as cancellation, through Celery: as soon as the time of the last day of the guests’ stay passes, the booking status is changed to completed. Below are code snippets.**

  Cancellation:
  ``` python
  @celery.task
  def bookings_cancel():
      db = SessionLocal()
      ten_minutes_ago = datetime.now(tz) - timedelta(minutes=1)
      bookings = db.query(models.Booking).filter(models.Booking.status == models.BookingStatus.pending, models.Booking.created_at <= ten_minutes_ago).all()
      for booking in bookings:
          booking.status = models.BookingStatus.cancelled
      db.commit()
      db.close()
  ```
  Payment:
  ``` python
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
  ```
  Completion:
  ``` python
  @celery.task
  def booking_completed():
      db = SessionLocal()
      today = datetime.now(tz).date()
      bookings = db.query(models.Booking).filter(models.Booking.status == models.BookingStatus.confirmed, models.Booking.date_to < today).all()
      for booking in bookings:
          booking.status = models.BookingStatus.completed
      db.commit()
      db.close()
  ```
  3. **It is also possible to write reviews for hotels. But in order to leave a review, the user must have at least 1 completed booking at that hotel. Everything works simply; below is the code snippet:**
  ``` python
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
  ```

## Installation and Setup
**To run the project, you need to install Docker in order to build a container with the basic data in the database ***(see point 3)***, the code, and its dependencies. Also, some functions are unavailable without changing the example.env file, подробнее below ***(see point 2)*****
  1. Go to the project folder and run one of the commands below; these are two commands for different Docker Compose versions:
     ```bash
     docker-compose up --build
     ```
     ```bash
     docker compose up --build
     ```
     That is all you will need to wait about 5 minutes, and the site will be ready to use.
  2. But, as I mentioned earlier, to make all functions available, specifically registration of a new account, you need to change these fields in the example.env file, because for login with a new account, it must be confirmed through a link that is sent to email. Therefore, you need to specify email data so that emails with the link are sent from it:
     ``` Dotenv
     MAIL_USERNAME=example@gmail.com
     MAIL_PASSWORD="ergr gerw wdfb ikhy"
     MAIL_FROM=example@gmail.com
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     ```
     (the last 2 fields very rarely need changes)

     If you do not know where to get this data, refer to this [documentation](https://www.hostpapa.com/knowledgebase/how-to-create-and-use-google-app-passwords/).
  3. When the container is created, the database is populated with basic data so that you can go through all the site’s features. These include hotel data, rooms, reviews, and accounts. You can see more in the [seed.py](./backend/seed.py) file

     **It is very important: to go through all the site’s features, you need to log in, and for this a test account has been created. Below are its email and password:**

     `test@gmail.com`

     `test1234`
