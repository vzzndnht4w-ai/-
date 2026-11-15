"""Тонкий клиент fal.ai (очередь). Ключ подставляет прокси сессии — в код его вписывать не нужно."""
import json, subprocess, time, hashlib
from pathlib import Path
def _curl(args, timeout=120):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), "-w", "\n%{http_code}"] + args, capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n"); return int(code or 0), body
def run(model, args, poll=3, timeout=600):
    code, body = _curl(["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(args), f"https://queue.fal.run/{model}"])
    if code != 200: raise RuntimeError(f"fal submit {code}: {body[:300]}")
    j = json.loads(body); t0 = time.time()
    while True:
        c, b = _curl([j["status_url"]]); st = json.loads(b).get("status") if c == 200 else "ERR"
        if st == "COMPLETED": break
        if st in ("FAILED", "ERR") or time.time() - t0 > timeout: raise RuntimeError(f"fal status {st}: {b[:300]}")
        time.sleep(poll)
    c, b = _curl([j["response_url"]]);
    if c != 200: raise RuntimeError(f"fal result {c}: {b[:300]}")
    return json.loads(b)
def download(url, path):
    c, _ = _curl(["-L", "-o", str(path), url], 180); return c
