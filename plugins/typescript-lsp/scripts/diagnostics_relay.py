"""diagnostics_relay：夹在 Claude Code 和只支持「拉取式」诊断的语言服务器之间，把诊断改成推送。

TypeScript 7 自带的 tsc --lsp 只在客户端发 textDocument/diagnostic 请求时才给错误，从不主动推送
textDocument/publishDiagnostics；Claude Code 只认推送，所以改完文件收不到类型错误。本脚本原样转发
双方的消息，另外在文档打开、改动、保存后主动向服务器要诊断，再以推送的形式发给 Claude Code。

用法：python3 diagnostics_relay.py <语言服务器命令> [参数...]
"""
import json
import os
import subprocess
import sys
import threading

PULL_DELAY = 0.05  # 秒：一串连续改动合并成一轮拉取
MAX_RETRIES = 3  # 服务器回「内容已变 / 已取消」时，同一版本最多重拉几次
RETRY_CODES = (-32801, -32802)  # ContentModified、ServerCancelled：服务器要求重新请求
RELAY_ID_PREFIX = "diagnostics-relay:"  # 本脚本自己发出的请求 id，回应不转给 Claude Code


def log(message):
    print("[diagnostics-relay] " + message, file=sys.stderr, flush=True)


def read_message(stream, source):
    """读一条 LSP 消息；对端正常关闭时返回 None。"""
    length = None
    while True:
        line = stream.readline()
        if not line:
            if length is None:
                return None
            raise RuntimeError(source + " 在消息头中途断开")
        line = line.strip()
        if not line:
            break
        name, _, value = line.partition(b":")
        if name.strip().lower() == b"content-length":
            length = int(value)
    if length is None:
        raise RuntimeError(source + " 发来的消息缺少 Content-Length 头")
    body = stream.read(length)
    if len(body) < length:
        raise RuntimeError("%s 的消息只收到 %d/%d 字节就断开了" % (source, len(body), length))
    return json.loads(body)


def write_message(stream, message):
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    stream.write(b"Content-Length: %d\r\n\r\n" % len(body) + body)
    stream.flush()


