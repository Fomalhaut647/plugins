#!/bin/bash
# 主会话把一块的开发交给本机的 Codex 命令行。过程不进主会话的上下文：Codex 的事件写进
# <运行目录>/events*.jsonl，它每一轮最后的汇报写进 report*.md，屏幕上只打印会话编号、结果、
# 改动清单、检查结果和汇报。
#
# 用法：
#   codex.sh --mode read|code --cd <工作目录> --out <运行目录> [选项] <任务书文件>
#   codex.sh --progress <运行目录>     查看这次任务进行到哪一步（用户询问进度时用）
#
#   --mode read|code     read 只读；code 只能写 --cd 那个目录。用户的 Codex 设置放开了也照这个关
#   --cd <目录>          Codex 的工作目录，必须在 git 工作副本里
#   --out <目录>         这次任务的运行目录，必须尚不存在：每次分派任务用一个新目录
#   --resume <会话编号>  接着之前那个 Codex 会话继续（确认验收清单后开发、修复）
#   --verify <命令>      只用于 code：Codex 完成后，在沙箱外的工作目录里运行这条检查；未通过就把
#                        失败输出在原会话里交回 Codex 修复，再检查，最多 --fix-rounds 轮
#   --fix-rounds <n>     检查未通过时自动交回 Codex 的轮数（默认 2；0 表示只检查不返工）
#   --no-net             只用于 code：不让 Codex 跑的命令联网。code 默认允许联网；read 的只读沙箱
#                        没有联网开关，始终不联网
#   --model <模型>、--effort <思考强度>
#   --fast on|off        开或关 Codex 的 Fast 模式（速度更快，用量更多）
#                        --model、--effort、--fast 不给就用用户 Codex 设置里的
#
# 退出码：0 完成（带 --verify 的也通过了检查）；3 自动返工后检查仍未通过；4 Codex 没有提交汇报或
#   没有给出会话编号；64 用法不对；69 没装 codex；77 codex 没登录；其余是 Codex 自己的退出码。
set -u

MODE="" CD="" OUT="" RESUME="" VERIFY="" FIX_ROUNDS=2 NET=1 MODEL="" EFFORT="" FAST=""

die() { echo "codex.sh：$2" >&2; exit "$1"; }
stage() { echo "$1" > "$OUT/stage"; }
finish() { date +%s > "$OUT/ended"; echo "$1" > "$OUT/exit_code"; rm -f "$OUT/stage"; exit "$1"; }

main() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --no-net) NET=0; shift ;;
      --progress|--mode|--cd|--out|--resume|--verify|--fix-rounds|--model|--effort|--fast)
        [ $# -ge 2 ] || die 64 "$1 后面要跟一个值"
        case "$1" in
          --progress) progress "$2"; exit $? ;;
          --mode) MODE="$2" ;;
          --cd) CD="$2" ;;
          --out) OUT="$2" ;;
          --resume) RESUME="$2" ;;
          --verify) VERIFY="$2" ;;
          --fix-rounds) FIX_ROUNDS="$2" ;;
          --model) MODEL="$2" ;;
          --effort) EFFORT="$2" ;;
          --fast) FAST="$2" ;;
        esac
        shift 2 ;;
      -*) die 64 "不认识的选项：$1" ;;
      *) break ;;
    esac
  done
  [ $# -eq 1 ] || die 64 "最后要给一个任务书文件（用法见脚本开头）"
  local brief="$1"
  case "$MODE" in read|code) ;; *) die 64 "--mode 要写 read 或 code" ;; esac
  [ -f "$brief" ] || die 64 "任务书文件不存在：$brief"
  [ -n "$CD" ] || die 64 "要用 --cd 给 Codex 的工作目录"
  [ -n "$OUT" ] || die 64 "要用 --out 指定这次任务的运行目录"
  [ -e "$OUT" ] && die 64 "运行目录已经存在：$OUT（每次分派任务用一个新目录）"
  if [ "$MODE" = read ] && { [ -n "$VERIFY" ] || [ "$NET" = 0 ]; }; then die 64 "--verify、--no-net 只用于 code"; fi
  case "$FIX_ROUNDS" in ''|*[!0-9]*) die 64 "--fix-rounds 要写非负整数" ;; esac
  case "$FAST" in ''|on|off) ;; *) die 64 "--fast 要写 on 或 off" ;; esac
  [ "$(git -C "$CD" rev-parse --is-inside-work-tree 2>/dev/null)" = true ] || die 64 "--cd 不在 git 工作副本里：$CD"
  command -v codex >/dev/null || die 69 "没装 codex 命令行"
  codex login status 2>&1 | grep -q '^Logged in' || die 77 "codex 没登录：请用户自己在终端跑 codex login"

  CD=$(cd "$CD" && pwd)
  mkdir -p "$OUT" || die 64 "建不了运行目录：$OUT"
  OUT=$(cd "$OUT" && pwd)
  cp "$brief" "$OUT/brief.md"
  echo $$ > "$OUT/pid"
  date +%s > "$OUT/started"
  trap 'date +%s > "$OUT/stopped"; exit 143' TERM INT HUP
  { cat "$OUT/brief.md"; printf '\n\n'; rules; } > "$OUT/prompt.md"

  stage "Codex 工作中"
  run_codex "$OUT/prompt.md" "$RESUME" events.jsonl report.md
  local rc=$? thread last=report.md vstat="" vround=0
  thread=$(cat "$OUT/thread_id" 2>/dev/null)
  if [ -n "$VERIFY" ] && [ "$rc" = 0 ] && [ -n "$thread" ]; then
    while :; do
      stage "本机检查中（第 $((vround + 1)) 次）"
      if (cd "$CD" && bash -c "$VERIFY") > "$OUT/verify-$vround.log" 2>&1; then vstat=pass; break; fi
      [ "$vround" -lt "$FIX_ROUNDS" ] || { vstat=fail; break; }
      vround=$((vround + 1))
      fix_prompt "$OUT/verify-$((vround - 1)).log" > "$OUT/fix-$vround.md"
      stage "Codex 返工中（第 $vround 轮）"
      last="report-fix$vround.md"
      run_codex "$OUT/fix-$vround.md" "$thread" "events-fix$vround.jsonl" "$last"
      rc=$?
      [ "$rc" = 0 ] || break
    done
  fi

  local code=0
  if [ "$rc" != 0 ]; then code=$rc
  elif [ -z "$thread" ] || [ ! -s "$OUT/$last" ]; then code=4
  elif [ "$vstat" = fail ]; then code=3
  fi
  summary "$code" "$thread" "$vstat" "$vround"
  finish "$code"
}

# run_codex <提示文件> <会话编号，新开就留空> <事件文件名> <汇报文件名>
run_codex() {
  local a=(-c 'approval_policy="never"')
  if [ "$MODE" = code ]; then
    a+=(-c 'sandbox_mode="workspace-write"')
    [ "$NET" = 1 ] && a+=(-c 'sandbox_workspace_write.network_access=true')
  else
    a+=(-c 'sandbox_mode="read-only"')
  fi
  [ -n "$MODEL" ] && a+=(-c "model=\"$MODEL\"")
  [ -n "$EFFORT" ] && a+=(-c "model_reasoning_effort=\"$EFFORT\"")
  # Codex 里 Fast 模式就是 priority 档；default 是普通速度
  case "$FAST" in
    on) a+=(-c 'service_tier="priority"') ;;
    off) a+=(-c 'service_tier="default"') ;;
  esac
  if [ -n "$2" ]; then
    (cd "$CD" && codex exec resume --json -o "$OUT/$4" "${a[@]}" "$2" -) < "$1" > "$OUT/$3" 2>> "$OUT/stderr.log"
  else
    (cd "$CD" && codex exec --json -o "$OUT/$4" "${a[@]}" -) < "$1" > "$OUT/$3" 2>> "$OUT/stderr.log"
  fi
  local r=$?
  if [ -n "$2" ]; then
    echo "$2" > "$OUT/thread_id"
  else
    grep -m1 -o '"thread_id":"[^"]*"' "$OUT/$3" | cut -d'"' -f4 > "$OUT/thread_id"
  fi
  return $r
}

