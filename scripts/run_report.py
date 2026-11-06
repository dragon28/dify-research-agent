"""Run the published Dify workflow via its API (streaming) and save the report.

Usage: set -a; . ./.env; set +a; python scripts/run_report.py "your topic"
"""

import json
import os
import pathlib
import re
import sys
import time
import urllib.request

base = os.environ.get("DIFY_BASE_URL", "http://localhost/v1")
key = os.environ["DIFY_API_KEY"]
topic = " ".join(sys.argv[1:]) or "Open-source tools for nanopore sequencing analysis"
req = urllib.request.Request(
    f"{base}/workflows/run",
    data=json.dumps({"inputs": {"topic": topic, "depth": 4}, "response_mode": "streaming",
                     "user": "cli"}).encode(),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
t0 = time.time()
final = None
with urllib.request.urlopen(req, timeout=1800) as r:
    for raw in r:
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        ev = json.loads(line[5:])
        if ev.get("event") == "node_finished":
            d = ev["data"]
            print(f"  {d.get('title')}: {d.get('status')}", file=sys.stderr)
        elif ev.get("event") == "workflow_finished":
            final = ev["data"]
if not final or final.get("status") != "succeeded":
    sys.exit(f"workflow failed: {final and final.get('error')}")
out = final["outputs"]
stats = json.loads(out.get("stats") or "{}")
stats["seconds"] = round(time.time() - t0)
if not stats.get("sources_total"):
    sys.exit(f"no sources retrieved - is SearXNG reachable from Dify? stats={stats}")
slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60]
dest = pathlib.Path(os.environ.get("REPORT_DIR", "reports"))
dest.mkdir(exist_ok=True)
(dest / f"{slug}.md").write_text(out["report"])
(dest / f"{slug}.stats.json").write_text(json.dumps({"topic": topic, **stats}, indent=2) + "\n")
print(f"saved {dest / (slug + '.md')}  stats={stats}")
