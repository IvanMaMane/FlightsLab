import math
import re
from datetime import datetime

AIRPORT_RE = re.compile(r"[A-Z]{3}")
FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}")
DATETIME_FMT = "%Y-%m-%d %H:%M"


def load_airports(path: str) -> set[str]:
    airports = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if code and not code.startswith("#"):
                airports.add(code)
    return airports


def parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, DATETIME_FMT)
    except ValueError:
        return None


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"
    fields = [f.strip() for f in fields]
    if any(f == "" for f in fields):
        return "MISSING_FIELD"
    flight_id, origin, destination, dep, arr, price = fields
    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
    dep_dt = parse_datetime(dep)
    if dep_dt is None:
        return "INVALID_DEPARTURE"
    arr_dt = parse_datetime(arr)
    if arr_dt is None:
        return "INVALID_ARRIVAL"
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"
    try:
        value = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(value):
        return "INVALID_PRICE"
    if value <= 0:
        return "NON_POSITIVE_PRICE"
    return None


def to_record(fields: list[str]) -> dict:
    fields = [f.strip() for f in fields]
    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5]),
    }
