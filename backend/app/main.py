from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analyses import router as analyses_router
from app.api.v1.calculations import router as calculations_router
from app.api.v1.garage import router as garage_router
from app.api.v1.prices import router as prices_router
from app.api.v1.vehicles import router as vehicles_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(
    title="EV Purchase Advisor API",
    description="API for Total Cost of Ownership (TCO), replacement economics, break-even timelines, and EV purchase recommendations.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles_router, prefix="/api/v1")
app.include_router(calculations_router, prefix="/api/v1")
app.include_router(garage_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")


@app.get("/")
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "EV Purchase Advisor API",
        "version": "0.1.0",
    }
