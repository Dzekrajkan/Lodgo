from celery import Celery

celery = Celery("fastapi_app", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

celery.autodiscover_tasks(["backend"])

celery.conf.accept_content = ["json"]
celery.conf.task_serializer = "json"
celery.conf.result_serializer = "json"
celery.conf.timezone = "Europe/Kiev"
celery.conf.beat_schedule ={
    "hotel_rating": {
        "task": "backend.tasks.hotel_rating",
        "schedule": 60.0
    },
    "bookings_cancel": {
        "task": "backend.tasks.bookings_cancel",
        "schedule": 60.0
    },
    "booking_completed": {
        "task": "backend.tasks.booking_completed",
        "schedule": 3600.0
    },
}