from typing import Any
from fastapi import APIRouter, Query

from app.services.energy_price_service import fetch_regional_prices

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get("/fuel", summary="Get regional average fuel and energy prices")
async def get_fuel_prices(
    region: str = Query("IT-25", description="Italian NUTS-2 region code (e.g. IT-25 for Lombardia)")
) -> dict[str, Any]:
    return await fetch_regional_prices(region=region)
