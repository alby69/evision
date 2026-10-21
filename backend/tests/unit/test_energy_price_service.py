import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.energy_price_service import fetch_regional_prices, _PRICE_CACHE

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    _PRICE_CACHE.clear()


@pytest.mark.asyncio
async def test_fetch_regional_prices_fallback():
    with patch("httpx.AsyncClient.get", side_effect=Exception("Network error")):
        data = await fetch_regional_prices("IT-25")
        assert data["region"] == "IT-25"
        assert data["region_name"] == "Lombardia"
        assert data["source"] == "DEFAULT_FALLBACK"
        assert data["petrol_eur_l"] > 0
        assert data["diesel_eur_l"] > 0


@pytest.mark.asyncio
async def test_fetch_regional_prices_success():
    mock_csv = (
        "id;descrizione;prezzo;isSelf\n"
        "1;Benzina;1.849;1\n"
        "2;Gasolio;1.799;1\n"
        "3;GPL;0.719;1\n"
        "4;Metano;1.299;1\n"
    )
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_csv

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        data = await fetch_regional_prices("IT-25")
        assert data["region"] == "IT-25"
        assert data["source"] == "MISE_API"
        assert data["petrol_eur_l"] == 1.849
        assert data["diesel_eur_l"] == 1.799
        assert data["lpg_eur_l"] == 0.719
        assert data["cng_eur_kg"] == 1.299


def test_get_fuel_prices_endpoint():
    response = client.get("/api/v1/prices/fuel?region=IT-25")
    assert response.status_code == 200
    data = response.json()
    assert data["region"] == "IT-25"
    assert "petrol_eur_l" in data
    assert "diesel_eur_l" in data
