"""Generate dify/research-agent.yml from research_agent/nodes.py.

The Code-node bodies are the same tested functions, inlined (Dify's sandbox
cannot import this package). Run: uv run python scripts/build_dsl.py
"""

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB = (ROOT / "research_agent" / "nodes.py").read_text()
LIB = re.sub(r"^from __future__ import annotations\n", "", LIB, flags=re.MULTILINE)

MODEL = {"provider": "langgenius/ollama/ollama", "name": "qwen2.5:7b", "mode": "chat",
         "completion_params": {"temperature": 0.2, "num_ctx": 16384}}
SEARX = "http://searxng:8080/search"


def code(body: str) -> str:
    return LIB + "\n\n" + body.strip() + "\n"


def node(id_, data, x, y, parent=None):
    n = {"id": id_, "type": "custom", "position": {"x": x, "y": y},
         "positionAbsolute": {"x": x, "y": y}, "width": 244, "height": 90,
         "sourcePosition": "right", "targetPosition": "left",
         "data": {"desc": "", "selected": False, **data}}
    if parent:
        n["parentId"] = parent
        n["zIndex"] = 1002
        n["data"].update({"isInIteration": True, "isInLoop": False, "iteration_id": parent})
    return n


def edge(s, t, st, tt, parent=None):
    d = {"sourceType": st, "targetType": tt, "isInIteration": bool(parent), "isInLoop": False}
    if parent:
        d["iteration_id"] = parent
    return {"id": f"{s}-{t}", "source": s, "target": t, "sourceHandle": "source",
            "targetHandle": "target", "type": "custom", "zIndex": 1002 if parent else 0,
            "data": d}


def http(title, q_template):
    return {"type": "http-request", "title": title, "method": "get", "url": SEARX,
            "authorization": {"type": "no-auth", "config": None}, "headers": "",
            "params": f"q:{q_template}\nformat:json",
            "body": {"type": "none", "data": []},
            "timeout": {"connect": 10, "read": 30, "write": 30},
            "retry_config": {"enabled": True, "max_retries": 2, "retry_interval": 1000},
            "error_strategy": "default-value",
            "default_value": [{"key": "body", "type": "string", "value": '{"results": []}'},
                              {"key": "status_code", "type": "number", "value": 0}]}


def llm(title, system, user):
    return {"type": "llm", "title": title, "model": MODEL,
            "prompt_template": [{"role": "system", "text": system},
                                {"role": "user", "text": user}],
            "context": {"enabled": False, "variable_selector": []},
            "vision": {"enabled": False}, "memory": None}


