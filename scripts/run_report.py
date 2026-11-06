"""Run the Dify workflow via its API and save the Markdown report.

Usage: DIFY_API_KEY=app-... python scripts/run_report.py "your topic"
"""
import json
import os
import pathlib
import re
import sys
import urllib.request

base = os.environ.get("DIFY_BASE_URL", "http://localhost/v1")
key = os.environ["DIFY_API_KEY"]
topic = " ".join(sys.argv[1:]) or "Open-source tools for nanopore sequencing analysis"
req = urllib.request.Request(
    f"{base}/workflows/run",
    data=json.dumps({"inputs": {"topic": topic, "depth": 4}, "response_mode": "blocking",
                     "user": "cli"}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    out = json.load(r)["data"]["outputs"]
slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60]
path = pathlib.Path("reports") / f"{slug}.md"
path.parent.mkdir(exist_ok=True)
path.write_text(out["report"])
print(f"saved {path}  stats={out.get('stats')}")
