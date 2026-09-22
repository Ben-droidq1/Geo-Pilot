"""Shared helpers for GeoPilot Vercel serverless functions (stdlib only).

NOT a route itself (leading underscore) — imported by api/*.py handlers.
Mirrors the search logic in backend/voice_agent_server.py, but reads the
camera database shipped with the frontend (frontend/public) so it works
on Vercel with no extra backend process.

On-disk schema (columnar, to keep the 229k-camera DB small):
  frontend/public/cameras.core.json   — count, lat[], lon[], live[], src[],
                                        cc[], ft[], srcDict, ccDict, ftDict
  frontend/public/cameras.labels.json — name[], city[], cityDict
  frontend/public/cameras.detail/N.json — per-chunk stream/feed URLs
"""
import json
import math
import os

_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "public"),
    os.path.join(os.getcwd(), "frontend", "public"),
    "/vercel/path0/frontend/public",
]

_data = None
_labels = None
_stream_cache = {}


def public_dir():
    for p in _CANDIDATES:
        if os.path.isdir(p):
            return p
    return _CANDIDATES[0]


def _load():
    global _data, _labels
    if _data is not None:
        return
    base = public_dir()
    try:
        with open(os.path.join(base, "cameras.core.json"), encoding="utf-8") as f:
            _data = json.load(f)
    except (OSError, ValueError):
        _data = {}
    try:
        with open(os.path.join(base, "cameras.labels.json"), encoding="utf-8") as f:
            _labels = json.load(f)
    except (OSError, ValueError):
        _labels = {}


COUNTRY_NAME_TO_CODE = {
    "united states": "us", "usa": "us", "america": "us",
    "united kingdom": "gb", "uk": "gb", "england": "gb",
    "south korea": "kr", "korea": "kr",
    "japan": "jp", "china": "cn", "india": "in",
    "germany": "de", "france": "fr", "spain": "es", "italy": "it",
    "brazil": "br", "mexico": "mx", "canada": "ca", "australia": "au",
    "russia": "ru", "turkey": "tr", "thailand": "th", "vietnam": "vn",
    "philippines": "ph", "indonesia": "id", "malaysia": "my",
    "netherlands": "nl", "belgium": "be", "sweden": "se", "norway": "no",
    "finland": "fi", "denmark": "dk", "poland": "pl", "portugal": "pt",
    "greece": "gr", "israel": "il", "egypt": "eg", "south africa": "za",
    "nigeria": "ng", "kenya": "ke", "argentina": "ar", "chile": "cl",
    "colombia": "co", "peru": "pe", "new zealand": "nz", "ireland": "ie",
    "singapore": "sg", "taiwan": "tw", "hong kong": "hk",
    "hawaii": "us", "florida": "us", "california": "us", "texas": "us",
    "new york": "us", "miami": "us", "los angeles": "us",
}

CONTENT_SOURCE_MAP = {
    "beach": ["surf", "beach", "ocean", "sea", "coast", "wave", "pier"],
    "ocean": ["surf", "beach", "ocean", "sea", "coast", "wave"],
    "sea": ["surf", "beach", "ocean", "sea", "coast"],
    "highway": ["highway", "freeway", "motorway", "expressway", "traffic"],
    "intersection": ["intersection", "crossing", "junction", "traffic"],
    "airport": ["airport", "airfield", "runway", "terminal"],
    "mountain": ["mountain", "alpine", "ski", "summit", "slope"],
    "harbor": ["harbor", "harbour", "port", "marina", "dock", "pier"],
    "city": ["downtown", "city", "urban", "street", "road"],
    "bridge": ["bridge", "overpass"],
    "tunnel": ["tunnel"],
    "parking": ["parking", "garage", "lot"],
    "train": ["train", "railway", "station", "metro"],
    "casino": ["casino"],
    "zoo": ["zoo", "safari", "wildlife"],
    "ski": ["ski", "snow", "mountain", "slope", "resort"],
    "campus": ["campus", "university", "college", "school"],
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_stream_url(cam_index):
    """Stream/feed URL for a camera index via its detail chunk (cached)."""
    _load()
    if not _data or cam_index < 0 or cam_index >= _data.get("count", 0):
        return None
    chunk_num = cam_index // _data.get("chunk", 1000)
    if chunk_num not in _stream_cache:
        path = os.path.join(public_dir(), f"cameras.detail/{chunk_num}.json")
        try:
            with open(path, encoding="utf-8") as f:
                _stream_cache[chunk_num] = json.load(f)
        except (OSError, ValueError):
            _stream_cache[chunk_num] = {}
    chunk = _stream_cache[chunk_num]
    local_idx = cam_index - chunk.get("from", chunk_num * _data.get("chunk", 1000))
    for key in ("stream", "feed"):
        arr = chunk.get(key, [])
        if 0 <= local_idx < len(arr) and arr[local_idx]:
            return arr[local_idx]
    return None


def search_cameras(query="", lat=None, lon=None, radius_km=50.0, limit=10):
    _load()
    if not _data:
        return []
    try:
        limit = max(1, min(int(limit), 50))
    except (TypeError, ValueError):
        limit = 10
    try:
        radius_km = float(radius_km or 50.0)
    except (TypeError, ValueError):
        radius_km = 50.0

    d, labels = _data, _labels or {}
    names = labels.get("name", [])
    cities = labels.get("city", [])
    city_dict = labels.get("cityDict", [])
    results = []
    q = (query or "").strip().lower()

    for i in range(d.get("count", 0)):
        cam_lat = d["lat"][i]
        cam_lon = d["lon"][i]
        country = d["ccDict"][d["cc"][i]]
        source = d["srcDict"][d["src"][i]]
        name = names[i] if i < len(names) else ""
        city_idx = cities[i] if i < len(cities) else 0
        city = city_dict[city_idx] if city_idx < len(city_dict) else ""

        if lat is not None and lon is not None:
            try:
                if haversine_km(float(lat), float(lon), cam_lat, cam_lon) > radius_km:
                    continue
            except (TypeError, ValueError):
                pass

        if q:
            searchable = f"{name} {city} {country} {source}".lower()
            matched = q in searchable or any(w in searchable for w in q.split())
            if not matched:
                for country_name, code in COUNTRY_NAME_TO_CODE.items():
                    if country_name in q and country.lower() == code:
                        matched = True
                        break
            if not matched:
                for keyword, sources in CONTENT_SOURCE_MAP.items():
                    if keyword in q and any(s in searchable for s in sources):
                        matched = True
                        break
            if not matched:
                continue

        results.append(
            {
                "index": i,
                "name": name,
                "city": city,
                "country": country,
                "lat": cam_lat,
                "lon": cam_lon,
                "live": d["live"][i] == 1,
                "source": source,
            }
        )

    if lat is not None and lon is not None:
        try:
            for r in results:
                r["distance_km"] = round(haversine_km(float(lat), float(lon), r["lat"], r["lon"]), 1)
            results.sort(key=lambda x: (not x["live"], x.get("distance_km", 9999)))
        except (TypeError, ValueError):
            results.sort(key=lambda x: not x["live"])
    else:
        results.sort(key=lambda x: not x["live"])
    return results[:limit]
