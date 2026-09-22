import json

import pytest

from trafficlab.analytics import TrafficAnalytics


def _obj(tid, cls, heading=None, speed=None, have=True):
    return {
        "tracked_id": tid,
        "class": cls,
        "confidence": 0.9,
        "bbox_2d": [10, 20, 60, 90],
        "sat_coords": [100.0, 200.0],
        "have_heading": have,
        "have_measurements": True,
        "default_heading": False,
        "heading": heading,
        "speed_kmh": speed,
        "sat_floor_box": None,
        "bbox_3d": None,
    }


def _replay():
    tracks = {1: "car", 2: "car", 3: "truck", 4: "truck", 5: "bus"}
    headings = {1: 0.0, 2: 90.0, 3: 180.0, 4: 270.0, 5: 45.0}
    speeds = {1: 10.0, 2: 20.0, 3: 30.0, 4: 40.0, 5: 50.0}
    frames = []
    for f in range(60):
        objs = [
            _obj(t, tracks[t], heading=headings[t], speed=speeds[t])
            for t in tracks
            if f < 40 + t * 4
        ]
        if f % 20 == 0:
            objs.append(_obj(None, "pedestrian", have=False))
        frames.append({"frame_index": f, "objects": objs})
    return {
        "mp4_path": "test.mp4",
        "meta": {"resolution": [1920, 1080], "fps": 30.0},
        "location_code": "LOC-1",
        "mp4_frame_count": 60,
        "animation_frame_count": 59,
        "frames": frames,
    }


@pytest.fixture
def eng():
    return TrafficAnalytics(_replay())


def test_counts(eng):
    assert eng.vehicle_count() == 8
    assert eng.vehicle_count("car") == 2
    assert eng.vehicle_count("truck") == 2
    assert eng.vehicle_count_by_class() == {
        "bus": 1, "car": 2, "pedestrian": 3, "truck": 2,
    }
    assert eng.detection_count() == (44 + 48 + 52 + 56 + 60) + 3


def test_speed_stats(eng):
    s = eng.speed_stats()
    assert s["sample_count"] == 5
    assert s["avg_kmh"] == pytest.approx(30.0, abs=0.01)
    assert s["min_kmh"] == 10.0 and s["max_kmh"] == 50.0
    assert eng.speed_stats("bus")["avg_kmh"] == 50.0
    assert eng.speed_stats("nothing")["sample_count"] == 0


def test_speed_distribution(eng):
    d = eng.speed_distribution(4)
    assert len(d) == 4
    assert sum(b["count"] for b in d) == 5
    assert abs(sum(b["percent"] for b in d) - 100.0) < 0.5
    assert eng.speed_distribution(0) and eng.speed_distribution("x")


def test_peak_frames(eng):
    pf = eng.peak_frames(3)
    assert len(pf) == 3
    assert [p["vehicle_count"] for p in pf] == [6, 6, 6]
    assert pf[0]["frame_index"] == 0
    assert eng.peak_frames(0)


def test_heading_distribution(eng):
    h = eng.heading_distribution()
    assert h["total_with_heading"] == 5
    assert abs(sum(h["cardinal"].values()) - 1.0) < 0.02
    assert h["counts"]["E"] == 1 and h["counts"]["S"] == 1
    assert h["counts"]["W"] == 1 and h["counts"]["N"] == 1
    assert h["counts"]["SE"] == 1


def test_flow_rate(eng):
    fr = eng.traffic_flow_rate()
    assert fr["duration_s"] == 2.0
    assert fr["unique_vehicles"] == 8
    assert fr["peak_per_minute"] >= fr["avg_per_minute"]
    assert fr["sample_rate"] is True


def test_full_summary_json(eng):
    summary = eng.full_summary()
    json.dumps(summary)
    assert summary["location_code"] == "LOC-1"
    assert summary["total_detections"] == eng.detection_count()


def test_query_router(eng):
    assert eng.query({"intent": "vehicle_count", "class": "car"})["data"]["count"] == 2
    assert eng.query({"type": "how_fast"})["intent"] == "speed_stats"
    assert eng.query({"intent": "BUSIEST", "top_n": "2"})["data"].__len__() == 2
    assert eng.query({"intent": "teleport"})["status"] == "error"
    assert eng.query(None)["status"] == "error"
    assert eng.query("garbage")["status"] == "error"


EMPTY_CASES = [
    {},
    None,
    {"frames": "nope", "meta": 7},
    {"frames": [None, 5, {"objects": "x"}, {"frame_index": "bad",
     "objects": [None, {"class": None, "speed_kmh": "fast",
     "heading": float("nan")}]}], "meta": {"fps": -3}},
    "not a dict at all",
]


@pytest.mark.parametrize("bad", EMPTY_CASES)
def test_malformed_never_crashes(bad):
    e = TrafficAnalytics(bad)
    assert isinstance(e.vehicle_count(), int)
    assert e.vehicle_count("car") >= 0
    assert isinstance(e.vehicle_count_by_class(), dict)
    assert e.speed_stats()["avg_kmh"] >= 0.0
    assert isinstance(e.speed_distribution(), list)
    assert isinstance(e.peak_frames(), list)
    assert e.heading_distribution()["total_with_heading"] >= 0
    assert e.traffic_flow_rate()["avg_per_minute"] >= 0.0
    json.dumps(e.full_summary())
    assert e.query({"intent": "summary"})["status"] == "ok"


def test_empty_replay_returns_zeros():
    e = TrafficAnalytics({})
    assert e.vehicle_count() == 0
    assert e.vehicle_count_by_class() == {}
    assert e.speed_stats()["sample_count"] == 0
    assert e.speed_distribution() == []
    assert e.peak_frames() == []
    assert e.heading_distribution()["total_with_heading"] == 0
    assert e.traffic_flow_rate()["avg_per_minute"] == 0.0
    assert e.full_summary()["duration_s"] is None
