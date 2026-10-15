---
name: rule-meter
description: Measure whether Claude Code actually follows a rule written in CLAUDE.md, by counting week by week how many of Claude's final answers in the user's own local transcripts still contain a banned string (default the em dash). Use for "규칙 지키는지 재 줘", "CLAUDE.md 규칙 잘 지켜?", "rule meter", "내 대화 기록에서 세 줘", "em dash 얼마나 써", or after adding a "never write X" rule. Reads only local files and prints counts; nothing leaves the machine.
---

# rule-meter

Claude Code saves every conversation as JSONL under `~/.claude/projects/<project-folder>/<session>.jsonl`.
`scripts/cc_rule_meter.py` reads those files and, per ISO week, counts how many of Claude's final answers
(the last text Claude wrote before the user typed again) contain a marker string. It reports the user's
own multi-turn sessions apart from one-turn sessions, which are usually scripts calling `claude -p`.

## 1. Pick the marker with the user

The meter answers one question: "after I wrote a rule banning X, how often does X still appear?"

- If the user named a rule, use the banned string from it.
- If not, read the user's CLAUDE.md files (`~/.claude/CLAUDE.md`, and `./CLAUDE.md` in the current project)
  and list the rules that ban a literal string ("never use the em dash", "do not write TODO"). Ask which
  one to measure. Rules about behaviour ("always run tests") cannot be measured by a string count; say so.
- With no rule chosen, the default marker is the em dash `—`.

Also find out **when the rule was added**: `git log -S "<rule text>" -- CLAUDE.md` if the file is in git,
otherwise ask the user. The before/after comparison around that week is the result that matters.

## 2. Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/cc_rule_meter.py" --marker "—"
python3 "${CLAUDE_SKILL_DIR}/scripts/cc_rule_meter.py" --marker "TODO" --project my-repo
python3 "${CLAUDE_SKILL_DIR}/scripts/cc_rule_meter.py" --root /path/to/projects
```

- On Windows use `python` if `python3` is missing.
- `--project` keeps only project folders whose name contains the string (folder names are the project
  path with separators replaced by `-`; list `~/.claude/projects/` to see them).
- If the user runs Claude Code with `CLAUDE_CONFIG_DIR`, pass `--root "$CLAUDE_CONFIG_DIR/projects"`.
- It only reads files and prints a table. Do not open or quote the transcripts themselves to the user
  unless they ask: they can hold private conversations.

## 3. Explain the result

Lead with the before/after rate around the week the rule was added, in the user's language. Then:

- **"your sessions" vs "one-turn runs".** Rules in CLAUDE.md load in both, but one-turn runs are often
  scripts with their own prompt; a difference between the two columns is worth pointing out.
- **Small weeks are noise.** A week with fewer than about 20 answers can swing by tens of percent on a
  few replies. Say the answer count next to any rate you quote.
- **The window is short.** Claude Code deletes transcripts older than `cleanupPeriodDays` (30 days by
  default), so the table normally covers about the last month. An empty early week means "no files",
  not "the rule worked".
- **What the count does not know.** A hit is any answer containing the string: a quoted example, a code
  block or a file path counts too. Before claiming the rule is broken, open two or three hit answers'
  context with the user's permission, or re-run with a more specific marker.
- **A rule that is still broken.** Suggest what the user can try and then re-measure next week: move the
  rule higher or into a shorter file, state it once as a positive instruction, or enforce it with a hook
  that checks the output instead of trusting prose. Do not promise any of these will work; the meter is
  how the user finds out.

Report the table the script printed as it is, plus three to five sentences of interpretation.