ITER = "iter"
nodes = [
    node("start", {"type": "start", "title": "Start", "variables": [
        {"variable": "topic", "label": "topic", "type": "paragraph", "required": True,
         "max_length": 500, "options": []},
        {"variable": "depth", "label": "depth (3-5)", "type": "number", "required": False,
         "options": []}]}, 0, 300),
    node("planner", llm(
        "Planner",
        "You plan web research. Reply with ONLY a JSON array of short search-engine "
        "queries (strings). No prose.",
        "Topic: {{#start.topic#}}\nWrite {{#start.depth#}} (default 4) distinct search "
        "queries that together cover background, current state, key players or tools, "
        "and open problems."), 300, 200),
    node("parse", {"type": "code", "title": "Parse plan", "code_language": "python3",
                   "variables": [
                       {"variable": "text", "value_selector": ["planner", "text"]},
                       {"variable": "topic", "value_selector": ["start", "topic"]},
                       {"variable": "depth", "value_selector": ["start", "depth"]}],
                   "outputs": {"questions": {"type": "array[string]", "children": None}},
                   "code": code("""
def main(text: str, topic: str, depth=None) -> dict:
    n = int(depth) if depth else 4
    return {"questions": parse_plan(text, topic, max(3, min(n, 5)))}
""")}, 600, 200),
    {"id": ITER, "type": "custom", "position": {"x": 900, "y": 150},
     "positionAbsolute": {"x": 900, "y": 150}, "width": 640, "height": 200, "zIndex": 1,
     "data": {"type": "iteration", "title": "Search each question", "desc": "",
              "selected": False, "iterator_selector": ["parse", "questions"],
              "iterator_input_type": "array[string]",
              "output_selector": ["pick", "results_json"], "output_type": "array[string]",
              "start_node_id": f"{ITER}start", "is_parallel": True, "parallel_nums": 3,
              "error_handle_mode": "continue-on-error", "width": 640, "height": 200}},
    {"id": f"{ITER}start", "type": "custom-iteration-start", "parentId": ITER,
     "position": {"x": 24, "y": 68}, "positionAbsolute": {"x": 924, "y": 218},
     "width": 44, "height": 48, "zIndex": 1002, "draggable": False, "selectable": False,
     "data": {"type": "iteration-start", "title": "", "desc": "", "isInIteration": True,
              "selected": False}},
    node("search", http("SearXNG search", "{{#iter.item#}}"), 1000, 230, ITER),
    node("pick", {"type": "code", "title": "Dedupe + top 3", "code_language": "python3",
                  "variables": [{"variable": "body", "value_selector": ["search", "body"]}],
                  "outputs": {"results_json": {"type": "string", "children": None}},
                  "code": code("""
def main(body: str) -> dict:
    try:
        res = pick_results(body or '{"results": []}', k=3)
    except Exception:
        res = []
    return {"results_json": json.dumps(res)}
""")}, 1300, 230, ITER),
    node("wiki", http("Wikipedia via SearXNG (parallel)", "!wp {{#start.topic#}}"), 900, 450),
    node("registry", {"type": "code", "title": "Build source registry",
                      "code_language": "python3",
                      "variables": [
                          {"variable": "per_q", "value_selector": [ITER, "output"]},
                          {"variable": "wiki", "value_selector": ["wiki", "body"]}],
                      "outputs": {"registry": {"type": "string", "children": None},
                                  "sources_text": {"type": "string", "children": None}},
                      "code": code("""
def main(per_q: list, wiki: str) -> dict:
    lists = []
    for s in per_q or []:
        try:
            lists.append(json.loads(s) if s else [])
        except Exception:
            pass
    try:
        lists.insert(0, pick_results(wiki or '{"results": []}', k=1))
    except Exception:
        pass
    reg = build_registry(lists)
    return {"registry": json.dumps(reg), "sources_text": format_sources(reg)}
""")}, 1650, 300),
    node("writer", llm(
        "Writer",
        "You write concise, factual research briefs in Markdown. Use ONLY the numbered "
        "sources provided. Cite every factual sentence with [n] matching a source number. "
        "Never invent sources, URLs or numbers. If sources are thin, say so.",
        "Topic: {{#start.topic#}}\n\nSources:\n{{#registry.sources_text#}}\n\nWrite the "
        "report with sections: '# <title>', '## Summary', '## Findings', "
        "'## Open questions'. Do not write a References section."), 1950, 300),
    node("validate", {"type": "code", "title": "Validate citations",
                      "code_language": "python3",
                      "variables": [
                          {"variable": "report", "value_selector": ["writer", "text"]},
                          {"variable": "registry", "value_selector": ["registry", "registry"]}],
                      "outputs": {"report": {"type": "string", "children": None},
                                  "stats": {"type": "string", "children": None}},
                      "code": code("""
def main(report: str, registry: str) -> dict:
    res = validate_citations(report or "", json.loads(registry or "[]"))
    out = res.pop("report")
    return {"report": out, "stats": json.dumps(res)}
""")}, 2250, 300),
    node("end", {"type": "end", "title": "End", "outputs": [
        {"variable": "report", "value_selector": ["validate", "report"],
         "value_type": "string"},
        {"variable": "stats", "value_selector": ["validate", "stats"],
         "value_type": "string"}]}, 2550, 300),
]

edges = [
    edge("start", "planner", "start", "llm"),
    edge("start", "wiki", "start", "http-request"),
    edge("planner", "parse", "llm", "code"),
    edge("parse", ITER, "code", "iteration"),
    edge(f"{ITER}start", "search", "iteration-start", "http-request", ITER),
    edge("search", "pick", "http-request", "code", ITER),
    edge(ITER, "registry", "iteration", "code"),
    edge("wiki", "registry", "http-request", "code"),
    edge("registry", "writer", "code", "llm"),
    edge("writer", "validate", "llm", "code"),
    edge("validate", "end", "code", "end"),
]

dsl = {
    "app": {"name": "Deep Research Agent", "mode": "workflow", "icon": "🔎",
            "icon_background": "#E0F2FE", "use_icon_as_answer_icon": False,
            "description": "Plan -> SearXNG search (iteration) + Wikipedia (parallel) -> "
                           "cited Markdown report with citation validation."},
    "kind": "app", "version": "0.3.1",
    "dependencies": [{"type": "marketplace", "value": {
        "marketplace_plugin_unique_identifier":
            "langgenius/ollama:1.0.3@1086758302d98263d5b7881de8ba95fc219351fdf97831d18a7807378674d203"}}],
    "workflow": {"conversation_variables": [], "environment_variables": [],
                 "features": {}, "graph": {"nodes": nodes, "edges": edges,
                                           "viewport": {"x": 0, "y": 0, "zoom": 0.6}}},
}

out = ROOT / "dify" / "research-agent.generated.yml"
out.write_text(yaml.safe_dump(dsl, sort_keys=False, allow_unicode=True))
print(f"wrote {out}")
