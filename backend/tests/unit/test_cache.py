import pytest
from unittest.mock import AsyncMock, patch

from app.core.cache import MemoryCache, global_cache
from app.schemas.api_schemas import VehicleValuationRequest
from app.services.car_catalog_service import search_cars
from app.services.valuation_service import estimate_vehicle_value


@pytest.fixture(autouse=True)
def clear_caches():
    global_cache.clear()


@pytest.mark.asyncio
async def test_memory_cache_get_or_call():
    cache = MemoryCache(ttl=60)
    mock_func = AsyncMock(return_value={"result": "data"})

    # First call - cache miss
    res1 = await cache.get_or_call("test_prefix", mock_func, "arg1", param="value1")
    assert res1 == {"result": "data"}
    assert mock_func.call_count == 1

    # Second call with same parameters - cache hit
    res2 = await cache.get_or_call("test_prefix", mock_func, "arg1", param="value1")
    assert res2 == {"result": "data"}
    assert mock_func.call_count == 1  # Not incremented!

    # Different parameters - cache miss
    res3 = await cache.get_or_call("test_prefix", mock_func, "arg2", param="value1")
    assert res3 == {"result": "data"}
    assert mock_func.call_count == 2


@pytest.mark.asyncio
async def test_search_cars_caching():
    with patch("app.services.car_catalog_service._search_cars_uncached", new_callable=AsyncMock) as mock_uncached:
        mock_uncached.return_value = []

        await search_cars("Volkswagen", "Golf")
        assert mock_uncached.call_count == 1

        await search_cars("Volkswagen", "Golf")
        assert mock_uncached.call_count == 1  # Cached!


@pytest.mark.asyncio
async def test_valuation_caching():
    req = VehicleValuationRequest(make="Fiat", model="500", year=2020)
    with patch("app.services.valuation_service._estimate_vehicle_value_uncached", new_callable=AsyncMock) as mock_uncached:
        mock_uncached.return_value = AsyncMock()

        await estimate_vehicle_value(req)
        assert mock_uncached.call_count == 1

        await estimate_vehicle_value(req)
        assert mock_uncached.call_count == 1  # Cached!
