"""Bootstrap a fresh, throwaway Dify instance and publish the research workflow.

Used by GitHub Actions. Creates a random admin (never a real account), installs
the Ollama plugin, registers the model, imports dify/research-agent.yml,
publishes it and prints an app API key to $GITHUB_ENV (masked).

Usage: python scripts/ci_bootstrap.py [--base-url http://localhost] [--model qwen2.5:7b]
"""

import argparse
import base64
import http.cookiejar
import io
import json
import os
import pathlib
import secrets
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROVIDER = "langgenius/ollama/ollama"
UA = {"User-Agent": "Mozilla/5.0 dify-research-agent-ci"}


class Console:
    def __init__(self, base: str):
        self.base = base.rstrip("/") + "/console/api"
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def csrf(self) -> str:
        for c in self.jar:
            if c.name.endswith("csrf_token"):
                return c.value
        return ""

    def call(self, path, method="GET", body=None, raw=False):
        h = {"Content-Type": "application/json", "X-CSRF-Token": self.csrf()}
        req = urllib.request.Request(self.base + path, method=method, headers=h,
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with self.op.open(req, timeout=120) as r:
                data = r.read()
                code = r.status
        except urllib.error.HTTPError as e:
            data, code = e.read(), e.code
        if raw:
            return code, data
        try:
            return code, json.loads(data)
        except ValueError:
            return code, data.decode("utf-8", "replace")


def must(res, what):
    code, body = res
    if code >= 300:
        sys.exit(f"{what} failed: HTTP {code} {str(body)[:500]}")
    return body


def wait_ready(c: Console, tries=90):
    for _ in range(tries):
        try:
            code, _ = c.call("/setup")
            if code == 200:
                return
        except OSError:
            pass
        time.sleep(5)
    sys.exit("Dify API never became ready")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://localhost")
    ap.add_argument("--model", default="qwen2.5:7b")
    a = ap.parse_args()
    gh_env = os.environ.get("GITHUB_ENV")

    c = Console(a.base_url)
    wait_ready(c)
    email = "ci@example.invalid"
    pw = "Ci" + secrets.token_urlsafe(18) + "9"
    if gh_env:
        print(f"::add-mask::{pw}")
    _, st = c.call("/setup")
    if isinstance(st, dict) and st.get("step") != "finished":
        must(c.call("/setup", "POST", {"email": email, "name": "ci", "password": pw}), "setup")
    enc = base64.b64encode(pw.encode()).decode()
    must(c.call("/login", "POST", {"email": email, "password": enc, "remember_me": True}), "login")
    print("signed in")

    meta = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://marketplace.dify.ai/api/v1/plugins/langgenius/ollama", headers=UA), timeout=60))
    ident = meta["data"]["plugin"]["latest_package_identifier"]
    r = must(c.call("/workspaces/current/plugin/install/marketplace", "POST",
                    {"plugin_unique_identifiers": [ident]}), "plugin install")
    tid = r.get("task_id")
    for _ in range(60):
        if not tid:
            break
        time.sleep(5)
        t = must(c.call(f"/workspaces/current/plugin/tasks/{tid}"), "plugin task")["task"]
        if t["status"] == "success":
            break
        if t["status"] == "failed":
            sys.exit(f"plugin install failed: {t}")
    print("ollama plugin:", ident)

    cred = {"base_url": "http://ollama:11434", "mode": "chat", "context_size": "16384",
            "max_tokens": "4096", "vision_support": "false", "function_call_support": "false"}
    must(c.call(f"/workspaces/current/model-providers/{PROVIDER}/models/credentials", "POST",
                {"model": a.model, "model_type": "llm", "credentials": cred, "name": "ci"}),
         "model credentials")
    must(c.call("/workspaces/current/default-model", "POST", {"model_settings": [
        {"model_type": "llm", "provider": PROVIDER, "model": a.model}]}), "default model")

    dsl = (ROOT / "dify" / "research-agent.yml").read_text().replace("qwen2.5:7b", a.model)
    imp = must(c.call("/apps/imports", "POST", {"mode": "yaml-content", "yaml_content": dsl}),
               "import")
    if imp.get("status") == "pending":
        imp = must(c.call(f"/apps/imports/{imp['id']}/confirm", "POST", {}), "import confirm")
    if imp.get("status") == "failed":
        sys.exit(f"import failed: {imp}")
    app = imp["app_id"]
    must(c.call(f"/apps/{app}/workflows/publish", "POST", {}), "publish")
    key = must(c.call(f"/apps/{app}/api-keys", "POST", {}), "api key")["token"]

    code, z = c.call(f"/apps/{app}/export?include_secret=false", raw=True)
    if code == 200 and z[:2] == b"PK":
        out = ROOT / "build" / "exported-app.yml"
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(zipfile.ZipFile(io.BytesIO(z)).read("app.yaml"))

    if gh_env:
        print(f"::add-mask::{key}")
        with open(gh_env, "a") as f:
            f.write(f"DIFY_API_KEY={key}\nDIFY_BASE_URL={a.base_url.rstrip('/')}/v1\n")
    else:
        print(f"DIFY_API_KEY={key}")
    print("workflow published:", app)


if __name__ == "__main__":
    main()
