#!/usr/bin/env python3
"""
Safely set an API key in .env — the key is typed HIDDEN (never shown on screen
or saved to your shell history), written to .env without duplicates, and
optionally tested live.

Run it from this folder:
    .venv/bin/python set_key.py
    # or, if you have no venv:   python3 set_key.py

Supports several keys — run it again for each one the organizers gave you:
    1) Anthropic (Claude)   sk-ant-...
    2) Groq                 gsk_...
    3) Nebius               v1....
"""
import getpass
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
ENV = HERE / ".env"

VARS = {
    "1": ("ANTHROPIC_API_KEY", "sk-ant-"),
    "2": ("GROQ_API_KEY", "gsk_"),
    "3": ("NEBIUS_API_KEY", ""),
}


def read_env_value(var):
    if not ENV.exists():
        return ""
    for line in ENV.read_text().splitlines():
        if line.startswith(var + "="):
            return line[len(var) + 1:]
    return ""


def write_env(var, key):
    lines = ENV.read_text().splitlines() if ENV.exists() else []
    lines = [l for l in lines if not l.startswith(var + "=")]   # drop old + duplicates
    lines.append(f"{var}={key}")
    ENV.write_text("\n".join(lines) + "\n")


def test_claude():
    """Send one harmless 'Hi' to claude-haiku-5-5 and report if the key works."""
    try:
        import requests
        from dotenv import dotenv_values
    except Exception:
        print("  (skipping live test: 'requests'/'dotenv' not installed in this python)")
        return
    env = dotenv_values(ENV)
    api = (env.get("API_URL") or "").rstrip("/")
    key = env.get("ANTHROPIC_API_KEY") or ""
    body = {"participant": env.get("YOUR_NAME", ""), "model": "claude-haiku-5-5",
            "conversation_id": "keytest_" + uuid.uuid4().hex[:8],
            "message": "Hi, what are your hours?"}
    try:
        r = requests.post(f"{api}/chat", json=body,
                          headers={"X-API-Key": key}, timeout=60)
        d = r.json()
    except Exception as e:  # noqa: BLE001
        print(f"  live test error: {e}")
        return
    if r.status_code == 200 and d.get("reply"):
        print("  ✅ KEY WORKS — Claude replied. You're ready to attack claude-* models.")
    elif "invalid x-api-key" in str(d):
        print("  ❌ Anthropic says the key is INVALID. Re-copy the FULL key (sk-ant-api03-…, ~108 chars).")
    else:
        print(f"  ⚠️ http={r.status_code}: {str(d)[:160]}")


def from_clipboard(var="ANTHROPIC_API_KEY"):
    """Non-interactive: read the key from the macOS clipboard (pbpaste).
    Copy the key (Cmd+C) first, then run:  python set_key.py --clip  [GROQ|NEBIUS]
    The key is never typed or echoed — only its length/prefix is shown."""
    import subprocess
    prefix = {"ANTHROPIC_API_KEY": "sk-ant-", "GROQ_API_KEY": "gsk_", "NEBIUS_API_KEY": ""}.get(var, "")
    try:
        key = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Could not read clipboard: {e}")
    if not key:
        sys.exit("Clipboard is empty — copy the key first (Cmd+C), then run again.")
    if prefix and not key.startswith(prefix):
        print(f"  WARNING: {var} normally starts with '{prefix}'. Clipboard starts with '{key[:7]}…'. Saving anyway.")
    if var == "ANTHROPIC_API_KEY" and len(key) < 90:
        print(f"  WARNING: clipboard key is only {len(key)} chars (real Anthropic key ~108). Possibly truncated.")
    write_env(var, key)
    print(f"  Saved {var} to {ENV}  (length {len(key)}, starts with {key[:7]}… — full value NOT shown)")
    if var == "ANTHROPIC_API_KEY":
        print("  testing claude-haiku-5-5 …")
        test_claude()
    sys.exit(0)


def main():
    if "--clip" in sys.argv:
        rest = [a for a in sys.argv[1:] if a != "--clip"]
        name = rest[0].upper() if rest else "ANTHROPIC"
        var = {"ANTHROPIC": "ANTHROPIC_API_KEY", "GROQ": "GROQ_API_KEY",
               "NEBIUS": "NEBIUS_API_KEY"}.get(name, "ANTHROPIC_API_KEY")
        from_clipboard(var)
        return
    print("\nWhich key do you want to save?")
    print("  1) Anthropic (Claude)   sk-ant-...")
    print("  2) Groq                 gsk_...")
    print("  3) Nebius               v1....")
    choice = (input("Number [1]: ").strip() or "1")
    if choice not in VARS:
        sys.exit("Pick 1, 2 or 3.")
    var, prefix = VARS[choice]

    key = getpass.getpass(f"\nPaste {var} (input is hidden) then press Enter: ").strip()
    if not key:
        sys.exit("No key entered — nothing changed.")
    if prefix and not key.startswith(prefix):
        print(f"  WARNING: {var} normally starts with '{prefix}'. Saving anyway.")
    if var == "ANTHROPIC_API_KEY" and len(key) < 90:
        print(f"  WARNING: this key is only {len(key)} chars. A real Anthropic key is ~108. "
              "It may be truncated — double-check you copied all of it.")

    write_env(var, key)
    print(f"\n  Saved {var} to {ENV}")
    print(f"  (length {len(key)}, starts with {key[:7]}… — full value NOT shown)")

    if var == "ANTHROPIC_API_KEY":
        if (input("\nTest it against Claude now? [Y/n]: ").strip().lower() or "y") == "y":
            print("  testing claude-haiku-5-5 …")
            test_claude()
    print("\nDone. Re-run this script for another key if you have more.\n")


if __name__ == "__main__":
    main()
