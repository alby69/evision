import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.listing_parser_service import parse_listing_url

client = TestClient(app)


@pytest.mark.asyncio
async def test_parse_listing_url_json_ld():
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fiat 500e La Prima 2023 - AutoScout24</title>
        <script type="application/ld+json">
        {
            "@type": "Car",
            "brand": {"name": "Fiat"},
            "model": {"name": "500e"},
            "productionDate": "2023",
            "offers": {"price": "22500"},
            "mileageFromOdometer": {"value": "15000"}
        }
        </script>
    </head>
    <body></body>
    </html>
    """
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_html

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await parse_listing_url("https://www.autoscout24.it/annunci/fiat-500e-12345")
        assert res.make == "Fiat"
        assert res.model == "500E" or res.model == "500e"
        assert res.year == 2023
        assert res.price_eur == 22500.0
        assert res.mileage_km == 15000


@pytest.mark.asyncio
async def test_parse_listing_url_fallback():
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tesla Model 3 2022 - € 28.500 - 45.000 km</title>
        <meta property="og:title" content="Tesla Model 3 2022 - € 28.500 - 45.000 km" />
    </head>
    <body>
        <p>Bellissima Tesla Model 3 del 2022 con 45.000 km, prezzo € 28.500</p>
    </body>
    </html>
    """
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_html

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await parse_listing_url("https://www.subito.it/auto/tesla-model-3-123.htm")
        assert res.make == "Tesla"
        assert res.year == 2022
        assert res.price_eur == 28500.0
        assert res.mileage_km == 45000


def test_parse_listing_api_endpoint_invalid_url():
    response = client.post("/api/v1/vehicles/parse-listing", json={"url": "not_a_valid_url"})
    assert response.status_code == 400
    assert "Invalid listing URL format" in response.json()["detail"]


def test_parse_listing_api_endpoint_network_error():
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection timeout")):
        response = client.post(
            "/api/v1/vehicles/parse-listing",
            json={"url": "https://www.autoscout24.it/annunci/tesla-model-3"},
        )
        assert response.status_code == 400
        assert "Network error" in response.json()["detail"]
