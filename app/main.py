from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI
from fastapi import Request

from app.database.init_db import init_db
from app.logging_config import configure_logging
from app.routes.accounts import router as accounts_router
from app.routes.customers import router as customers_router
from app.routes.transactions import router as transactions_router

configure_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Mini Core Banking System application")
    init_db()
    yield
    logger.info("Shutting down Mini Core Banking System application")


app = FastAPI(
    title="Mini Core Banking System",
    description="A lightweight backend API for core banking operations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(customers_router)
app.include_router(accounts_router)
app.include_router(transactions_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "%s %s -> %s in %sms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Mini Core Banking System API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
