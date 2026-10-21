import json
import logging
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.schemas.api_schemas import ParsedListingResponse

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _extract_year(text: str) -> int | None:
    match = re.search(r"\b(19[8-9]\d|20[0-2]\d)\b", text)
    return int(match.group(1)) if match else None


def _extract_price(text: str) -> float | None:
    match = re.search(r"(?:€|EUR)\s*([\d\.,]+)|([\d\.,]+)\s*(?:€|EUR)", text, re.IGNORECASE)
    if match:
        raw = match.group(1) or match.group(2)
        cleaned = raw.replace(".", "").replace(",", ".")
        try:
            val = float(cleaned)
            return val if val > 100 else None
        except ValueError:
            return None
    return None


def _extract_mileage(text: str) -> int | None:
    match = re.search(r"([\d\.,]+)\s*km\b", text, re.IGNORECASE)
    if match:
        raw = match.group(1).replace(".", "").replace(",", "")
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def _parse_json_ld(soup: BeautifulSoup) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                item_type = item.get("@type", "")
                if isinstance(item_type, list):
                    item_type = " ".join(item_type)
                if any(t in str(item_type) for t in ("Vehicle", "Car", "Product", "Offer")):
                    if "brand" in item:
                        brand = item["brand"]
                        extracted["make"] = brand.get("name") if isinstance(brand, dict) else str(brand)
                    if "model" in item:
                        model = item["model"]
                        extracted["model"] = model.get("name") if isinstance(model, dict) else str(model)
                    if "productionDate" in item:
                        extracted["year"] = _extract_year(str(item["productionDate"]))
                    elif "modelDate" in item:
                        extracted["year"] = _extract_year(str(item["modelDate"]))

                    offers = item.get("offers")
                    if isinstance(offers, dict):
                        if "price" in offers:
                            try:
                                extracted["price_eur"] = float(offers["price"])
                            except (ValueError, TypeError):
                                pass
                    elif isinstance(offers, list) and offers:
                        if "price" in offers[0]:
                            try:
                                extracted["price_eur"] = float(offers[0]["price"])
                            except (ValueError, TypeError):
                                pass

                    if "mileageFromOdometer" in item:
                        m = item["mileageFromOdometer"]
                        if isinstance(m, dict) and "value" in m:
                            try:
                                extracted["mileage_km"] = int(m["value"])
                            except (ValueError, TypeError):
                                pass
                        elif isinstance(m, (int, float, str)):
                            try:
                                extracted["mileage_km"] = int(m)
                            except (ValueError, TypeError):
                                pass
        except Exception:
            continue
    return extracted


async def parse_listing_url(url: str) -> ParsedListingResponse:
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Invalid listing URL format: {url}")

    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=12.0) as client:
            response = await client.get(url)
            if response.status_code >= 400:
                raise ValueError(f"Failed to fetch listing: target returned HTTP {response.status_code}")
            html_content = response.text
    except (httpx.HTTPError, Exception) as err:
        raise ValueError(f"Network error while reaching listing URL: {err}")

    soup = BeautifulSoup(html_content, "html.parser")

    raw_title = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        raw_title = title_tag.string.strip()

    og_title = ""
    og_title_meta = soup.find("meta", property="og:title")
    if og_title_meta and og_title_meta.get("content"):
        og_title = str(og_title_meta["content"]).strip()

    full_text = f"{og_title} {raw_title} {soup.get_text()}"

    json_ld_data = _parse_json_ld(soup)

    make = json_ld_data.get("make")
    model = json_ld_data.get("model")
    year = json_ld_data.get("year") or _extract_year(og_title or raw_title)
    price = json_ld_data.get("price_eur") or _extract_price(og_title or raw_title or full_text)
    mileage = json_ld_data.get("mileage_km") or _extract_mileage(og_title or raw_title or full_text)

    if not make or not model:
        title_to_split = og_title or raw_title
        words = title_to_split.split()
        if len(words) >= 2:
            make = make or words[0]
            model = model or " ".join(words[1:3])
        else:
            path_segments = [s for s in parsed_url.path.split("/") if s]
            if len(path_segments) >= 2:
                make = make or path_segments[0].capitalize()
                model = model or path_segments[1].capitalize()

    if not make or not model:
        raise ValueError("Could not extract vehicle make and model from the listing page.")

    return ParsedListingResponse(
        url=url,
        make=str(make).strip().title(),
        model=str(model).strip().title(),
        year=year,
        price_eur=price,
        mileage_km=mileage,
        fuel_type=None,
        raw_title=raw_title or og_title or None,
    )
