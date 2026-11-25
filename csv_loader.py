import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()
    for path in paths:
        name = os.path.basename(path)
        with open(path, encoding="utf-8", newline="") as f:
            lines = [ln.rstrip("\r") for ln in f.read().split("\n")]
        for line_no, line in enumerate(lines, start=1):
            if line_no == 1:
                continue
            stripped = line.strip()
            if stripped == "" or stripped.startswith("#"):
                continue
            fields = next(csv.reader([line]), [])
            code = validate_row(fields, airports)
            if code is None:
                record = to_record(fields)
                key = (record["flight_id"], record["departure_datetime"])
                if key in seen:
                    code = "DUPLICATE_FLIGHT"
                else:
                    seen.add(key)
                    records.append(record)
            if code is not None:
                errors.append(f"{name}:{line_no}: {code} | {line}")
    return records, errors
