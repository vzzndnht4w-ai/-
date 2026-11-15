"""Клиент GPTunnel Creative Lab (генерация картинок/видео). Ключ подставляет прокси сессии (заголовок Authorization для gptunnel.ru).
Документация: https://docs.gptunnel.ru/creative-lab/"""
import base64, json, subprocess, time
from pathlib import Path
BASE = "https://gptunnel.ru/api/v2/media"
def _req(method, path, body=None, timeout=120):
    args = ["curl", "-s", "-m", str(timeout), "-w", "\n%{http_code}", "-X", method, "-H", "Content-Type: application/json"]
    stdin = None
    if body is not None: args += ["--data-binary", "@-"]; stdin = json.dumps(body)
    r = subprocess.run(args + [BASE + path], input=stdin, capture_output=True, text=True)
    txt, _, code = r.stdout.rpartition("\n")
    try: return int(code or 0), json.loads(txt)
    except Exception: return int(code or 0), {"raw": txt[:300]}
def models(type=None):
    c, j = _req("GET", "/models" + (f"?type={type}" if type else "")); return c, j
def price(model, params=None, prompt=None, inputs=None):
    body = {"model": model}; body.update({k: v for k, v in (("params", params), ("prompt", prompt), ("inputs", inputs)) if v})
    return _req("POST", "/price", body)
def data_url(path):
    mime = "image/png" if str(path).lower().endswith("png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()
def create(model, prompt=None, params=None, inputs=None, idem=None, wait=False):
    body = {"model": model}
    for k, v in (("prompt", prompt), ("params", params), ("inputs", inputs), ("idempotency_key", idem)):
        if v: body[k] = v
    if wait: body["wait"] = True
    return _req("POST", "/tasks", body, 180)
def result(task_id, every=6, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        c, j = _req("GET", f"/tasks/{task_id}")
        if c == 200 and j.get("status") in ("done", "failed"): return j
        time.sleep(every)
    raise TimeoutError(task_id)
def download(url, path):
    r = subprocess.run(["curl", "-s", "-L", "-m", "240", "-o", str(path), "-w", "%{http_code}", url], capture_output=True, text=True); return r.stdout.strip()