# summary <退出码> <会话编号> <检查结果> <自动返工轮数>
summary() {
  local secs=$(( $(date +%s) - $(cat "$OUT/started") )) evs=("$OUT/events.jsonl") i=1 n usage
  while [ "$i" -le "$4" ]; do evs+=("$OUT/events-fix$i.jsonl"); i=$((i + 1)); done
  echo "运行目录：$OUT"
  [ -n "$2" ] && echo "会话编号：$2"
  case "$1" in
    0) if [ "$3" = pass ]; then echo "结果：完成，本机检查通过（自动返工 $4 轮）"; else echo "结果：完成"; fi ;;
    3) echo "结果：本机检查未通过，自动返工 $4 轮后仍失败" ;;
    4) if [ -n "$2" ]; then echo "结果：Codex 这一轮没有提交汇报"; else echo "结果：没有拿到 Codex 的会话编号，无法续接返工"; fi ;;
    *) echo "结果：Codex 出错（退出码 $1），出错信息在最后" ;;
  esac
  usage=$(cat "${evs[@]}" 2>/dev/null | grep -o '"usage":{[^}]*}' | tail -1)
  echo "用时：$((secs / 60)) 分 $((secs % 60)) 秒${usage:+；Codex 用量（这个会话累计）：${usage#\"usage\":}}"
  if [ "$MODE" = code ]; then
    echo "--- 改动清单 ---"
    git -C "$CD" status --short | head -40
    n=$(git -C "$CD" status --short | wc -l | tr -d ' ')
    [ "$n" -gt 40 ] && echo "……共 $n 项"
    git -C "$CD" diff --shortstat HEAD
  fi
  if [ -n "$3" ]; then
    echo "--- 本机检查：$VERIFY ---"
    tail -n 15 "$OUT/verify-$4.log"
    echo "（完整日志：$OUT/verify-$4.log）"
  fi
  echo "--- 汇报 ---"
  print_report "$OUT/report.md" 150
  i=1
  while [ "$i" -le "$4" ]; do
    echo "--- 自动返工第 $i 轮的汇报 ---"
    print_report "$OUT/report-fix$i.md" 40
    i=$((i + 1))
  done
  if [ "$1" != 0 ] && [ "$1" != 3 ] && [ "$1" != 4 ]; then
    echo "--- 出错信息 ---"
    grep -h -E '"type":"(error|turn\.failed)"' "${evs[@]}" 2>/dev/null | tail -3 | cut -c1-400
    tail -n 20 "$OUT/stderr.log"
  fi
  return 0
}

# print_report <文件> <最多打印的行数>
print_report() {
  if [ ! -s "$1" ]; then echo "（没有）"; return 0; fi
  local n
  n=$(wc -l < "$1" | tr -d ' ')
  head -n "$2" "$1"
  [ -n "$(tail -c1 "$1")" ] && echo
  [ "$n" -gt "$2" ] && echo "……共 $n 行，全文见 $1"
  return 0
}

rules() {
  cat <<'EOF'
---
固定规矩（主会话分派任务时追加的，优先于上文；项目规矩里和这几条冲突的，比如要求认领 Issue、完成后开 PR，这次以这几条为准）：
- 汇报用简体中文；代码、命令、报错、文件名照原样。
- 不提交、不推送、不切换分支、不开或合并 PR、不动 Issue、不发布、不对外发任何消息；这些由主会话做。
- 不读、不打印、不改任何密码、Key、令牌、Cookie。
- 只做任务书里的事，不顺手重构，不批量格式化无关的文件。
- 改动明显超出任务书预计的规模，先停下，在汇报里写打算怎么做、为什么，不要先写完。
- 拿不准、要主会话定的事：不影响其余部分的先绕开往下做，汇报里列出来；绕不开就停下，写清卡在哪、要定什么。不要猜着往下做。
- 这一轮结束后即停止，运行中无法与主会话对话。最后一条消息就是交给主会话的汇报，别处的输出主会话看不到。汇报至少写清：结论（三五句）；做了什么、查到什么（每条附依据：文件:行号，或命令和结果）；未完成的、未验证的、需要主会话决定的。篇幅控制在 1500 字以内，长材料存成文件，汇报里给路径。
EOF
  if [ "$MODE" = code ]; then
    cat <<'EOF'
- 改完后自行运行任务书要求的测试和检查，未通过就修复。沙箱里无法运行的（比如要监听端口），不排查，列出是哪些，主会话会在沙箱外运行。
EOF
  else
    echo "- 这一轮只读，不改任何文件。"
  fi
}

