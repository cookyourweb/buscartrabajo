#!/usr/bin/env python3
"""Uploads a workflow JSON to n8n with PUT, keeping its ID and active state.

    SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/subir_workflow.py <workflow-id> <file.json>

Reads N8N_HOST and N8N_API_KEY from .env and never prints them. Take a backup first:
the previous version is not kept by n8n's public API.

IMPORTANT (1 Nov 2026): this n8n version separates draft and published versions. PUT only
updates the DRAFT. The schedule keeps running the published version until someone clicks
"Publish" in the editor. Check afterwards that `versionId` equals `activeVersionId`.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ALLOWED_SETTINGS = {
    "executionOrder", "timezone", "saveDataErrorExecution", "saveDataSuccessExecution",
    "saveManualExecutions", "saveExecutionProgress", "executionTimeout", "errorWorkflow",
    "callerPolicy", "callerIds", "timeSavedPerExecution",
}


def env(name: str) -> str:
    for line in (Path(__file__).resolve().parent.parent / ".env").read_text().splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit(f"{name} is not in .env")


def main() -> None:
    wf_id, path = sys.argv[1], sys.argv[2]
    url = f"{env('N8N_HOST').rstrip('/')}/api/v1/workflows/{wf_id}"
    headers = {"X-N8N-API-KEY": env("N8N_API_KEY"), "Content-Type": "application/json"}
    wf = json.loads(Path(path).read_text())
    body = {
        "name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in ALLOWED_SETTINGS},
    }
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="PUT", headers=headers)
            res = json.load(urllib.request.urlopen(req, timeout=90))
            break
        except urllib.error.HTTPError as e:
            # Render's free plan answers 502 while the instance restarts.
            print(f"attempt {attempt + 1}: HTTP {e.code}")
            time.sleep(20)
    else:
        sys.exit("could not upload")
    print(f"uploaded: {res['name']} | active: {res.get('active')} | updatedAt: {res.get('updatedAt')}")
    if res.get("versionId") != res.get("activeVersionId"):
        print("DRAFT ONLY: open the workflow in n8n and click Publish, or the change is not live.")


if __name__ == "__main__":
    main()
