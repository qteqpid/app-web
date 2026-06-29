#!/usr/bin/env python3
import argparse
import json
import os
import re
import time
import uuid
from typing import Any, Dict, List, Optional

import requests


API_BASE = "https://de1.api.radio-browser.info"
GEOCODE_BASE = "https://nominatim.openstreetmap.org"
DEFAULT_GENRE = "Music"


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def pick_genre(tags: str) -> str:
    if not tags:
        return ""
    parts = [p.strip() for p in tags.split(",") if p.strip()]
    return parts[0] if parts else ""


def fallback_id(name: str, city: str, country: str) -> str:
    seed = f"{name}|{city}|{country}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def best_match(
    candidates: List[Dict[str, Any]],
    name: str,
    city: str,
    country: str,
) -> Optional[Dict[str, Any]]:
    target_name = normalize(name)
    target_city = normalize(city)
    target_country = normalize(country)

    best = None
    best_score = -1
    for c in candidates:
        score = 0
        cand_name = normalize(c.get("name", ""))
        cand_city = normalize(c.get("city", ""))
        cand_country = normalize(c.get("country", ""))

        if cand_name == target_name:
            score += 5
        elif target_name and (target_name in cand_name or cand_name in target_name):
            score += 3

        if target_country and cand_country == target_country:
            score += 3
        if target_city and cand_city == target_city:
            score += 2

        if c.get("latitude") not in (None, 0, "0") and c.get("longitude") not in (None, 0, "0"):
            score += 1

        if score > best_score:
            best_score = score
            best = c

    return best


def fetch_candidates_by_url(session: requests.Session, url: str) -> List[Dict[str, Any]]:
    params = {"url": url}
    resp = session.get(f"{API_BASE}/json/stations/byurl", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_candidates(session: requests.Session, name: str, country: str) -> List[Dict[str, Any]]:
    params = {"name": name, "limit": 20}
    if country:
        params["country"] = country
    resp = session.get(f"{API_BASE}/json/stations/search", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def geocode_city(
    session: requests.Session,
    city: str,
    country: str,
    geo_cache: Dict[str, Optional[Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    if not city:
        return None
    cache_key = f"{city}|{country}".strip()
    if cache_key in geo_cache:
        return geo_cache[cache_key]

    query = f"{city}, {country}" if country else city
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "radio-info-filler/1.0"}
    resp = session.get(f"{GEOCODE_BASE}/search", params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        geo_cache[cache_key] = None
        return None
    geo_cache[cache_key] = data[0]
    return data[0]


def geocode_country(
    session: requests.Session,
    country: str,
    geo_cache: Dict[str, Optional[Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    if not country:
        return None
    cache_key = f"country|{country}".strip()
    if cache_key in geo_cache:
        return geo_cache[cache_key]

    params = {"q": country, "format": "json", "limit": 1}
    headers = {"User-Agent": "radio-info-filler/1.0"}
    resp = session.get(f"{GEOCODE_BASE}/search", params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        geo_cache[cache_key] = None
        return None
    geo_cache[cache_key] = data[0]
    return data[0]


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def enrich_records(
    records: List[Dict[str, Any]],
    geo_cache: Dict[str, Optional[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    session = requests.Session()
    cache: Dict[str, Optional[Dict[str, Any]]] = {}
    enriched: List[Dict[str, Any]] = []

    for idx, row in enumerate(records, start=1):
        name = str(row.get("name", "")).strip()
        city = str(row.get("city", "")).strip()
        country = str(row.get("country", "")).strip()
        url = row.get("url")

        cache_key = f"{name}|{city}|{country}"
        match = cache.get(cache_key)
        if match is None and cache_key not in cache:
            try:
                candidates = []
                if url:
                    try:
                        candidates = fetch_candidates_by_url(session, str(url))
                    except Exception:
                        candidates = []
                if not candidates:
                    candidates = fetch_candidates(session, name, country)
                match = best_match(candidates, name, city, country)
                cache[cache_key] = match
                time.sleep(0.2)
            except Exception:
                cache[cache_key] = None
                match = None

        station_id = match.get("stationuuid") if match else None
        genre = pick_genre(match.get("tags", "")) if match else ""
        lat = match.get("latitude") if match else None
        lng = match.get("longitude") if match else None

        if is_missing(lat) or is_missing(lng):
            try:
                geo = geocode_city(session, city, country, geo_cache)
                if geo:
                    lat = lat or geo.get("lat")
                    lng = lng or geo.get("lon")
                    time.sleep(0.2)
            except Exception:
                pass

        if is_missing(lat) or is_missing(lng):
            try:
                geo = geocode_country(session, country, geo_cache)
                if geo:
                    lat = lat or geo.get("lat")
                    lng = lng or geo.get("lon")
                    time.sleep(0.2)
            except Exception:
                pass

        if not station_id:
            station_id = fallback_id(name, city, country)

        record = {
            "id": station_id,
            "name": name,
            "url": url,
            "genre": genre or DEFAULT_GENRE,
            "city": city,
            "country": country,
            "lat": lat,
            "lng": lng,
        }

        missing_fields = [k for k, v in record.items() if is_missing(v)]
        if missing_fields:
            print(
                "Drop record (missing fields: "
                + ", ".join(missing_fields)
                + f"): {name} | {city} | {country}"
            )
        else:
            enriched.append(record)

        if idx % 20 == 0:
            print(f"Processed {idx}/{len(records)}")

    return enriched


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill radio station info (lat, lng, genre, id) in a JSON file."
    )
    parser.add_argument("input_file", help="Input JSON file path")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        raise ValueError("Input JSON must be a list of station objects.")

    cache_path = os.path.join(os.path.dirname(__file__), "geocode_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                geo_cache = json.load(f)
        except Exception:
            geo_cache = {}
    else:
        geo_cache = {}

    enriched = enrich_records(records, geo_cache)

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(geo_cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    with open(args.input_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=4)

    print(f"Updated {args.input_file} with {len(enriched)} records.")


if __name__ == "__main__":
    main()
