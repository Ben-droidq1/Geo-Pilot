"""
Entry point for the TrafficLab Analytics API server.

Run directly:
    python backend/analytics_server.py

Or with uvicorn:
    uvicorn trafficlab.analytics.api:app --host 0.0.0.0 --port 8787
"""
from __future__ import annotations

import argparse
import uvicorn

from trafficlab.analytics.api import app


def main() -> None:
    parser = argparse.ArgumentParser(description="TrafficLab Analytics API")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8787, help="Port (default: 8787)")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
