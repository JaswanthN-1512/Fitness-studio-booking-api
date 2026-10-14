import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.logging_config import configure_logging
from app.models import Booking, FitnessClass, User  # noqa: F401
from app.routers import auth, bookings, classes

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")
    yield
    logger.info("Application stopped")


app = FastAPI(
    title="Fitness Studio Booking API",
    version="1.0.0",
    description="A secure RESTful booking backend using FastAPI, SQLAlchemy, SQLite and JWT authentication.",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(bookings.router)


@app.get("/health", tags=["Health"], summary="Check API health")
def health():
    return {"status": "healthy"}
