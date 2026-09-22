import math
from statistics import median


_INTENT_ALIASES = {
    "count": "vehicle_count",
    "how_many": "vehicle_count",
    "how_many_vehicles": "vehicle_count",
    "volume": "vehicle_count",
    "traffic_volume": "vehicle_count",
    "vehicles": "vehicle_count",
    "by_class": "vehicle_count_by_class",
    "breakdown": "vehicle_count_by_class",
    "composition": "vehicle_count_by_class",
    "class_breakdown": "vehicle_count_by_class",
    "speed": "speed_stats",
    "how_fast": "speed_stats",
    "average_speed": "speed_stats",
    "avg_speed": "speed_stats",
    "fastest": "speed_stats",
    "distribution": "speed_distribution",
    "histogram": "speed_distribution",
    "speed_histogram": "speed_distribution",
    "peak": "peak_frames",
    "busiest": "peak_frames",
    "busiest_moments": "peak_frames",
    "busiest_frames": "peak_frames",
    "congestion": "peak_frames",
    "jam": "peak_frames",
    "heading": "heading_distribution",
    "direction": "heading_distribution",
    "which_way": "heading_distribution",
    "where_going": "heading_distribution",
    "flow": "traffic_flow_rate",
    "rate": "traffic_flow_rate",
    "flow_rate": "traffic_flow_rate",
    "throughput": "traffic_flow_rate",
    "summary": "full_summary",
    "all": "full_summary",
    "everything": "full_summary",
    "overview": "full_summary",
}


