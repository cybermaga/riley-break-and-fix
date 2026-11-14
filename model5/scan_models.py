"""
Live model scanner for the Break the Model server.

One command shows every model the server currently exposes, diffs against the
models we already know, and loudly flags any Claude / Anthropic model the moment
the organizers switch on the 5th "boss" model.

Usage:
    python3 model5/scan_models.py            # one-shot
    python3 model5/scan_models.py --watch 30 # re-poll every 30s until Claude appears
"""
from __future__ import annotations

import argparse
import os
import sys
import time

# allow running as `python3 model5/scan_models.py` — put the repo root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import btm  # local client: list_models()  # noqa: E402

# Every model we have already seen on the stand — so only a genuinely new one
# is flagged as NEW. (The 4 Nebius originals + the Groq and Claude endpoints.)
KNOWN = {
    "Qwen/Qwen3-30B-A3B-Instruct-2507",
    "openai/gpt-oss-120b",
    "Qwen/Qwen3-235B-A22B-Instruct-2507",
    "deepseek-ai/DeepSeek-V4-Pro-0813",
    "groq/openai/gpt-oss-120b",
    "groq/qwen/qwen3.8-27b",
    "groq/openai/gpt-oss-20b",
    "claude-haiku-5-5",
    "claude-sonnet-5-5",
    "claude-opus-5-5",
}


def is_claude(model_id: str) -> bool:
    m = model_id.lower()
    return "claude" in m or "anthropic" in m


def scan() -> list[str]:
    models = btm.list_models()
    new = [m for m in models if m not in KNOWN]
    claude = [m for m in models if is_claude(m)]
    print(f"\n{len(models)} models live:")
    for m in models:
        tags = []
        if m not in KNOWN:
            tags.append("NEW")
        if is_claude(m):
            tags.append("★ CLAUDE / 5th BOSS")
        print(f"  {m}" + (f"   [{', '.join(tags)}]" if tags else ""))
    if new:
        print(f"\nNew since our baseline ({len(new)}): " + ", ".join(new))
    if claude:
        print("\n*** 5th model is LIVE: " + ", ".join(claude) +
              "  ->  run:  python3 model5/crack_model5.py ***")
    else:
        print("\n5th (Claude) model: not live yet.")
    return claude


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", type=int, default=0,
                    help="seconds between polls; stops when a Claude model appears")
    args = ap.parse_args()
    if not args.watch:
        scan()
        return
    print(f"Watching the model list every {args.watch}s (Ctrl-C to stop)...")
    while True:
        try:
            if scan():
                return
        except Exception as e:  # noqa: BLE001
            print(f"  (scan error: {e})", file=sys.stderr)
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
