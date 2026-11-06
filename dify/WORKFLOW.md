# Dify workflow: Deep Research (build spec)

Status: built and exported as research-agent.yml (DSL 0.7.0, Dify 1.19.0). After building it in Dify,
export DSL to dify/research-agent.yml and record the Dify version here.

Inputs: topic (text), depth (number, 3-5)

1. LLM "Planner" - Ollama qwen2.5:7b. Prompt: return ONLY a JSON array of
   {{depth}} search-style sub-questions about {{topic}}.
2. Code "Parse plan" - body of parse_plan() -> questions: array[string]
3. Iteration over questions (parallel mode, max 3):
   a. Tool "SearXNG Search" (base URL http://searxng:8080) -- or HTTP Request
      GET http://searxng:8080/search?q={{item}}&format=json
   b. Code "Pick results" - pick_results(body, k=3) -> results
   Output: array of results
4. Parallel branch (from step 2): Tool "Wikipedia" on {{topic}} for background.
5. Code "Build registry" - build_registry() + format_sources()
   -> registry (json string), sources_text
6. LLM "Writer" - Write a Markdown report on {{topic}} using ONLY the sources
   below. Cite as [n]. Do not invent sources. Sections: Summary, Findings,
   Open questions.
7. Code "Validate citations" - validate_citations(report, registry)
8. End: report, stats

Networking: Dify runs nodes server-side, so use http://searxng:8080 and
http://ollama:11434, never localhost. If HTTP Request is blocked, allow the
host in Dify's ssrf_proxy config rather than disabling it.
