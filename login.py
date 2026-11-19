"""
One-time login for Google's GA4 MCP server (analytics-mcp), read-only.

Reads the Desktop OAuth client (client.json) from ~/.ga4-mcp, or from
~/.gsc-mcp if the Search Console connector is already set up, opens the
browser for a Google sign-in with the analytics.readonly scope only, and
writes an authorized_user credentials file to ~/.ga4-mcp/credentials.json.
The MCP server reads it through GOOGLE_APPLICATION_CREDENTIALS.
No secrets are printed. GA4_CONFIG_DIR overrides ~/.ga4-mcp.
"""
import json
import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
CONFIG_DIR = Path(os.environ.get("GA4_CONFIG_DIR") or Path.home() / ".ga4-mcp")
CLIENT_CANDIDATES = [CONFIG_DIR / "client.json", Path.home() / ".gsc-mcp" / "client.json"]
OUT = CONFIG_DIR / "credentials.json"


def main() -> None:
    # Windows consoles default to a legacy code page; the messages are Swedish.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    client_file = next((p for p in CLIENT_CANDIDATES if p.exists()), None)
    if client_file is None:
        raise SystemExit(f"Hittar ingen klientfil. Lägg client.json i {CONFIG_DIR}")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes=[SCOPE])
    creds = flow.run_local_server(port=0, prompt="consent")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "type": "authorized_user",
                "client_id": flow.client_config["client_id"],
                "client_secret": flow.client_config["client_secret"],
                "refresh_token": creds.refresh_token,
            }
        ),
        encoding="utf-8",
    )
    os.chmod(OUT, 0o600)
    print(f"Klart: inloggningen sparad i {OUT}")
    print(f"Sökväg att använda i nästa steg: {OUT.as_posix()}")


if __name__ == "__main__":
    main()