# fix_prompt <检查日志>
fix_prompt() {
  cat <<EOF
# 返工（任务分派脚本自动发出）：本机检查未通过

你上一轮完成后，主会话在沙箱外的工作目录里运行了检查：\`$VERIFY\`，未通过。完整日志：$1，末尾 200 行附在下面。

- 按这份输出修复。沙箱里无法运行的测试，就按这份输出修复，汇报里写明哪些需要主会话再运行确认。
- 不准改测试、放宽断言、跳过用例来迁就代码；只有测试本身错了（比如它断言的正是任务书要改掉的旧行为）才改，并在汇报里写明理由。
- 失败项和你这次的改动无关（没碰过的模块、偶发、环境问题）时，不要强行修改，汇报里写清为什么判断无关。
- 汇报只写这一轮：改了什么（文件:行号）、为什么能修好、自己运行了哪些测试。

\`\`\`
$(tail -n 200 "$1")
\`\`\`
EOF
}

# progress <运行目录>：只打印几行摘要，不把事件全文拉进对话
progress() {
  local d="${1%/}" now started secs state files=() i=1
  [ -f "$d/started" ] || die 64 "不是 codex.sh 的运行目录：$d"
  now=$(date +%s)
  started=$(cat "$d/started")
  if [ -f "$d/exit_code" ]; then
    secs=$(( $(cat "$d/ended") - started ))
    state="已结束，退出码 $(cat "$d/exit_code")，结果见后台任务的输出"
  elif kill -0 "$(cat "$d/pid")" 2>/dev/null; then
    secs=$(( now - started ))
    state="运行中：$(cat "$d/stage" 2>/dev/null)"
  else
    secs=$(( $(cat "$d/stopped" 2>/dev/null || echo "$now") - started ))
    state="中途被停止，停在「$(cat "$d/stage" 2>/dev/null)」"
  fi
  echo "$state；用时 $((secs / 60)) 分 $((secs % 60)) 秒"
  [ -f "$d/events.jsonl" ] || return 0
  files+=("$d/events.jsonl")
  while [ -f "$d/events-fix$i.jsonl" ]; do files+=("$d/events-fix$i.jsonl"); i=$((i + 1)); done
  python3 -I - "${files[@]}" <<'PY'
import json, sys

steps = []
for n, path in enumerate(sys.argv[1:]):
    if n:
        steps.append(f"—— 自动返工第 {n} 轮 ——")
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        item = ev.get("item") or {}
        if ev.get("type") != "item.completed":
            continue
        kind = item.get("type")
        if kind == "command_execution":
            ok = item.get("exit_code") == 0
            steps.append(("命令 ✓ " if ok else f"命令 ✗（退出码 {item.get('exit_code')}）") + " ".join(str(item.get("command", "")).split())[:100])
        elif kind == "file_change":
            steps.append("改文件：" + "、".join(str(c.get("path", "")).rsplit("/", 1)[-1] for c in item.get("changes", [])))
        elif kind == "agent_message":
            steps.append("Codex 说：" + " ".join(str(item.get("text", "")).split())[:100])
print(f"最近几步（共 {len(steps)} 步）：")
for s in steps[-8:]:
    print("  " + s)
PY
}

main "$@"
