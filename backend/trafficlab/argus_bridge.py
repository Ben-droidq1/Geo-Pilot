"""
Argus ↔ GeoPilot Bridge
========================
Reads Argus camera data and provides a bridge to GeoPilot's inference pipeline.

Usage:
    from trafficlab.argus_bridge import ArgusBridge

    bridge = ArgusBridge()
    cameras = bridge.search(source="caltrans", country="US", has_stream=True)
    cam = cameras[0]
    location_dir = bridge.create_location(cam)
    # location_dir now has a symlink-style reference the pipeline can use
"""

import os
import sys
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Optional

# Add Argus scripts to path so we can import store
_ARGUS_SCRIPTS = str(Path(__file__).resolve().parent.parent / "Argus" / "scripts")
if _ARGUS_SCRIPTS not in sys.path:
    sys.path.insert(0, _ARGUS_SCRIPTS)

try:
    import store as _argus_store
    HAS_ARGUS_STORE = True
except ImportError:
    HAS_ARGUS_STORE = False

# Fallback: read from exported JSON files
_ARGUS_PUBLIC = str(Path(__file__).resolve().parent.parent / "Argus" / "public")

LOCATION_ROOT = str(Path(__file__).resolve().parent.parent / "location")


class ArgusBridge:
    """Bridge between Argus camera data and GeoPilot's inference pipeline."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self._conn = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            if HAS_ARGUS_STORE:
                self._conn = _argus_store.connect(self.db_path or _argus_store.DEFAULT_DB)
            else:
                # Fallback: try to open directly
                db = self.db_path or os.path.join(_ARGUS_SCRIPTS, "data", "cameras.db")
                if not os.path.exists(db):
                    raise FileNotFoundError(
                        f"Argus database not found at {db}. "
                        "Run the Argus scraper first: cd Argus && python scripts/scraper.py --all"
                    )
                self._conn = sqlite3.connect(db)
                self._conn.row_factory = sqlite3.Row
        return self._conn

    def search(
        self,
        source: Optional[str] = None,
        country: Optional[str] = None,
        has_stream: bool = False,
        has_feed: bool = True,
        bbox: Optional[tuple] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search Argus cameras with filters.

        Args:
            source: Filter by source (e.g. "caltrans", "windy", "opencctv")
            country: Filter by ISO country code (e.g. "US", "CA", "GB")
            has_stream: Only cameras with HLS/MP4 stream URLs
            has_feed: Only cameras with a feed URL (image or stream)
            bbox: Bounding box (min_lat, max_lat, min_lon, max_lon)
            limit: Maximum results to return

        Returns:
            List of camera dicts with keys: id, name, city, country, source,
            feed_url, stream_url, feed_type, lon, lat
        """
        conn = self._get_conn()
        query = "SELECT id, name, city, country, source, feed_url, stream_url, feed_type, lon, lat FROM cameras WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)
        if country:
            query += " AND country = ?"
            params.append(country.upper())
        if has_stream:
            query += " AND stream_url IS NOT NULL AND stream_url != ''"
        if has_feed:
            query += " AND feed_url IS NOT NULL AND feed_url != ''"
        if bbox:
            min_lat, max_lat, min_lon, max_lon = bbox
            query += " AND lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?"
            params.extend([min_lat, max_lat, min_lon, max_lon])

        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_camera(self, camera_id: str) -> Optional[dict]:
        """Get a single camera by ID."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT id, name, city, country, source, feed_url, stream_url, feed_type, lon, lat "
            "FROM cameras WHERE id = ?", (camera_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_sources(self) -> list[dict]:
        """Get all sources with camera counts."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT source, COUNT(*) as count FROM cameras GROUP BY source ORDER BY count DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_countries(self) -> list[dict]:
        """Get all countries with camera counts."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT country, COUNT(*) as count FROM cameras "
            "WHERE country IS NOT NULL AND country != '' "
            "GROUP BY country ORDER BY count DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stream_url(self, camera: dict) -> Optional[str]:
        """Get the best playable URL for a camera.
        Prefers stream_url (HLS/MP4), falls back to feed_url (JPEG snapshot).
        """
        stream = (camera.get("stream_url") or "").strip()
        if stream:
            return stream
        feed = (camera.get("feed_url") or "").strip()
        if feed:
            return feed
        return None

    def create_location(self, camera: dict, footage_url: Optional[str] = None) -> str:
        """Create a GeoPilot location folder for an Argus camera.

        Args:
            camera: Camera dict from search() or get_camera()
            footage_url: Override URL (defaults to camera's stream/feed URL)

        Returns:
            Path to the created location directory
        """
        cam_id = camera["id"]
        # Use a safe location code from the camera ID
        loc_code = cam_id.replace("/", "_").replace(" ", "_")[:30]

        loc_dir = os.path.join(LOCATION_ROOT, loc_code)
        footage_dir = os.path.join(loc_dir, "footage")
        os.makedirs(footage_dir, exist_ok=True)

        # Write camera metadata
        meta_path = os.path.join(loc_dir, "argus_camera.json")
        with open(meta_path, "w") as f:
            json.dump({
                "camera_id": cam_id,
                "name": camera.get("name", ""),
                "city": camera.get("city", ""),
                "country": camera.get("country", ""),
                "source": camera.get("source", ""),
                "lon": camera.get("lon"),
                "lat": camera.get("lat"),
                "feed_url": camera.get("feed_url", ""),
                "stream_url": camera.get("stream_url", ""),
                "feed_type": camera.get("feed_type", ""),
            }, f, indent=2)

        # Write a README
        readme_path = os.path.join(loc_dir, "README.md")
        url = footage_url or self.get_stream_url(camera)
        with open(readme_path, "w") as f:
            f.write(f"# {camera.get('name', cam_id)}\n\n")
            f.write(f"- **Source:** {camera.get('source', 'unknown')}\n")
            f.write(f"- **Location:** {camera.get('city', '')}, {camera.get('country', '')}\n")
            f.write(f"- **Coordinates:** {camera.get('lat')}, {camera.get('lon')}\n")
            f.write(f"- **Feed URL:** {camera.get('feed_url', 'N/A')}\n")
            f.write(f"- **Stream URL:** {camera.get('stream_url', 'N/A')}\n")
            f.write(f"- **Feed Type:** {camera.get('feed_type', 'N/A')}\n\n")
            f.write(f"## Pipeline URL\n\n```\n{url}\n```\n")

        return loc_dir

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# ─────────────────────────────────────────────────────────
# CLI interface for quick testing
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Argus ↔ GeoPilot Bridge")
    sub = parser.add_subparsers(dest="cmd")

    # search
    sp = sub.add_parser("search", help="Search cameras")
    sp.add_argument("--source", help="Filter by source")
    sp.add_argument("--country", help="Filter by country code")
    sp.add_argument("--stream", action="store_true", help="Only cameras with streams")
    sp.add_argument("--limit", type=int, default=10)
    sp.add_argument("--json", action="store_true", help="Output as JSON")

    # sources
    sub.add_parser("sources", help="List all sources")

    # countries
    sub.add_parser("countries", help="List all countries")

    # create-location
    cp = sub.add_parser("create-location", help="Create a location folder for a camera")
    cp.add_argument("camera_id", help="Camera ID (e.g. caltrans_d01_42)")

    args = parser.parse_args()
    bridge = ArgusBridge()

    if args.cmd == "search":
        cams = bridge.search(source=args.source, country=args.country, has_stream=args.stream, limit=args.limit)
        if args.json:
            print(json.dumps(cams, indent=2))
        else:
            for c in cams:
                stream = "HLS" if c.get("stream_url") else "IMG"
                print(f"  [{stream}] {c['id']:40s}  {c.get('name','')[:40]:40s}  {c.get('source','')}")
            print(f"\n  {len(cams)} cameras found")

    elif args.cmd == "sources":
        for s in bridge.get_sources():
            print(f"  {s['source']:30s}  {s['count']:>6,}")

    elif args.cmd == "countries":
        for c in bridge.get_countries():
            print(f"  {c['country']:5s}  {c['count']:>6,}")

    elif args.cmd == "create-location":
        cam = bridge.get_camera(args.camera_id)
        if not cam:
            print(f"Camera not found: {args.camera_id}")
            sys.exit(1)
        loc = bridge.create_location(cam)
        print(f"Location created: {loc}")

    else:
        parser.print_help()

    bridge.close()
