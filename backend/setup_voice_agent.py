"""One-time registration of the GeoPilot voice agent with AssemblyAI.

Reads ASSEMBLYAI_API_KEY (and GEOPILOT_API_URL / VOICE_ID / FRAME_URL_MODE)
from the environment or the project-root .env, builds the stored-agent
config from trafficlab/voice/agent_config.py, then:

    python backend/setup_voice_agent.py --dry-run  print the exact JSON, no network
    python backend/setup_voice_agent.py --list      list agents already on the account
    python backend/setup_voice_agent.py              create the agent (or update it in
                                            place if the name already exists)

The printed agent_id is what the browser/client connects with via
session.update -> {"agent_id": ...}. The API key is never printed.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from trafficlab.voice.agent_config import (
    AGENT_NAME,
    build_agent_config,
    validate_api_base_url,
)

AGENTS_URL = "https://agents.assemblyai.com/v1/agents"


def load_dotenv(path=".env"):
    try:
        from dotenv import load_dotenv as _load
        _load(path)
        return
    except ImportError:
        pass
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and value and key not in os.environ:
                os.environ[key] = value


def api(method, url, key, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return e.code, {"detail": raw.decode("utf-8", "replace")[:500]}
    except urllib.error.URLError as e:
        return None, {"detail": f"network error: {e.reason}"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the agent config JSON without calling AssemblyAI")
    parser.add_argument("--list", action="store_true",
                        help="list agents on the account and exit")
    parser.add_argument("--voice", default=None,
                        help="voice_id override (default: alba, see agent_config.VALID_VOICES)")
    parser.add_argument("--frame-url-mode", choices=["path", "query"], default=None,
                        help="get_frame_objects URL style (default: path)")
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()

    load_dotenv(args.env_file)
    config = build_agent_config(voice_id=args.voice, frame_url_mode=args.frame_url_mode)

    if args.dry_run:
        print(json.dumps(config, indent=2))
        problem = validate_api_base_url(config["tools"][0]["http"]["url"].split("/vehicle-count")[0])
        if problem:
            print(f"\n[dry-run warning] {problem}", file=sys.stderr)
        return 0

    key = os.environ.get("ASSEMBLYAI_API_KEY", "").strip()
    if not key:
        print("ERROR: ASSEMBLYAI_API_KEY is not set.\n"
              "  1. Create a free account at https://www.assemblyai.com/dashboard\n"
              "  2. Copy your key from the API Keys page\n"
              "  3. Put it in .env as ASSEMBLYAI_API_KEY=... (each teammate uses their own)",
              file=sys.stderr)
        return 1

    base = config["tools"][0]["http"]["url"].split("/vehicle-count")[0]
    problem = validate_api_base_url(base)
    if problem:
        print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    status, agents = api("GET", AGENTS_URL, key)
    if args.list:
        print(json.dumps(agents, indent=2))
        return 0 if status == 200 else 1
    if status not in (200, 401) and status is not None:
        print(f"WARNING: could not list existing agents (HTTP {status}): {agents}", file=sys.stderr)
    if status == 401:
        print("ERROR: AssemblyAI rejected the API key (401 Unauthorized).", file=sys.stderr)
        return 1

    existing = None
    if status == 200 and isinstance(agents, list):
        existing = next((a for a in agents if a.get("name") == AGENT_NAME), None)

    if existing:
        agent_id = existing["id"]
        status, record = api("PUT", f"{AGENTS_URL}/{agent_id}", key, config)
        action = "updated"
    else:
        status, record = api("POST", AGENTS_URL, key, config)
        agent_id = (record or {}).get("id")
        action = "created"

    if status in (200, 201) and record:
        print(f"Agent {action}: {record.get('name')}")
        print(f"agent_id: {agent_id}")
        print(f"voice:    {config['voice']['voice_id']}")
        print(f"tools:    {len(config['tools'])} HTTP tools -> {base}")
        print("\nNext: verify it in the AssemblyAI dashboard, then connect with")
        print(f'  session.update -> {{"type": "session.update", "session": {{"agent_id": "{agent_id}"}}}}')
        return 0

    print(f"ERROR: AssemblyAI returned HTTP {status}: {json.dumps(record)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