class Relay:
    def __init__(self, command):
        self.server = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.server_lock = threading.Lock()  # 写语言服务器的 stdin
        self.client_lock = threading.Lock()  # 写 Claude Code（本进程的 stdout）
        self.lock = threading.Lock()  # 保护下面的状态
        self.documents = {}  # 打开着的文档：uri -> {"version", "result_id", "pushed"}
        self.dirty = set()  # 等着拉取诊断的文档
        self.forced = set()  # 拉到后不管有没有变化都要推送的文档（刚打开或刚改动的）
        self.retries = {}  # uri -> 当前版本已重拉次数
        self.pending = {}  # 本脚本发出的拉取请求 id -> (uri, version, forced, retries)
        self.next_id = 0
        self.ready = False  # Claude Code 发出 initialized 之后才能向服务器发请求
        self.stopping = False
        self.timer = None

    def send_server(self, message):
        with self.server_lock:
            try:
                write_message(self.server.stdin, message)
            except (BrokenPipeError, ValueError):
                log("语言服务器已退出，丢弃发给它的消息：%s" % message.get("method", message.get("id")))

    def send_client(self, message):
        with self.client_lock:
            write_message(sys.stdout.buffer, message)

    def publish(self, uri, version, items):
        params = {"uri": uri, "diagnostics": items}
        if version is not None:
            params["version"] = version
        self.send_client({"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics", "params": params})

    # ---- Claude Code -> 语言服务器 ----

    def from_client(self, message):
        self.send_server(message)
        method = message.get("method")
        if method == "exit":
            self.close_server_stdin()  # tsc --lsp 收到 exit 后要等 stdin 关闭才真正退出
            return
        document = (message.get("params") or {}).get("textDocument") or {}
        uri = document.get("uri")
        closed = None
        with self.lock:
            if method == "initialized":
                self.ready = True
            elif method == "textDocument/didOpen":
                self.documents[uri] = {"version": document.get("version"), "result_id": None, "pushed": None}
                self.mark_changed(uri)
            elif method in ("textDocument/didChange", "textDocument/didSave") and uri in self.documents:
                if method == "textDocument/didChange":
                    self.documents[uri]["version"] = document.get("version")
                self.mark_changed(uri)
            elif method == "textDocument/didClose":
                self.documents.pop(uri, None)
                self.dirty.discard(uri)
                self.forced.discard(uri)
                self.retries.pop(uri, None)
                closed = uri
            elif method == "shutdown":
                self.stopping = True
            self.schedule()
        if closed is not None:
            self.publish(closed, None, [])

    def mark_changed(self, uri):
        # 一个文件改了可能影响别的文件（比如改了导出的函数签名），所以打开着的文档全部重拉；
        # 只有改动的这个文件必推，其余的诊断有变化才推
        self.forced.add(uri)
        self.retries.pop(uri, None)
        self.dirty.update(self.documents)

    def schedule(self):
        if not self.ready or self.stopping or not self.dirty:
            return
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(PULL_DELAY, self.pull)
        self.timer.daemon = True
        self.timer.start()

    def pull(self):
        requests = []
        with self.lock:
            if self.stopping:
                return
            for uri in self.dirty:
                document = self.documents.get(uri)
                if document is None:
                    continue
                request_id = RELAY_ID_PREFIX + str(self.next_id)
                self.next_id += 1
                self.pending[request_id] = (uri, document["version"], uri in self.forced, self.retries.get(uri, 0))
                params = {"textDocument": {"uri": uri}}
                if document["result_id"]:
                    params["previousResultId"] = document["result_id"]
                requests.append({"jsonrpc": "2.0", "id": request_id, "method": "textDocument/diagnostic", "params": params})
            self.dirty.clear()
            self.forced.clear()
        for request in requests:
            self.send_server(request)

    # ---- 语言服务器 -> Claude Code ----

    def from_server(self, message):
        request_id = message.get("id")
        if "method" not in message and isinstance(request_id, str) and request_id.startswith(RELAY_ID_PREFIX):
            self.on_pull_response(message)
        elif message.get("method") == "workspace/diagnostic/refresh":
            # 服务器要求重拉所有诊断（比如 tsconfig 变了）；Claude Code 不拉，由本脚本代答
            self.send_server({"jsonrpc": "2.0", "id": request_id, "result": None})
            with self.lock:
                self.dirty.update(self.documents)
                self.schedule()
        else:
            self.send_client(message)

    def on_pull_response(self, message):
        to_publish = []
        with self.lock:
            pull = self.pending.pop(message["id"], None)
            if pull is None:
                log("收到一个没有对应请求的诊断回应：%s" % message["id"])
                return
            uri, version, forced, retries = pull
            document = self.documents.get(uri)
            if document is None or document["version"] != version:
                return  # 文档已关闭，或拉取期间又改了（新一轮拉取已经排上）
            error = message.get("error")
            if error:
                retrigger = (error.get("data") or {}).get("retriggerRequest", True)
                if error.get("code") in RETRY_CODES and retrigger and retries < MAX_RETRIES:
                    self.retries[uri] = retries + 1
                    self.dirty.add(uri)
                    if forced:
                        self.forced.add(uri)
                    self.schedule()
                else:
                    log("拉取 %s 的诊断失败：%s %s" % (uri, error.get("code"), error.get("message")))
                return
            self.retries.pop(uri, None)
            report = message.get("result") or {}
            to_publish += self.take_report(uri, document, report, forced)
            for related_uri, related in (report.get("relatedDocuments") or {}).items():
                related_document = self.documents.get(related_uri)
                if related_document is not None:
                    to_publish += self.take_report(related_uri, related_document, related, False)
        for uri, version, items in to_publish:
            self.publish(uri, version, items)

    def take_report(self, uri, document, report, forced):
        kind = report.get("kind")
        if kind == "unchanged":
            document["result_id"] = report.get("resultId")
            if forced and document["pushed"] is not None:
                return [(uri, document["version"], document["pushed"])]
            return []
        if kind != "full":
            log("%s 的诊断报告类型未知：%r，没有推送" % (uri, kind))
            return []
        document["result_id"] = report.get("resultId")
        items = report.get("items") or []
        if not forced and items == document["pushed"]:
            return []
        document["pushed"] = items
        return [(uri, document["version"], items)]

    # ---- 运行 ----

    def pump(self, stream, source, handle):
        try:
            while True:
                message = read_message(stream, source)
                if message is None:
                    return
                handle(message)
        except Exception as error:  # 消息坏了就整体停掉，让 Claude Code 看到语言服务器退出
            log("处理%s的消息时出错：%r" % (source, error))
            self.server.kill()
            os._exit(1)

    def pump_client(self):
        self.pump(sys.stdin.buffer, "Claude Code", self.from_client)
        self.close_server_stdin()  # Claude Code 断开了：让语言服务器也收尾退出

    def close_server_stdin(self):
        with self.server_lock:
            self.server.stdin.close()


def finish(code):
    # 读 Claude Code 的线程还卡在 stdin 上，正常退出时解释器收尾会因此崩溃，所以刷完输出直接退
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


def main():
    command = sys.argv[1:]
    if not command:
        log("缺少语言服务器命令。用法：python3 diagnostics_relay.py <命令> [参数...]")
        sys.exit(2)
    try:
        relay = Relay(command)
    except OSError as error:
        log("启动语言服务器 %s 失败：%s" % (command[0], error))
        sys.exit(1)
    threading.Thread(target=relay.pump_client, daemon=True).start()
    relay.pump(relay.server.stdout, "语言服务器", relay.from_server)
    code = relay.server.wait()
    if code < 0:
        log("语言服务器被信号 %d 终止" % -code)
        finish(1)
    if code != 0:
        log("语言服务器退出，退出码 %d" % code)
    finish(code)


if __name__ == "__main__":
    main()