def _to_float(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(out) or math.isinf(out):
        return None
    return out


def _to_int(value, default=None):
    if value is None or isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _norm_class(value):
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    return text if text else "unknown"


def _is_valid(value):
    return bool(value) and value != "false" and value != "False"


class TrafficAnalytics:
    """Aggregates a raw replay JSON dict (as produced by the inference
    pipeline / replay_writer) into traffic statistics.

    Counting rules:
      - vehicle_count() counts UNIQUE vehicles, keyed by tracked_id
        (objects without a tracked_id are counted once each).
      - vehicle_count_by_class() returns a flat {class: unique_count} dict,
        e.g. {"car": 12, "truck": 3}. Per-frame detection volume is
        available via detection_count() and full_summary()["total_detections"].

    Every method returns zeros/empty containers on missing or malformed
    data instead of raising.
    """

    def __init__(self, replay_data: dict):
        if not isinstance(replay_data, dict):
            replay_data = {}
        self.data = replay_data

        frames = replay_data.get("frames")
        if not isinstance(frames, list):
            frames = []

        meta = replay_data.get("meta")
        if not isinstance(meta, dict):
            meta = {}
        fps = _to_float(meta.get("fps"))
        self.fps = fps if fps is not None and fps > 0 else None

        self.total_frames = len(frames)
        self._frame_indices = []
        self._class_totals = {}
        self._track_classes = {}
        self._track_speeds = {}
        self._track_headings = {}
        self._track_first_frame = {}
        self._speed_samples = {}
        self._heading_samples = {}
        self._frame_counts = {}

        for idx, frame in enumerate(frames):
            if not isinstance(frame, dict):
                self._frame_indices.append(idx)
                self._frame_counts[idx] = 0
                continue
            fi = _to_int(frame.get("frame_index"), idx)
            if fi is None:
                fi = idx
            self._frame_indices.append(fi)
            objects = frame.get("objects")
            if not isinstance(objects, list):
                objects = []
            self._frame_counts[fi] = len(objects)

            for obj in objects:
                if not isinstance(obj, dict):
                    continue
                cls = _norm_class(obj.get("class"))
                self._class_totals[cls] = self._class_totals.get(cls, 0) + 1

                tid = obj.get("tracked_id")
                if tid is None:
                    key = ("__untracked__", fi, id(obj))
                else:
                    key = tid
                if key not in self._track_classes:
                    self._track_classes[key] = cls
                    self._track_first_frame[key] = fi

                have = _is_valid(obj.get("have_heading")) or _to_float(obj.get("speed_kmh")) is not None and _to_float(obj.get("heading")) is not None
                speed = _to_float(obj.get("speed_kmh")) if have else None
                if speed is not None and speed >= 0:
                    self._speed_samples.setdefault(key, []).append(speed)

                heading = _to_float(obj.get("heading"))
                if have and heading is not None:
                    self._heading_samples.setdefault(key, []).append(heading % 360.0)

        for key, samples in self._speed_samples.items():
            self._track_speeds[key] = sum(samples) / len(samples)
        for key, samples in self._heading_samples.items():
            self._track_headings[key] = self._mean_heading(samples)

        self.duration_seconds = (
            self.total_frames / self.fps if self.fps and self.total_frames else None
        )

    @staticmethod
    def _mean_heading(samples):
        if not samples:
            return None
        x = sum(math.cos(math.radians(h)) for h in samples)
        y = sum(math.sin(math.radians(h)) for h in samples)
        if abs(x) < 1e-9 and abs(y) < 1e-9:
            return None
        return math.degrees(math.atan2(y, x)) % 360.0

    @staticmethod
    def _cardinal(deg):
        return ["E", "SE", "S", "SW", "W", "NW", "N", "NE"][int((deg + 22.5) % 360 // 45)]

    @staticmethod
    def _quadrant(deg):
        return ["E", "S", "W", "N"][int((deg + 45.0) % 360 // 90)]

    def _match_class(self, key, class_filter):
        if class_filter is None:
            return True
        want = str(class_filter).strip().lower()
        parts = [p.strip().lower() for p in want.split(",") if p.strip()]
        if not parts:
            return True
        cls = self._track_classes.get(key, "unknown")
        return any(cls == p or p in cls or cls in p for p in parts)

    def _filtered_keys(self, class_filter=None):
        return [k for k in self._track_classes if self._match_class(k, class_filter)]

    def vehicle_count(self, class_filter=None) -> int:
        return len(self._filtered_keys(class_filter))

    def detection_count(self, class_filter=None) -> int:
        if class_filter is None:
            return sum(self._class_totals.values())
        want = str(class_filter).strip().lower()
        return sum(n for cls, n in self._class_totals.items() if cls == want or want in cls or cls in want)

    def vehicle_count_by_class(self) -> dict:
        unique = {}
        for cls in self._track_classes.values():
            unique[cls] = unique.get(cls, 0) + 1
        return dict(sorted(unique.items()))

    def speed_stats(self, class_filter=None) -> dict:
        values = [self._track_speeds[k] for k in self._filtered_keys(class_filter) if k in self._track_speeds]
        if not values:
            return {
                "avg_kmh": 0.0, "min_kmh": 0.0, "max_kmh": 0.0,
                "median_kmh": 0.0, "sample_count": 0,
            }
        return {
            "avg_kmh": round(sum(values) / len(values), 2),
            "min_kmh": round(min(values), 2),
            "max_kmh": round(max(values), 2),
            "median_kmh": round(median(values), 2),
            "sample_count": len(values),
        }

    def speed_distribution(self, buckets=10) -> list:
        try:
            n_buckets = int(buckets)
        except (TypeError, ValueError):
            n_buckets = 10
        n_buckets = max(1, min(n_buckets, 100))
        values = sorted(self._track_speeds.values())
        if not values:
            return []
        lo, hi = values[0], values[-1]
        if hi - lo < 1e-9:
            return [{
                "min_kmh": round(lo, 2),
                "max_kmh": round(hi, 2),
                "count": len(values),
                "percent": 100.0,
            }]
        step = (hi - lo) / n_buckets
        counts = [0] * n_buckets
        for v in values:
            counts[min(int((v - lo) / step), n_buckets - 1)] += 1
        total = len(values)
        return [
            {
                "min_kmh": round(lo + i * step, 2),
                "max_kmh": round(lo + (i + 1) * step, 2),
                "count": c,
                "percent": round(100.0 * c / total, 1),
            }
            for i, c in enumerate(counts)
        ]

    def peak_frames(self, top_n=5) -> list:
        try:
            n = int(top_n)
        except (TypeError, ValueError):
            n = 5
        n = max(1, n)
        ordered = sorted(self._frame_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        result = []
        for fi, count in ordered[:n]:
            if count <= 0:
                break
            result.append({
                "frame_index": fi,
                "vehicle_count": count,
                "timestamp_s": round(fi / self.fps, 2) if self.fps else None,
            })
        return result

    def heading_distribution(self) -> dict:
        counts = {"N": 0, "S": 0, "E": 0, "W": 0}
        detail = {"N": 0, "NE": 0, "E": 0, "SE": 0, "S": 0, "SW": 0, "W": 0, "NW": 0}
        total = 0
        for heading in self._track_headings.values():
            counts[self._quadrant(heading)] += 1
            detail[self._cardinal(heading)] += 1
            total += 1
        pct = {d: round(100.0 * c / total, 1) for d, c in detail.items()} if total else {d: 0.0 for d in detail}
        frac = {d: round(c / total, 3) for d, c in counts.items()} if total else dict.fromkeys(counts, 0.0)
        return {
            "cardinal": frac,
            "counts": detail,
            "percentages": pct,
            "total_with_heading": total,
            "note": "compass angles are in satellite image frame: 0 deg = +x (east), 90 deg = +y (south)",
        }

    def traffic_flow_rate(self) -> dict:
        unique = len(self._track_classes)
        if not self.fps or not self.total_frames:
            return {
                "avg_per_minute": 0.0, "peak_per_minute": 0.0,
                "duration_s": 0.0, "unique_vehicles": unique,
                "window_s": 60, "sample_rate": False,
            }
        starts = sorted(self._track_first_frame[k] / self.fps for k in self._track_first_frame)
        duration = self.total_frames / self.fps
        window = min(60.0, duration)
        avg = unique / (duration / 60.0)
        peak = 0.0
        if starts:
            i = 0
            while i < len(starts):
                j = i
                while j < len(starts) and starts[j] < starts[i] + window:
                    j += 1
                peak = max(peak, (j - i) / (window / 60.0))
                i = max(j, i + 1)
        return {
            "avg_per_minute": round(avg, 2),
            "peak_per_minute": round(peak, 2),
            "duration_s": round(duration, 2),
            "unique_vehicles": unique,
            "window_s": round(window, 2),
            "sample_rate": window < 60.0,
        }

    def full_summary(self) -> dict:
        return {
            "location_code": self.data.get("location_code"),
            "mp4_path": self.data.get("mp4_path"),
            "fps": self.fps,
            "total_frames": self.total_frames,
            "duration_s": round(self.duration_seconds, 2) if self.duration_seconds else None,
            "vehicle_count_by_class": self.vehicle_count_by_class(),
            "total_detections": self.detection_count(),
            "speed_stats": self.speed_stats(),
            "speed_distribution": self.speed_distribution(),
            "peak_frames": self.peak_frames(),
            "heading_distribution": self.heading_distribution(),
            "traffic_flow_rate": self.traffic_flow_rate(),
        }

    def query(self, question_parsed: dict) -> dict:
        if not isinstance(question_parsed, dict):
            question_parsed = {}
        raw_intent = str(
            question_parsed.get("intent")
            or question_parsed.get("type")
            or question_parsed.get("question_type")
            or ""
        ).strip().lower().replace(" ", "_").replace("-", "_")
        intent = _INTENT_ALIASES.get(raw_intent, raw_intent)
        filt = question_parsed.get("class_filter") or question_parsed.get("filter") or question_parsed.get("class")

        def num(name, default):
            try:
                value = int(question_parsed.get(name, default))
            except (TypeError, ValueError):
                return default
            return max(1, value) if default >= 1 else value

        if intent == "vehicle_count":
            data = {
                "count": self.vehicle_count(filt),
                "detections": self.detection_count(filt),
                "class_filter": filt,
            }
        elif intent == "vehicle_count_by_class":
            data = self.vehicle_count_by_class()
        elif intent == "speed_stats":
            data = self.speed_stats(filt)
        elif intent == "speed_distribution":
            data = self.speed_distribution(num("buckets", 10))
        elif intent == "peak_frames":
            data = self.peak_frames(num("top_n", 5))
        elif intent == "heading_distribution":
            data = self.heading_distribution()
        elif intent == "traffic_flow_rate":
            data = self.traffic_flow_rate()
        elif intent == "full_summary":
            data = self.full_summary()
        else:
            return {
                "status": "error",
                "intent": raw_intent,
                "data": {"error": f"unknown intent: {raw_intent or '(missing)'}"},
            }
        return {"status": "ok", "intent": intent, "data": data}
