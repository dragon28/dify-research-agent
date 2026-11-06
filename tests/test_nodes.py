from research_agent.nodes import (
    build_registry,
    normalize_url,
    parse_plan,
    pick_results,
    validate_citations,
)


def test_parse_plan_json_and_fallback():
    assert parse_plan('Sure! ["What is X?", "Why X?", "what is x?"]', "X") == ["What is X?", "Why X?"]
    assert parse_plan("1. What is X?\n2. How?\nnoise", "X") == ["What is X?", "How?"]
    assert parse_plan("garbage", "topic") == ["topic"]


def test_normalize_url_strips_tracking():
    a = normalize_url("http://www.Example.com/a/?utm_source=x&id=2#frag")
    assert a == "https://example.com/a?id=2"


def test_pick_results_dedupes_and_limits():
    data = {"results": [
        {"url": "https://a.com/x", "title": "A", "content": "s"},
        {"url": "https://www.a.com/x/?utm_medium=y", "title": "A dup"},
        {"url": "ftp://bad", "title": "bad"},
        {"url": "https://b.com", "title": "B"},
        {"url": "https://c.com", "title": "C"}]}
    out = pick_results(data, k=2)
    assert [r["title"] for r in out] == ["A", "B"]


def test_pick_results_empty():
    assert pick_results('{"results": []}') == []


def test_registry_stable_ids_across_questions():
    reg = build_registry([[{"url": "https://a.com", "title": "A", "snippet": ""}],
                          [{"url": "https://a.com/", "title": "A2", "snippet": ""},
                           {"url": "https://b.com", "title": "B", "snippet": ""}]])
    assert [(s["id"], s["title"]) for s in reg] == [(1, "A"), (2, "B")]


def test_validate_citations_removes_unknown_and_rebuilds_refs():
    reg = [{"id": 1, "title": "A", "url": "https://a.com", "snippet": ""},
           {"id": 2, "title": "B", "url": "https://b.com", "snippet": ""}]
    report = "# T\n\nFact one [1].\n\nFact two [2, 7].\n\nMade up [9].\n\n## References\n1. fake"
    res = validate_citations(report, reg)
    assert res["cited"] == [1, 2]
    assert res["invalid_removed"] == [7, 9]
    assert res["uncited_paragraphs"] == 1
    assert "[2]" in res["report"] and "[9]" not in res["report"] and "fake" not in res["report"]
    assert "1. [A](https://a.com)" in res["report"]
