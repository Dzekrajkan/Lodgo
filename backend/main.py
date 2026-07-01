import asyncio
from contextlib import asynccontextmanager
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.auth.router import router as auth_router
from backend.bookings.router import router as bookings_router
from backend.celery_app import celery
from backend.config import CORS_ORIGINS, REDIS_HOST, REDIS_PORT
from backend.hotels.router import router as hotels_router
from backend.reviews.router import router as reviews_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client: redis.Redis | None = None

    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        await redis_client.ping()
        print("✅ Redis connection established")
    except Exception as e:
        redis_client = None
        print(f"❌ Redis unavailable: {repr(e)}")
        print("⚠️  Running without Redis cache — ratings will be calculated from DB on each request")

    if redis_client:
        try:
            celery.send_task("backend.tasks.hotel_rating")
            print("✅ Celery task scheduled")
        except Exception as e:
            print(f"⚠️  Celery unavailable: {repr(e)}")
            print("⚠️  Hotel ratings will not be pre-cached on startup")

    app.state.redis_client = redis_client

    yield

    if redis_client:
        try:
            await redis_client.close()
            await redis_client.connection_pool.disconnect()
            print("🔘 Redis connection closed")
        except asyncio.CancelledError:
            print("⚠️  Shutdown interrupted by CancelledError")

app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api/media", StaticFiles(directory="backend/media"), name="media")

app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(bookings_router)
app.include_router(reviews_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)