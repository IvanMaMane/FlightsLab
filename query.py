from validator import parse_datetime

STRING_KEYS = ("flight_id", "origin", "destination")
DATETIME_KEYS = ("departure_datetime", "arrival_datetime")
NUMBER_KEYS = ("price", "min_price")
RECORD_KEYS = STRING_KEYS + DATETIME_KEYS + ("price",)
ALLOWED_KEYS = set(STRING_KEYS) | set(DATETIME_KEYS) | set(NUMBER_KEYS) | {"sort_by", "order", "limit"}


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_valid_query(query) -> bool:
    if not isinstance(query, dict):
        return False
    for key, value in query.items():
        if key not in ALLOWED_KEYS:
            return False
        if key in STRING_KEYS and not isinstance(value, str):
            return False
        if key in DATETIME_KEYS and (not isinstance(value, str) or parse_datetime(value) is None):
            return False
        if key in NUMBER_KEYS and not is_number(value):
            return False
        if key == "sort_by" and value not in RECORD_KEYS:
            return False
        if key == "order" and value not in ("asc", "desc"):
            return False
        if key == "limit" and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            return False
    return True


def matches(flight: dict, query: dict) -> bool:
    for key in STRING_KEYS:
        if key in query and flight[key] != query[key]:
            return False
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and flight["price"] > query["price"]:
        return False
    if "min_price" in query and flight["price"] < query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
    result = [flight for flight in db if matches(flight, query)]
    if "sort_by" in query:
        key = query["sort_by"]
        reverse = query.get("order") == "desc"
        result = sorted(result, key=lambda f: f[key], reverse=reverse)
    if "limit" in query:
        result = result[:query["limit"]]
    return {"query": query, "matches": result}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, q) for q in queries]
