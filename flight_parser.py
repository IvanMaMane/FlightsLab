import argparse
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB124"
FIRST_NAME = "Ivan"
LAST_NAME = "Kuzanov"


class RunError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Flight schedule parser and query tool")
    parser.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    parser.add_argument("-d", metavar="FOLDER", help="parse every .csv file in a folder")
    parser.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list file")
    parser.add_argument("-o", metavar="FILE", help="output path for the JSON database")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", metavar="FOLDER", help="folder for the response file")
    return parser


def load_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        raise RunError(f"cannot read {path}: {e.strerror}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RunError(f"{path} is not valid JSON")


def collect_csv_paths(args) -> list[str]:
    if args.i:
        if not os.path.isfile(args.i):
            raise RunError(f"file not found: {args.i}")
        return [args.i]
    if not os.path.isdir(args.d):
        raise RunError(f"folder not found: {args.d}")
    try:
        names = sorted(os.listdir(args.d))
    except OSError as e:
        raise RunError(f"cannot read folder {args.d}: {e.strerror}")
    paths = [os.path.join(args.d, n) for n in names
             if n.endswith(".csv") and os.path.isfile(os.path.join(args.d, n))]
    if not paths:
        raise RunError(f"no .csv files in {args.d}")
    return paths


def parse_csvs(args) -> list[dict]:
    paths = collect_csv_paths(args)
    try:
        airports = load_airports(args.a)
    except (OSError, UnicodeDecodeError):
        raise RunError(f"cannot read airport file: {args.a}")
    try:
        records, errors = parse_files(paths, airports)
    except (OSError, UnicodeDecodeError) as e:
        raise RunError(f"cannot read CSV file: {e}")

    out_path = args.o or "db.json"
    out_dir = os.path.dirname(out_path) or "."
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        raise RunError(f"cannot create directory {out_dir}: {e.strerror}")
    log_path = os.path.join(out_dir, "errors.log")
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    except OSError as e:
        raise RunError(f"cannot write {log_path}: {e.strerror}")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    try:
        logger.info("parsed %d file(s): %d valid, %d invalid", len(paths), len(records), len(errors))
        for message in errors:
            logger.warning(message)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except OSError as e:
            logger.error("cannot write %s", out_path)
            raise RunError(f"cannot write {out_path}: {e.strerror}")
    finally:
        logger.removeHandler(handler)
        handler.close()
    print(f"{len(records)} valid flights, {len(errors)} invalid rows")
    return records


def load_db(path: str) -> list[dict]:
    db = load_json(path)
    if not isinstance(db, list) or not all(isinstance(r, dict) for r in db):
        raise RunError(f"{path} must contain a JSON array of objects")
    return db


def write_response(db: list[dict], args) -> None:
    queries = load_json(args.q)
    if isinstance(queries, list):
        if not all(isinstance(q, dict) for q in queries):
            raise RunError(f"{args.q} must contain a query object or an array of query objects")
    elif not isinstance(queries, dict):
        raise RunError(f"{args.q} must contain a query object or an array of query objects")
    responses = run_queries(db, queries)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
    resp_dir = args.r or "."
    try:
        os.makedirs(resp_dir, exist_ok=True)
    except OSError as e:
        raise RunError(f"cannot create directory {resp_dir}: {e.strerror}")
    path = os.path.join(resp_dir, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2)
    except OSError as e:
        raise RunError(f"cannot write {path}: {e.strerror}")
    print(f"{len(responses)} queries answered, written to {path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        sources = [s for s in (args.i, args.d, args.j) if s is not None]
        if len(sources) == 0:
            parser.error("one of -i, -d or -j is required")
        if len(sources) > 1:
            parser.error("only one of -i, -d or -j may be used")
        if (args.i or args.d) and not args.a:
            parser.error("-a is required with -i and -d")
        if args.j and args.o:
            parser.error("-o cannot be used with -j")
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    try:
        if args.j:
            db = load_db(args.j)
        else:
            db = parse_csvs(args)
        if args.q:
            write_response(db, args)
    except RunError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
