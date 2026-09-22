"""
Analytics API server for TrafficLab replay data.

Wraps TrafficAnalytics in a REST API so the voice agent (AssemblyAI tool
calls) can query traffic data over HTTP instead of reading .json.gz files
directly.  Every JSON response is capped at 8 KiB to stay within
AssemblyAI's tool-response limit.
"""
from __future__ import annotations

import gzip
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from trafficlab.visualization.replay_loader import ReplayLoader
except ImportError:
    # Same logic as main's ReplayLoader — fallback until main is merged in.
    class ReplayLoader:
        @staticmethod
        def load(path):
            if str(path).endswith(".gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    return json.load(f)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

# ---------------------------------------------------------------------------
# 8 KiB ceiling for AssemblyAI tool responses
# ---------------------------------------------------------------------------
MAX_RESPONSE_BYTES = 8 * 1024


def _trim_to_limit(payload: dict[str, Any]) -> dict[str, Any]:
    """Shrink *payload* until its JSON encoding fits under MAX_RESPONSE_BYTES.

    Strategy (in order):
    1. Truncate any list called "peaks", "speeding_events", or "objects"
       to its first 20 items.
    2. If still too large, round all floats to 1 decimal place.
    3. If still too large, progressively halve the longest list.
    """
    encoded = json.dumps(payload).encode()
    if len(encoded) <= MAX_RESPONSE_BYTES:
        return payload

    # Step 1 – trim known long lists
    for key in ("peaks", "speeding_events", "objects", "details"):
        if key in payload and isinstance(payload[key], list) and len(payload[key]) > 20:
            payload[key] = payload[key][:20]
            payload[f"{key}_truncated"] = True

    if len(json.dumps(payload).encode()) <= MAX_RESPONSE_BYTES:
        return payload

    # Step 2 – round floats
    _round_floats(payload, decimals=1)
    if len(json.dumps(payload).encode()) <= MAX_RESPONSE_BYTES:
        return payload

    # Step 3 – halve longest list until it fits
    for _ in range(10):
        longest_key = _find_longest_list_key(payload)
        if longest_key is None:
            break
        lst = payload[longest_key]
        half = len(lst) // 2
        if half < 1:
            break
        payload[longest_key] = lst[:half]
        payload[f"{longest_key}_truncated"] = True
        if len(json.dumps(payload).encode()) <= MAX_RESPONSE_BYTES:
            return payload

    return payload


def _round_floats(obj: Any, decimals: int) -> Any:
    if isinstance(obj, float):
        return round(obj, decimals)
    if isinstance(obj, dict):
        return {k: _round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, decimals) for v in obj]
    return obj


def _find_longest_list_key(d: dict[str, Any]) -> Optional[str]:
    best_key, best_len = None, 0
    for k, v in d.items():
        if isinstance(v, list) and len(v) > best_len:
            best_key, best_len = k, len(v)
    return best_key


# ---------------------------------------------------------------------------
# TrafficAnalytics – the analytics engine
# ---------------------------------------------------------------------------

