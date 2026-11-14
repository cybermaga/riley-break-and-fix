"""
Watch for Level 3 opening.

Right now the server answers level:3 with HTTP 403 {"code":"level_not_available",
"message":"only level [2] is open"}. This polls a tiny benign probe at level 3 and
exits 0 the moment the organizers open it (HTTP 200) — so the crack can auto-fire.

Usage:
    python3 model5/watch_level3.py              # one probe
    python3 model5/watch_level3.py --watch 20   # poll every 20s until L3 opens
"""
from __future__ import annotations

import argparse
import os
import time
import uuid

import requests
from dotenv import load_dotenv

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_ROOT, ".env"))
API = os.environ["API_URL"].rstrip("/")
KEY = os.environ["NEBIUS_API_KEY"]
NAME = os.environ.get("YOUR_NAME", "")


def probe():
    body = {"participant": NAME, "model": "Qwen/Qwen3-30B-A3B-Instruct-2507",
            "level": 3, "conversation_id": "l3probe_" + uuid.uuid4().hex[:8],
            "message": "Hi, what can you help with?"}
    try:
        r = requests.post(f"{API}/chat", json=body,
                          headers={"X-Nebius-Key": KEY}, timeout=60)
        try:
            return r.status_code, r.json()
        except Exception:  # noqa: BLE001
            return r.status_code, {"_raw": r.text[:200]}
    except Exception as e:  # noqa: BLE001
        return None, {"error": {"message": str(e)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", type=int, default=0,
                    help="seconds between polls; stops when Level 3 opens")
    args = ap.parse_args()
    while True:
        code, data = probe()
        if code == 200:
            print("\n*** LEVEL 3 IS OPEN (HTTP 200) — firing the crack now ***\n"
                  "    -> python3 model5/crack_level3.py")
            return
        msg = ""
        if isinstance(data, dict):
            msg = (data.get("error") or {}).get("message") or data.get("_raw", "")
        print(f"[{time.strftime('%H:%M:%S')}] Level 3 still closed (http={code}): {msg}")
        if not args.watch:
            return
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
