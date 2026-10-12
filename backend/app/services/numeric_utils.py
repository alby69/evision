import re


def parse_number(value: object) -> float | None:
    """Extracts the first number from API values like "200 kW DC" or "66.0 kWh".

    Returns None for non-numeric values such as "No Data" or premium-only messages.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:[.,]\d+)?", value.replace(",", "."))
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
    return None


def parse_int(value: object) -> int | None:
    """Extracts an integer year from values like "2025" or 2025."""
    number = parse_number(value)
    return int(number) if number is not None else None
