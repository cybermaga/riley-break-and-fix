#!/usr/bin/env python3
"""
One-shot: set the Claude key from the clipboard, verify it, and — only if it
works — immediately run the attack across all three Claude models.

Use it when the organizers give you a WORKING Anthropic API key (sk-ant-api03-…):
  1. Copy the key (Cmd+C).
  2. Run (press ↑ to recall, Enter — do NOT copy the command, or you overwrite the key):
       .venv/bin/python go_claude.py
  3. If the key is valid it prints "✅ KEY WORKS" and then attacks
     claude-haiku-5-5, claude-sonnet-5-5, claude-opus-5-5 and shows the winning turn_ids.
  If the key is rejected it stops and tells you — nothing is attacked.
"""
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
ENV = HERE / ".env"
CLAUDE_MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]


def set_key_from_clipboard():
    key = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=10).stdout.strip()
    if not key:
        sys.exit("Clipboard empty — copy the key first (Cmd+C), then run again.")
    if not key.startswith("sk-ant-"):
        sys.exit(f"Clipboard doesn't look like a key (starts with '{key[:8]}…'). Copy the KEY, not the command.")
    lines = [l for l in ENV.read_text().splitlines() if not l.startswith("ANTHROPIC_API_KEY=")]
    lines.append("ANTHROPIC_API_KEY=" + key)
    ENV.write_text("\n".join(lines) + "\n")
    print(f"  Saved key (len {len(key)}, prefix {key[:12]}…).")
    return key


def test_key(key):
    import requests
    from dotenv import dotenv_values
    env = dotenv_values(ENV)
    api = env.get("API_URL", "").rstrip("/")
    body = {"participant": env.get("YOUR_NAME", ""), "model": "claude-haiku-5-5",
            "conversation_id": "test_" + uuid.uuid4().hex[:8], "message": "Hi"}
    try:
        r = requests.post(f"{api}/chat", json=body, headers={"X-API-Key": key}, timeout=60)
        d = r.json()
    except Exception as e:  # noqa: BLE001
        print(f"  live test error: {e}"); return False
    if r.status_code == 200 and d.get("reply"):
        print("  ✅ KEY WORKS — Claude replied.")
        return True
    if "invalid x-api-key" in str(d):
        print("  ❌ Anthropic rejects this key (invalid x-api-key). Need a valid sk-ant-api03-… key.")
    else:
        print(f"  ❌ not working: {str(d.get('error') or d)[:160]}")
    return False


def attack():
    print("\n=== ATTACKING ALL THREE CLAUDE MODELS ===")
    wins = []
    for model in CLAUDE_MODELS:
        print(f"\n########## {model} ##########")
        p = subprocess.run([sys.executable, str(HERE / "model5" / "crack_model5.py"),
                            "--model", model], capture_output=True, text=True, timeout=1200)
        out = p.stdout + p.stderr
        print(out[-1500:])
        for line in out.splitlines():
            if "winning_turn_id =" in line and "—" not in line:
                wins.append((model, line.split("winning_turn_id =")[-1].strip()))
    print("\n==================== CLAUDE RESULTS ====================")
    if wins:
        for m, t in wins:
            print(f"  {m}: {t}")
        print("  → submit these turn_ids for the Claude (5th model) rows.")
    else:
        print("  No leak yet on Claude. Claude is well-aligned; we iterate the vectors.")
    print("=======================================================")


def main():
    print("Setting Claude key from clipboard…")
    key = set_key_from_clipboard()
    print("Testing it…")
    if test_key(key):
        attack()
    else:
        print("\nStopped — fix the key and run again. Nothing was attacked.")


if __name__ == "__main__":
    main()
