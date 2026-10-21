from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/evadvisor"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    EV_CATALOG_API_KEY: str = ""
    EV_CATALOG_API_URL: str = "https://api.api-ninjas.com/v1/electricvehicle"
    # Bundled OpenEV Data dataset (CSV) used as the primary, offline EV catalog.
    EV_DATASET_PATH: str = "data/open-ev-data.csv"

    # Conventional (ICE) car catalog. Both endpoints below are available on the API Ninjas free tier.
    CAR_CATALOG_API_KEY: str = ""
    CAR_FACETS_API_URL: str = "https://api.api-ninjas.com/v2/carfacets"
    CAR_CATALOG_API_URL: str = "https://api.api-ninjas.com/v1/cars"

    # Used-car valuation via RapidAPI's "AutoScout24 Scraper" (scrapeunblocker).
    # The estimate is derived from comparable AutoScout24.it listings fetched per request.
    RAPIDAPI_API_KEY: str = ""
    RAPIDAPI_AS24_URL: str = "https://autoscout24-scraper.p.rapidapi.com/get_page_source"
    AUTOSCOUT24_BASE_URL: str = "https://www.autoscout24.it"

    # Live Energy & Fuel Price Feeds (MISE / MIMIT Open Data API & Fallbacks)
    MISE_FUEL_PRICES_API_URL: str = "https://www.mimit.gov.it/images/exportopenData/prezzi_alle_pompe.csv"
    DEFAULT_DIESEL_PRICE: float = 1.80
    DEFAULT_PETROL_PRICE: float = 1.85
    DEFAULT_LPG_PRICE: float = 0.75
    DEFAULT_CNG_PRICE: float = 1.35
    DEFAULT_ELECTRICITY_HOME_PRICE: float = 0.25

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
