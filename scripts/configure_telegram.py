"""Verify the configured bot and save the most recent private chat ID."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def api_call(token, method):
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}", timeout=15) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(f"Telegram {method} failed")
    return result["result"]


def main():
    contents = ENV_FILE.read_text(encoding="utf-8")
    values = dict(line.split("=", 1) for line in contents.splitlines() if line and not line.startswith("#") and "=" in line)
    token = values.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env")
    bot = api_call(token, "getMe")
    expected = values.get("TELEGRAM_EXPECTED_USERNAME", "")
    if expected and bot["username"] != expected:
        raise RuntimeError("Token does not belong to the expected bot")
    updates = api_call(token, "getUpdates") if not values.get("TELEGRAM_CHAT_ID") else []
    private_chats = [
        update["message"]["chat"]["id"]
        for update in updates
        if update.get("message", {}).get("chat", {}).get("type") == "private"
    ]
    if not private_chats and not values.get("TELEGRAM_CHAT_ID"):
        raise RuntimeError("Send /start to your bot in Telegram, then rerun")
    chat_id = values.get("TELEGRAM_CHAT_ID") or str(private_chats[-1])
    if "TELEGRAM_CHAT_ID=" in contents:
        lines = [f"TELEGRAM_CHAT_ID={chat_id}" if line.startswith("TELEGRAM_CHAT_ID=") else line for line in contents.splitlines()]
        ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        with ENV_FILE.open("a", encoding="utf-8") as env:
            env.write(f"\nTELEGRAM_CHAT_ID={chat_id}\n")
    secrets = ENV_FILE.parent / "secrets"
    secrets.mkdir(exist_ok=True)
    (secrets / "telegram_bot_token").write_text(token, encoding="utf-8")
    if "--test" in sys.argv:
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=json.dumps({"chat_id": chat_id, "text": "[TEST] DDM501 Tutorial07: Telegram configured. Airflow and Prometheus alerts will arrive here."}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            if not json.load(response).get("ok"):
                raise RuntimeError("Test delivery failed")
    print(f"Verified @{bot['username']}; synced ignored Alertmanager secret" + ("; test delivered" if "--test" in sys.argv else ""))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        detail = f" HTTP {error.code}" if isinstance(error, urllib.error.HTTPError) else (f": {error}" if isinstance(error, RuntimeError) else "")
        print(f"Telegram setup failed: {type(error).__name__}{detail}")
        raise SystemExit(1) from None
