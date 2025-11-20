"""Command-line helper to inspect TomTom parking availability."""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, Sequence

# Ensure src package is importable when running from repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parking_service import (  # type: ignore[import-not-found]
    MissingApiKeyError,
    ParkingAreaInfo,
    UnknownParkingAreaError,
    fetch_parking_availability,
    list_parking_areas,
)


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--area",
        default="melbourne_cbd",
        help="Parking area key (default: melbourne_cbd). Use --list-areas to see options.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit results (default: 10)",
    )
    parser.add_argument(
        "--list-areas",
        action="store_true",
        help="List configured parking areas and exit.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_parking_areas(areas: Iterable[ParkingAreaInfo]) -> None:
    print("Configured parking areas:")
    for area in areas:
        print(f"- {area.key}: {area.display_name} (radius {area.radius_m}m)")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(list(argv) if argv is not None else sys.argv[1:])

    if args.list_areas:
        print_parking_areas(list_parking_areas())
        return 0

    try:
        results = fetch_parking_availability(args.area, limit=args.limit)
    except UnknownParkingAreaError:
        print(f"Unknown area '{args.area}'. Use --list-areas to see valid keys.")
        return 2
    except MissingApiKeyError:
        print("TomTom API key missing. Set TOMTOM_API_KEY in your environment.")
        return 3
    except Exception as exc:  # noqa: BLE001
        print(f"Parking lookup failed: {exc}")
        return 4

    if not results:
        print("No parking locations returned.")
        return 0

    print(f"Top {len(results)} parking locations for area '{args.area}':")
    for item in results:
        name = item.get("name") or item.get("id") or "Unnamed location"
        available = item.get("available")
        total = item.get("total")
        status = item.get("status") or "UNKNOWN"
        address = item.get("address") or "Address unavailable"
        print(f"- {name}: {status} ({available}/{total} free)\n  {address}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
