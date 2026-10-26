"""diagnostics_relay 的端到端测试：扮演只收推送诊断的客户端（和 Claude Code 一样），检查改动后能收到错误。

用法：python3 relay_test.py <diagnostics_relay.py 路径> [语言服务器命令...]（默认 tsc --lsp --stdio）
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time

RELAY = str(pathlib.Path(sys.argv[1]).resolve())  # 测试在临时目录里跑，相对路径会找不到
SERVER = sys.argv[2:] or ["tsc", "--lsp", "--stdio"]
work = pathlib.Path(tempfile.mkdtemp(prefix="relay-test-"))
failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (("  -- " + detail) if detail and not cond else ""))
    if not cond:
        failures.append(name)


proc = subprocess.Popen([sys.executable, RELAY, *SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, cwd=work)
msgs, lock = [], threading.Lock()


def send(obj):
    data = json.dumps(obj).encode()
    proc.stdin.write(b"Content-Length: %d\r\n\r\n" % len(data) + data)
    proc.stdin.flush()


def reader():
    f = proc.stdout
    while True:
        headers = {}
        while True:
            line = f.readline()
            if not line:
                return
            line = line.decode().strip()
            if not line:
                break
            k, v = line.split(":", 1)
            headers[k.lower()] = v.strip()
        m = json.loads(f.read(int(headers["content-length"])))
        with lock:
            msgs.append(m)
        if "id" in m and "method" in m:
            send({"jsonrpc": "2.0", "id": m["id"], "result": None})


threading.Thread(target=reader, daemon=True).start()


def mark():
    with lock:
        return len(msgs)


def pushes(since, uri=None):
    with lock:
        return [m["params"] for m in msgs[since:] if m.get("method") == "textDocument/publishDiagnostics"
                and (uri is None or m["params"]["uri"] == uri)]


def wait_push(since, uri, timeout=15, version=None):
    end = time.time() + timeout
    while time.time() < end:
        for p in pushes(since, uri):
            if version is None or p.get("version") == version:
                return p
        time.sleep(0.05)
    return None


def wait_id(i, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        with lock:
            for m in msgs:
                if m.get("id") == i and "method" not in m:
                    return m
        time.sleep(0.05)
    return None


def write(name, text):
    p = work / name
    p.write_text(text)
    return p.as_uri()


def open_doc(uri, lang, text):
    send({"jsonrpc": "2.0", "method": "textDocument/didOpen",
          "params": {"textDocument": {"uri": uri, "languageId": lang, "version": 1, "text": text}}})


def change(uri, version, text):
    send({"jsonrpc": "2.0", "method": "textDocument/didChange",
          "params": {"textDocument": {"uri": uri, "version": version}, "contentChanges": [{"text": text}]}})


(work / "tsconfig.json").write_text('{"compilerOptions": {"strict": true, "checkJs": true}}')
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "processId": None, "rootUri": work.as_uri(), "workspaceFolders": [{"uri": work.as_uri(), "name": "t"}],
    "capabilities": {"textDocument": {"publishDiagnostics": {"versionSupport": True}, "hover": {}}}}})
check("initialize answered through relay", (wait_id(1) or {}).get("result") is not None)
send({"jsonrpc": "2.0", "method": "initialized", "params": {}})

# 1. single file: open with error, fix, break again
a_bad = 'const n: number = "x";\n'
a = write("a.ts", a_bad)
s = mark(); open_doc(a, "typescript", a_bad)
p = wait_push(s, a, version=1)
check("open a.ts pushes 1 error", p is not None and len(p["diagnostics"]) == 1, json.dumps(p))
s = mark(); change(a, 2, "const n: number = 1;\n")
p = wait_push(s, a, version=2)
check("fixing a.ts pushes 0 errors", p is not None and p["diagnostics"] == [], json.dumps(p))
s = mark(); change(a, 3, 'const n: number = "x";\nconst b: boolean = 1;\n')
p = wait_push(s, a, version=3)
check("breaking a.ts again pushes 2 errors", p is not None and len(p["diagnostics"]) == 2, json.dumps(p))

# 2. passthrough request
send({"jsonrpc": "2.0", "id": 2, "method": "textDocument/hover",
      "params": {"textDocument": {"uri": a}, "position": {"line": 0, "character": 6}}})
h = wait_id(2)
check("hover passes through", h is not None and "number" in json.dumps(h.get("result")), json.dumps(h))

# 3. cross-file: changing lib.ts signature re-pushes use.ts
lib_v1 = "export function f(n: number): number { return n; }\n"
use_text = 'import { f } from "./lib";\nf(1);\n'
lib = write("lib.ts", lib_v1)
use = write("use.ts", use_text)
s = mark(); open_doc(lib, "typescript", lib_v1); open_doc(use, "typescript", use_text)
p = wait_push(s, use, version=1)
check("open use.ts pushes 0 errors", p is not None and p["diagnostics"] == [], json.dumps(p))
time.sleep(1)
s = mark(); change(lib, 2, "export function f(s: string): string { return s; }\n")
p = wait_push(s, use)
check("changing lib.ts signature pushes the new error in use.ts", p is not None and len(p["diagnostics"]) == 1, json.dumps(p))
check("changing lib.ts also pushes lib.ts itself", wait_push(s, lib, version=2) is not None)
time.sleep(1)
check("unchanged a.ts is not re-pushed when lib.ts changes", pushes(s, a) == [], json.dumps(pushes(s, a)))

# 4. JS with @ts-check
js_text = '// @ts-check\n/** @param {string} s */\nfunction g(s) { return s; }\ng(1);\n'
js = write("b.js", js_text)
s = mark(); open_doc(js, "javascript", js_text)
p = wait_push(s, js, version=1)
check("open b.js pushes its type error", p is not None and len(p["diagnostics"]) == 1, json.dumps(p))

# 5. close clears diagnostics
s = mark()
send({"jsonrpc": "2.0", "method": "textDocument/didClose", "params": {"textDocument": {"uri": use}}})
p = wait_push(s, use)
check("closing use.ts pushes empty diagnostics", p is not None and p["diagnostics"] == [], json.dumps(p))

# 6. burst of edits: only the latest version gets pushed for a.ts
s = mark()
for v in range(4, 9):
    change(a, v, "const n: number = %d;\n" % v + ('const z: string = 0;\n' if v == 8 else ""))
p = wait_push(s, a, version=8)
time.sleep(0.5)
stale = [q for q in pushes(s, a) if q.get("version") != 8]
check("burst of edits pushes the final version with 1 error", p is not None and len(p["diagnostics"]) == 1, json.dumps(p))
check("burst of edits pushes no stale versions", stale == [], json.dumps(stale))

# 7. shutdown / exit
send({"jsonrpc": "2.0", "id": 3, "method": "shutdown"})
check("shutdown answered", wait_id(3) is not None)
send({"jsonrpc": "2.0", "method": "exit"})
try:
    code = proc.wait(10)
except subprocess.TimeoutExpired:
    proc.kill(); code = "timeout"
check("relay exits 0 after exit", code == 0, "code=%s stderr=%s" % (code, proc.stderr.read().decode()[-500:]))

# 8. missing server command fails loudly
bad = subprocess.run([sys.executable, RELAY, "no-such-language-server"], capture_output=True, input=b"", timeout=10)
check("missing server exits non-zero with message", bad.returncode != 0 and "no-such-language-server" in bad.stderr.decode(),
      "rc=%s stderr=%s" % (bad.returncode, bad.stderr.decode()))

shutil.rmtree(work)
print("\n%d failure(s)" % len(failures))
sys.exit(1 if failures else 0)
