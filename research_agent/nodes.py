"""Pure-Python logic used by the Dify Code nodes.

Each public function mirrors one Code node. Keep them dependency-free so the
same body can be pasted into Dify's sandbox and unit-tested here.
"""
from __future__ import annotations

import json
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "fbclid", "gclid", "ref"}


def parse_plan(llm_text: str, topic: str, max_q: int = 5) -> list[str]:
    """Parse planner output into sub-questions; fall back to the topic itself."""
    m = re.search(r"\[.*\]", llm_text or "", re.DOTALL)
    qs: list[str] = []
    if m:
        try:
            data = json.loads(m.group(0))
            qs = [str(q).strip() for q in data if str(q).strip()]
        except json.JSONDecodeError:
            qs = []
    if not qs:
        qs = [ln.strip(" -*0123456789.").strip() for ln in (llm_text or "").splitlines()]
        qs = [q for q in qs if q.endswith("?")]
    seen, out = set(), []
    for q in qs:
        if q.lower() not in seen:
            seen.add(q.lower()); out.append(q)
    return out[:max_q] or [topic]


def normalize_url(url: str) -> str:
    p = urlsplit(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(p.query) if k.lower() not in TRACKING])
    host = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/") or "/"
    return urlunsplit(("https" if p.scheme in ("http", "https") else p.scheme, host, path, query, ""))


def pick_results(searxng_json: str | dict, k: int = 3) -> list[dict]:
    """Take a SearXNG /search?format=json response, dedupe, keep top k."""
    data = json.loads(searxng_json) if isinstance(searxng_json, str) else searxng_json
    out, seen = [], set()
    for r in data.get("results", []):
        url = r.get("url")
        if not url or not url.startswith(("http://", "https://")):
            continue
        key = normalize_url(url)
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": r.get("title", "").strip(), "url": url,
                    "snippet": (r.get("content") or "").strip()[:500]})
        if len(out) >= k:
            break
    return out


def build_registry(per_question: list[list[dict]]) -> list[dict]:
    """Merge results from all sub-questions into one numbered source list."""
    reg, index = [], {}
    for results in per_question:
        for r in results:
            key = normalize_url(r["url"])
            if key not in index:
                index[key] = len(reg) + 1
                reg.append({"id": index[key], **r})
    return reg


def format_sources(reg: list[dict], max_chars: int = 600) -> str:
    return "\n".join(f"[{s['id']}] {s['title']} - {s['url']}\n{s['snippet'][:max_chars]}"
                     for s in reg)


REF = r"(?:n|source|src|#)?\s*\d+"
CITE = re.compile(r"\[(" + REF + r"(?:\s*[,;]\s*" + REF + r")*)\]", re.IGNORECASE)


def validate_citations(report: str, reg: list[dict]) -> dict:
    """Drop citations to unknown sources, rebuild References, report stats.

    Checks citation integrity only - not whether the claim is supported.
    """
    valid = {s["id"] for s in reg}
    used, invalid = set(), set()

    def fix(m: re.Match) -> str:
        nums = [int(n) for n in re.findall(r"\d+", m.group(1))]
        keep = [n for n in nums if n in valid]
        invalid.update(n for n in nums if n not in valid)
        used.update(keep)
        return "[" + ", ".join(map(str, keep)) + "]" if keep else ""

    body = re.split(r"\n#+\s*References\b", report, maxsplit=1, flags=re.IGNORECASE)[0]
    body = CITE.sub(fix, body).rstrip()
    refs = "\n".join(f"{s['id']}. [{s['title'] or s['url']}]({s['url']})"
                      for s in reg if s["id"] in used)
    text = "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))
    paras = [p for p in re.split(r"\n\s*\n|\n(?=\s*[-*] )", text) if p.strip()]
    uncited = sum(1 for p in paras if not CITE.search(p))
    return {"report": body + "\n\n## References\n\n" + (refs or "_No sources cited._") + "\n",
            "cited": sorted(used), "invalid_removed": sorted(invalid),
            "uncited_paragraphs": uncited, "sources_total": len(reg)}