class TrafficAnalytics:
    """Compute analytics over a single TrafficLab replay JSON.

    Instantiate with *data* — the parsed dict from a ``.json.gz`` file (see
    the TrafficLab-Output-Schema for the exact structure).
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.frames: list[dict[str, Any]] = data.get("frames", [])
        self.meta: dict[str, Any] = data.get("meta", {})
        self.location_code: str = data.get("location_code", "unknown")
        self.fps: float = self.meta.get("fps", 30.0)
        self.resolution: list[int] = self.meta.get("resolution", [0, 0])
        self.frame_count: int = len(self.frames)

        # Pre-compute once so every endpoint is O(1).
        self._all_objects = self._collect_objects()
        self._unique_ids: set[Any] = set()
        self._class_counts: Counter[str] = Counter()
        self._speeds: list[float] = []
        self._headings: list[float] = []
        self._per_frame_counts: list[int] = []

        self._build_indices()

    # -- private helpers --------------------------------------------------

    def _collect_objects(self) -> list[dict[str, Any]]:
        """Flatten every frame's objects list into one big list."""
        out: list[dict[str, Any]] = []
        for frame in self.frames:
            for obj in frame.get("objects", []):
                obj["_frame_index"] = frame.get("frame_index", 0)
                out.append(obj)
        return out

    def _build_indices(self) -> None:
        seen: set[Any] = set()
        for frame in self.frames:
            objs = frame.get("objects", [])
            self._per_frame_counts.append(len(objs))
            for obj in objs:
                tid = obj.get("tracked_id")
                key = tid if tid is not None else obj.get("id")
                if key not in seen:
                    seen.add(key)
                    self._class_counts[obj.get("class", "unknown")] += 1
                speed = obj.get("speed_kmh")
                if speed is not None and speed > 0:
                    self._speeds.append(float(speed))
                heading = obj.get("heading")
                if heading is not None and obj.get("have_heading") and not obj.get("default_heading"):
                    self._headings.append(float(heading))
        self._unique_ids = seen

    # -- public analytics methods -----------------------------------------

    def total_vehicles(self) -> int:
        return len(self._unique_ids)

    def counts_by_class(self) -> dict[str, int]:
        return dict(self._class_counts)

    def average_speed(self) -> float:
        return round(sum(self._speeds) / len(self._speeds), 1) if self._speeds else 0.0

    def summary(self) -> dict[str, Any]:
        return {
            "location_code": self.location_code,
            "frame_count": self.frame_count,
            "total_vehicles": self.total_vehicles(),
            "classes": self.counts_by_class(),
            "avg_speed": self.average_speed(),
        }

    def vehicle_count(self) -> dict[str, Any]:
        return {
            "count": self.total_vehicles(),
            "by_class": self.counts_by_class(),
        }

    def speed_stats(self) -> dict[str, Any]:
        if not self._speeds:
            return {"avg": 0, "min": 0, "max": 0, "median": 0}
        s = sorted(self._speeds)
        return {
            "avg": round(sum(s) / len(s), 1),
            "min": round(s[0], 1),
            "max": round(s[-1], 1),
            "median": round(statistics.median(s), 1),
        }

    def peak_hours(self, top_n: int = 5) -> dict[str, Any]:
        """Return the *top_n* frames with the most objects."""
        indexed = list(enumerate(self._per_frame_counts))
        indexed.sort(key=lambda x: x[1], reverse=True)
        peaks = [
            {"frame": self.frames[i].get("frame_index", i), "count": c}
            for i, c in indexed[:top_n]
        ]
        return {"peaks": peaks}

    def turning_patterns(self) -> dict[str, Any]:
        """Bucket headings into cardinal directions."""
        buckets: dict[str, int] = {"north": 0, "east": 0, "south": 0, "west": 0}
        for h in self._headings:
            h = h % 360
            if 315 <= h or h < 45:
                buckets["north"] += 1
            elif 45 <= h < 135:
                buckets["east"] += 1
            elif 135 <= h < 225:
                buckets["south"] += 1
            else:
                buckets["west"] += 1
        return buckets

    def flow_rate(self) -> dict[str, Any]:
        """Vehicles per minute based on unique track appearances."""
        if not self.frames or self.fps <= 0:
            return {"avg_per_minute": 0.0, "peak_per_minute": 0.0}
        duration_minutes = self.frame_count / self.fps / 60.0
        if duration_minutes <= 0:
            return {"avg_per_minute": 0.0, "peak_per_minute": 0.0}

        # Per-minute buckets (each bucket = fps*60 frames)
        frames_per_min = max(1, int(self.fps * 60))
        buckets: list[int] = []
        for start in range(0, self.frame_count, frames_per_min):
            end = min(start + frames_per_min, self.frame_count)
            bucket_ids: set[Any] = set()
            for fi in range(start, end):
                for obj in self.frames[fi].get("objects", []):
                    tid = obj.get("tracked_id") or obj.get("id")
                    bucket_ids.add(tid)
            buckets.append(len(bucket_ids))

        return {
            "avg_per_minute": round(sum(buckets) / len(buckets), 1) if buckets else 0.0,
            "peak_per_minute": max(buckets) if buckets else 0,
        }

    def objects_at_frame(self, frame_idx: int) -> list[dict[str, Any]]:
        """Return trimmed object list for a single frame."""
        if frame_idx < 0 or frame_idx >= self.frame_count:
            raise IndexError(f"frame_index {frame_idx} out of range [0, {self.frame_count - 1}]")
        frame = self.frames[frame_idx]
        return [
            {
                "id": obj.get("id"),
                "tracked_id": obj.get("tracked_id"),
                "class": obj.get("class"),
                "confidence": obj.get("confidence"),
                "speed_kmh": obj.get("speed_kmh"),
                "heading": obj.get("heading"),
            }
            for obj in frame.get("objects", [])
        ]


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="TrafficLab Analytics API", version="1.0.0")

# In-memory state – one loaded replay at a time.
_analytics: Optional[TrafficAnalytics] = None
_meta: dict[str, Any] = {}


class LoadRequest(BaseModel):
    path: str


# -- helpers --------------------------------------------------------------

def _require_loaded() -> TrafficAnalytics:
    if _analytics is None:
        raise HTTPException(status_code=400, detail="No replay loaded. Call POST /load first.")
    return _analytics


# -- endpoints ------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/load")
def load_replay(req: LoadRequest) -> dict[str, Any]:
    global _analytics, _meta
    p = Path(req.path).expanduser()
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {p}")

    try:
        data = ReplayLoader.load(str(p))
    except (OSError, gzip.BadGzipFile, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse replay: {exc}")

    _analytics = TrafficAnalytics(data)
    _meta = {"source": str(p)}
    return {
        "frame_count": _analytics.frame_count,
        "total_objects": len(_analytics._all_objects),
    }


@app.get("/summary")
def summary() -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.summary())


@app.get("/vehicle-count")
def vehicle_count() -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.vehicle_count())


@app.get("/speed-stats")
def speed_stats() -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.speed_stats())


@app.get("/peak-hours")
def peak_hours(top_n: int = 5) -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.peak_hours(top_n=min(top_n, 20)))


@app.get("/turning-patterns")
def turning_patterns() -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.turning_patterns())


@app.get("/flow-rate")
def flow_rate() -> dict[str, Any]:
    a = _require_loaded()
    return _trim_to_limit(a.flow_rate())


@app.get("/object/{frame_idx}")
def object_at_frame(frame_idx: int) -> dict[str, Any]:
    a = _require_loaded()
    try:
        objects = a.objects_at_frame(frame_idx)
    except IndexError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _trim_to_limit({"objects": objects})
