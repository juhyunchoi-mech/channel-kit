"""Does Claude Code follow a rule you wrote down? Count it from your own transcripts.

Claude Code keeps every conversation as JSONL under ~/.claude/projects/. This script reads
them and, week by week, counts how many of Claude's final answers still contain a marker
you banned (default: the em dash). Multi-turn sessions (you talking to Claude) are reported
apart from one-turn sessions (usually scripts calling `claude -p`).

Usage:
  python cc_rule_meter.py                       # em dash, all projects
  python cc_rule_meter.py --marker "TODO"       # any string your rule bans
  python cc_rule_meter.py --project my-repo     # only projects whose folder name contains this
"""
import argparse
import collections
import datetime
import json
import pathlib
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        if _stream.isatty():
            _stream.reconfigure(errors="replace")
        else:
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ap = argparse.ArgumentParser()
ap.add_argument("--marker", default="—")
ap.add_argument("--project", default="")
ap.add_argument("--root", default=str(pathlib.Path.home() / ".claude" / "projects"))
args = ap.parse_args()

weeks = collections.defaultdict(lambda: [0, 0, 0, 0])   # multi finals, multi hits, one finals, one hits
n_sessions = n_tools = 0

for path in pathlib.Path(args.root).glob("*/*.jsonl"):   # top level only: subagent files live deeper
    if args.project not in path.parent.name:
        continue
    turns = []            # one entry per human turn: [timestamp, last assistant text]
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message") or {}
        content = msg.get("content")
        if rec.get("type") == "user" and not rec.get("isMeta"):
            if isinstance(content, list) and any(b.get("type") == "tool_result" for b in content if isinstance(b, dict)):
                continue  # a tool result, not a person typing
            text = content if isinstance(content, str) else " ".join(
                b.get("text", "") for b in content or [] if isinstance(b, dict))
            if text.strip() and not text.lstrip().startswith("<"):   # skip command and system wrappers
                turns.append([rec.get("timestamp"), None])
        elif rec.get("type") == "assistant" and isinstance(content, list) and turns:
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    n_tools += 1
                elif b.get("type") == "text" and b.get("text", "").strip():
                    turns[-1][1] = (rec.get("timestamp"), b["text"])
    if not turns:
        continue
    n_sessions += 1
    off = 0 if len(turns) > 1 else 2
    for _, final in turns:
        if not final or not final[0]:
            continue
        day = datetime.datetime.fromisoformat(final[0].replace("Z", "+00:00"))
        iso = day.isocalendar()
        w = f"{iso[0]}-W{iso[1]:02d}"
        weeks[w][off] += 1
        weeks[w][off + 1] += args.marker in final[1]

print(f"sessions {n_sessions}, tool calls {n_tools}, marker {args.marker!r}")
print("| week | your sessions: answers | with marker | rate | one-turn runs: answers | with marker | rate |")
print("|---|---|---|---|---|---|---|")
for w, v in sorted(weeks.items()):
    r = lambda n, h: f"{100 * h / n:.1f}%" if n else "-"
    print(f"| {w} | {v[0]} | {v[1]} | {r(v[0], v[1])} | {v[2]} | {v[3]} | {r(v[2], v[3])} |")
