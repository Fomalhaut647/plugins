"""kill-guard：挡住「按名字或命令行文字找进程再停」的 Bash 命令（PreToolUse 钩子）。

pkill -f 拿整条命令行做子串匹配。Mac 上几乎所有程序都在 /Applications 或 Application Support 下，
一条 pkill -f "cat" 曾把 Claude 桌面端、所有并行会话、Chrome、微信一起杀掉（2026-10-18）。
挡住时退出码 2：命令不执行，stderr 交给 Claude，让它改成按进程号停。只看本机命令的写法，
ssh 到别的机器上执行的（引号里的远程命令）不管。
"""
import json, re, sys

# 命令所在的位置：行首，或 ; & | ( ` $( 之后；前面可以带 sudo、exec 这类前缀，命令可以写成完整路径
HEAD = r"(?:^|[;&|(`\n]|\$\()\s*(?:(?:sudo|exec|command|nohup|time)(?:\s+-\S+)*\s+)*(?:\S*/)?"
RULES = [
    (re.compile(HEAD + r"(?:pkill|killall)\b"), "pkill / killall 按名字匹配进程"),
    (re.compile(r"\|\s*xargs(?:\s+(?:-\S+|\d+|\{\}))*\s+(?:sudo\s+)?(?:\S*/)?kill\b"), "把找出来的进程号交给 xargs kill"),
    (re.compile(r"\bkill\b[^;&|\n]*(?:\$\(|`)\s*(?:\S*/)?(?:pgrep|pidof|ps)\b"), "kill $(pgrep …) 按名字找进程号"),
]

ADVICE = """按名字或命令行文字找进程，会误杀名字、路径里碰巧带这几个字的程序（pkill -f 曾把 Claude 桌面端、并行会话、Chrome、微信一起杀掉）。改用：
- 自己起的进程：kill 启动时记下的进程号（$!），或用启动它的工具自带的停法（后台任务的停止、预览的停止、launchctl、systemctl）；
- 要找进程：pgrep -fl 或 ps 只列出来，逐个确认是自己起的，再 kill <进程号>；
- 按端口找：kill $(lsof -ti tcp:<端口> -sTCP:LISTEN)，只停监听这个端口的那一个（不加 -sTCP:LISTEN 会连连着这个端口的浏览器一起列出来）。"""


def main():
    command = json.load(sys.stdin)["tool_input"]["command"]
    for pattern, reason in RULES:
        if pattern.search(command):
            print("kill-guard 挡住了这条命令：%s。\n%s" % (reason, ADVICE), file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
