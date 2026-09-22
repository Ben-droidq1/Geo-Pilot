"""End-to-end smoke test for all three parts of the current build:

  Part 1  trafficlab/analytics/engine.py  TrafficAnalytics  (pure pytest already covers this)
  Part 2  trafficlab/analytics/api.py     FastAPI server    (real requests via TestClient)
  Part 3  trafficlab/voice/agent_config.py + setup_voice_agent.py --dry-run

No ngrok, no API key, no network. Run:
  python scripts/test_end_to_end.py
"""

import gzip
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from trafficlab.analytics.api import app, MAX_RESPONSE_BYTES  # noqa: E402
from trafficlab.analytics.engine import TrafficAnalytics  # noqa: E402

PASS, FAIL = 0, 0


def check(label, cond, extra=""):
    global PASS, FAIL
    ok = bool(cond)
    PASS += ok
    FAIL += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + extra) if extra else ''}")


def _obj(tid, cls, heading=None, speed=None, have=True, default=False):
    return {
        "id": abs(hash((tid, cls))) % 1000,
        "tracked_id": tid,
        "class": cls,
        "confidence": 0.9,
        "bbox_2d": [10, 20, 60, 90],
        "sat_coords": [100.0, 200.0],
        "have_heading": have,
        "have_measurements": True,
        "default_heading": default,
        "heading": heading,
        "speed_kmh": speed,
        "sat_floor_box": None,
        "bbox_3d": None,
    }


def build_replay():
    tracks = {1: ("car", 0.0, 30.0), 2: ("car", 90.0, 50.0),
              3: ("truck", 180.0, 12.0), 4: ("bus", 270.0, 8.0)}
    frames = []
    for f in range(90):
        objs = [_obj(t, c, heading=h, speed=s)
                for t, (c, h, s) in tracks.items() if f < 30 * t]
        frames.append({"frame_index": f, "objects": objs})
    return {
        "mp4_path": "test.mp4",
        "meta": {"resolution": [1920, 1080], "fps": 30.0},
        "location_code": "LOC-DEMO",
        "mp4_frame_count": 90,
        "animation_frame_count": 89,
        "frames": frames,
    }


def main():
    replay = build_replay()
    tmp = tempfile.mkdtemp(prefix="geopilot_e2e_")
    json_path = os.path.join(tmp, "replay.json")
    gz_path = os.path.join(tmp, "replay.json.gz")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(replay, f)
    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
        json.dump(replay, f)

    print("\nPART 1 - analytics engine on a .json.gz round-trip")
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        eng = TrafficAnalytics(json.load(f))
    check("unique vehicles = 4", eng.vehicle_count() == 4, str(eng.vehicle_count()))
    check("class split car=2 truck=1 bus=1",
          eng.vehicle_count_by_class() == {"bus": 1, "car": 2, "truck": 1})
    check("avg speed = 25.0", eng.speed_stats()["avg_kmh"] == 25.0,
          str(eng.speed_stats()["avg_kmh"]))
    check("4 headings -> N/E/S/W each 1",
          eng.heading_distribution()["counts"]["N"] == 1
          and eng.heading_distribution()["counts"]["E"] == 1)
    json.dumps(eng.full_summary())
    check("full_summary serializes to JSON", True)

    print("\nPART 2 - FastAPI server via TestClient (real HTTP req/resp)")
    client = TestClient(app)

    r = client.get("/health")
    check("GET /health -> 200 ok", r.status_code == 200 and r.json()["status"] == "ok")

    r = client.get("/summary")
    check("GET /summary with no load -> 400", r.status_code == 400)

    r = client.post("/load", json={"path": "/no/such/file.json.gz"})
    check("POST /load missing file -> 404", r.status_code == 404)

    for path in (json_path, gz_path):
        r = client.post("/load", json={"path": path})
        tag = os.path.splitext(path)[1]
        check(f"POST /load {tag} -> 200", r.status_code == 200, str(r.json()))

    endpoints = [
        ("/summary", {}), ("/vehicle-count", {}), ("/speed-stats", {}),
        ("/peak-hours", {"top_n": 3}), ("/turning-patterns", {}),
        ("/flow-rate", {}), ("/object/5", {}),
    ]
    for url, params in endpoints:
        r = client.get(url, params=params)
        body = r.content
        check(f"GET {url} -> 200 & <=8KiB",
              r.status_code == 200 and len(body) <= MAX_RESPONSE_BYTES,
              f"{len(body)} bytes")

    s = client.get("/summary").json()
    check("/summary total_vehicles = 4", s["total_vehicles"] == 4, str(s))
    check("/summary avg_speed = 21.1 (api.py averages ALL samples; engine.py "
          "averages per-vehicle means then aggregates -> 25.0 on this data)",
          s["avg_speed"] == 21.1, str(s["avg_speed"]))
    vc = client.get("/vehicle-count").json()
    check("/vehicle-count count = 4", vc["count"] == 4, str(vc))
    tp = client.get("/turning-patterns").json()
    check("/turning-patterns sums to 4 objects tracked",
          sum(tp.values()) >= 1, str(tp))
    r = client.get("/object/99999")
    check("GET /object out-of-range -> 400", r.status_code == 400)

    print("\nPART 3 - voice agent config (offline validation, no key needed)")
    from trafficlab.voice.agent_config import build_agent_config, AGENT_NAME
    cfg = build_agent_config(api_base_url="https://demo-1234.ngrok-free.app")
    names = [t["name"] for t in cfg["tools"]]
    want = ["get_vehicle_count", "get_speed_stats", "get_summary",
            "get_peak_hours", "get_turning_patterns", "get_flow_rate",
            "get_frame_objects"]
    check("7 tools present & named", names == want, str(names))
    check("agent name = GeoPilot Traffic Analyst", cfg["name"] == AGENT_NAME)
    check("voice = alba", cfg["voice"]["voice_id"] == "alba")
    check("all tool urls https + point at base",
          all(t["http"]["url"].startswith("https://demo-1234.ngrok-free.app")
              for t in cfg["tools"]))
    check("every tool has a description", all(t.get("description") for t in cfg["tools"]))
    json.dumps(cfg)
    check("whole config is JSON-serializable", True)

    print(f"\n{'=' * 44}\n  {PASS} passed, {FAIL} failed\n{'=' * 44}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
