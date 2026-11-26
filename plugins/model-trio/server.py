#!/usr/bin/env python3
"""model-trio 的 MCP 服务器：把任务交给本机的 Codex 和 Antigravity 命令行。

stdio 传输，每行一条 JSON-RPC 消息。每次工具调用起一个子进程，等它结束，返回它最后的汇报。
调用可能持续几分钟到一个多小时：Claude Code 会把超过两分钟的调用转到后台，这里不用自己管。
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.abspath(__file__))
PROTOCOL = "2025-06-18"

CODEX_RULES = """

---
调用方追加的固定规矩：
- 不提交、不推送、不切换分支，这些由调用方做。
- 这一轮结束即停止，运行中无法与调用方对话。最后一条消息就是交给调用方的汇报：写清结论、依据（文件:行号，或命令和结果）、没做完或没验证的部分。
"""

CODEX_REVIEW_RULES = """

---
调用方追加的固定规矩：
- 每条发现写清位置（文件:行号）和具体出错场景：什么输入或操作下，出什么错。
"""

AGY_PROMPT = """项目目录：{cwd}（只读）。你当前所在的目录是空的，不是项目。

{task}

---
调用方追加的固定规矩：
- 只读：不修改任何文件，只给意见。
- 运行中无法与调用方对话，最后一条回复就是交给调用方的全部内容。
- 没有对照代码核实过的判断，标明「推测」。
"""

TOOLS = [
    {
        "name": "codex",
        "description": "把一项任务交给本机的 Codex 命令行，等它做完，返回它的汇报和 session_id。"
        "Codex 只看得到 task 和 cwd 下的文件，看不到当前对话；它运行在沙箱里，不联网，不提交。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "任务书。mode 为 review 时写审查范围（如未提交的改动，或 <基线>...HEAD）和希望重点看的地方。",
                },
                "cwd": {"type": "string", "description": "工作目录的绝对路径，须在 git 工作副本里。"},
                "mode": {
                    "type": "string",
                    "enum": ["read", "write", "review"],
                    "description": "read：只读调研。write：可以改 cwd 下的文件。review：用 Codex 自带的审查流程，只读。",
                },
                "session_id": {"type": "string", "description": "续接之前那个 Codex 会话（追加要求、返工）。review 不能续接。"},
                "model": {"type": "string", "description": "不给就用用户 Codex 设置里的模型。"},
                "effort": {"type": "string", "description": "思考强度，如 high、xhigh。不给就用用户 Codex 设置里的。"},
            },
            "required": ["task", "cwd", "mode"],
        },
    },
    {
        "name": "antigravity",
        "description": "向本机的 Antigravity 命令行（Gemini）提一个问题，或请它出一份方案，等它答完，返回回复和 conversation_id。"
        "它只看得到 task，看不到当前对话；能读 cwd 下的文件、运行只读命令，不能改任何文件。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "问题或任务，连同它需要的背景。"},
                "cwd": {"type": "string", "description": "项目目录的绝对路径，Antigravity 只能读这个目录。"},
                "conversation_id": {"type": "string", "description": "续接之前那次对话（追问）。"},
                "model": {"type": "string", "description": "不给就用 Antigravity 的默认模型；可选的名字见 `agy models`。"},
            },
            "required": ["task", "cwd"],
        },
    },
]

running = {}  # 请求编号 -> 正在运行的子进程
write_lock = threading.Lock()


class Cancelled(Exception):
    pass


def send(message):
    with write_lock:
        sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def run(request_id, argv, cwd, stdin_text=None, env=None):
    """运行子进程到结束，返回（退出码，标准输出，标准错误）。子进程自成一个进程组，取消时整组停掉。"""
    proc = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL if stdin_text is None else subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    running[request_id] = proc
    out, err = proc.communicate(stdin_text)
    if running.pop(request_id, None) is None:
        raise Cancelled()
    return proc.returncode, out, err


def stop(proc):
    os.killpg(proc.pid, signal.SIGTERM)


def failure(what, code, out, err):
    return "%s（退出码 %s）。\n--- 标准输出末尾 ---\n%s\n--- 标准错误末尾 ---\n%s" % (what, code, out[-2000:], err[-2000:]), True


def codex(request_id, args):
    mode, session = args["mode"], args.get("session_id")
    config = ['approval_policy="never"', 'sandbox_mode="%s"' % ("workspace-write" if mode == "write" else "read-only")]
    if args.get("model"):
        # 审查流程优先用 review_model，所以两个都设
        config += ['model="%s"' % args["model"], 'review_model="%s"' % args["model"]]
    if args.get("effort"):
        config.append('model_reasoning_effort="%s"' % args["effort"])

    argv = ["codex", "exec"]
    if mode == "review":
        if session:
            return "review 每次新开一个 Codex 会话，不能带 session_id。", True
        argv.append("review")
    elif session:
        argv.append("resume")
    with tempfile.TemporaryDirectory() as tmp:
        report_file = os.path.join(tmp, "report.md")
        argv += ["--json", "-o", report_file]
        for item in config:
            argv += ["-c", item]
        if session:
            argv.append(session)
        argv.append("-")  # 任务书从标准输入读
        rules = CODEX_REVIEW_RULES if mode == "review" else CODEX_RULES
        code, out, err = run(request_id, argv, args["cwd"], stdin_text=args["task"] + rules)
        report = open(report_file, encoding="utf-8").read() if os.path.exists(report_file) else ""

    if code != 0 or not report.strip():
        return failure("Codex 出错或没有交回汇报", code, out, err)
    if mode == "review":
        return report, False
    if not session:
        session = re.search(r'"thread_id":"([^"]+)"', out).group(1)
    return "session_id: %s\n\n%s" % (session, report), False


def antigravity(request_id, args):
    project = os.path.abspath(args["cwd"])
    # 让它在一个空目录里运行、只把项目目录授权成只读：它的命令沙箱只允许写自己的工作目录，
    # 这样命令和文件工具都改不了项目。直接在项目里运行时，命令仍然能写文件。
    workdir = os.path.join(os.environ["CLAUDE_PLUGIN_DATA"], "agy-cwd")
    os.makedirs(workdir, exist_ok=True)
    settings = {"permissions": {"allow": ["read_file(%s)" % project], "deny": ["write_file(*)"]}}
    argv = [
        "agy",
        "--print", AGY_PROMPT.format(cwd=project, task=args["task"]),
        "--output-format", "json",
        "--settings", json.dumps(settings),
    ]
    if args.get("model"):
        argv += ["--model", args["model"]]
    if args.get("conversation_id"):
        argv += ["--conversation", args["conversation_id"]]
    # 它的命令沙箱读不到用户主目录下的 git 配置，git 会直接报错退出；让 git 不读全局配置
    code, out, err = run(request_id, argv, workdir, env=dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull))

    try:
        data = json.loads(out)
    except ValueError:
        data = {}
    if code != 0 or data.get("status") != "SUCCESS" or not data.get("response", "").strip():
        return failure("Antigravity 出错或没有给出回复", code, out, err)
    return "conversation_id: %s\n\n%s" % (data["conversation_id"], data["response"]), False


HANDLERS = {"codex": codex, "antigravity": antigravity}


def call(request):
    params = request["params"]
    try:
        text, is_error = HANDLERS[params["name"]](request["id"], params.get("arguments") or {})
    except Cancelled:
        return
    except Exception as error:  # 意外原样报给调用方，服务器继续运行
        text, is_error = "%s: %s" % (type(error).__name__, error), True
    send({"jsonrpc": "2.0", "id": request["id"], "result": {"content": [{"type": "text", "text": text}], "isError": is_error}})


def main():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    for line in sys.stdin:
        request = json.loads(line)
        method = request.get("method")
        if method == "initialize":
            result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}}, "serverInfo": {"name": "model-trio", "version": version}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "ping":
            result = {}
        elif method == "tools/call":
            threading.Thread(target=call, args=(request,), daemon=True).start()
            continue
        elif method == "notifications/cancelled":
            proc = running.pop(request["params"]["requestId"], None)
            if proc:
                stop(proc)
            continue
        elif "id" in request and method:
            send({"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32601, "message": "Method not found: %s" % method}})
            continue
        else:
            continue  # 其他通知，以及对方发来的响应
        send({"jsonrpc": "2.0", "id": request["id"], "result": result})
    # 标准输入关闭说明 Claude Code 退出了：停掉还在运行的子进程
    for proc in list(running.values()):
        stop(proc)


if __name__ == "__main__":
    main()
