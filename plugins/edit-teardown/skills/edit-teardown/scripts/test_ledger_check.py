"""Pinned cases for ledger_check.py. Run after any change to the checker:  python3 test_ledger_check.py

A checker that is never shown a bad ledger can pass everything. So this file runs both directions:
a small valid ledger written to a temporary folder must PASS, each planted defect must be caught, and
negative_control_ledger.md must FAIL with exactly 11 errors.
"""
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        if _stream.isatty():
            _stream.reconfigure(errors="replace")
        else:
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ledger_check as lc  # noqa: E402

failures = []


def expect(name, cond):
    print(("ok    " if cond else "FAIL  ") + name)
    if not cond:
        failures.append(name)


# 1. negative-claim pattern
for s in ["쓰지 않았다", "보이지 않는다", "하나도 없다", "전무하다",
          "박스는 0개다", "자막이 없다", "never uses boxes", "박스를 안 쓴다", "도구를 찾지 못했다"]:
    expect(f"negative fires: {s}", bool(lc.NEGATIVE.search(s)))
for s in ["없는지 확인했다", "0.5% 늘었다", "10개를 찾았다", "100%다",
          "창 안에 있다", "적지 않은 시간이 든다"]:
    expect(f"negative silent: {s}", not lc.NEGATIVE.search(s))

# 2. evidence path forms
expect("path: bare file name", list(lc.evidence_paths("missing.json")) == ["missing.json"])
expect("path: :line suffix stripped",
       list(lc.evidence_paths("evidence/missing.json:12")) == ["evidence/missing.json"])
expect("path: file:line:col", list(lc.evidence_paths("`preload.js:1:22764`")) == ["preload.js"])
expect("path: URL skipped", list(lc.evidence_paths("https://example.com/a.js (2026-10-14)")) == [])
expect("path: prose skipped", list(lc.evidence_paths("본인 진술, 고정 댓글")) == [])

# 3. positive control: a minimal valid ledger with a real evidence file
VALID = """---
target: 예시 채널 최근 3편 (2026-08~2026-10)
kind: youtube
question: 자막 강조를 분당 몇 번 하는가
date: 2026-10-15
snapshot: evidence/video_ids.txt
status: closed
---

## 질문 체크리스트

| id | 질문 | 필요한 증거 | 상태 |
|---|---|---|---|
| Q1 | 자막 강조 빈도 | 프레임 측정 | answered |
| Q3 | 강조 색 | 프레임 | unresolved |

## 발견

| id | 주장 | 상태 | 권위 | 증거 | 범위 | 한계 |
|---|---|---|---|---|---|---|
| F1 | 강조는 분당 1.1회다 | derived | replay | evidence/emphasis.json | 3편 전편 | 내 영상으로 검정한 자 |
| F2 | 박스는 0개다 | observed | replay | evidence/emphasis.json | 3편, 2026-08~10 | |

## 미해결

| id | 질문 | 필요한 권위 | 다음 탐침 |
|---|---|---|---|
| U1 | (Q3) 강조 색 | artifact | 프레임 색 추출 |
"""

with tempfile.TemporaryDirectory() as tmp:
    led = Path(tmp) / "ledger.md"
    (Path(tmp) / "evidence").mkdir()
    (Path(tmp) / "evidence" / "emphasis.json").write_text("{}", encoding="utf-8")
    (Path(tmp) / "evidence" / "video_ids.txt").write_text("x\n", encoding="utf-8")
    led.write_text(VALID, encoding="utf-8")
    errs, _ = lc.check(led)
    expect(f"positive control passes (errors: {errs})", errs == [])

    for bad in ["missing.json", "evidence/missing.json:12"]:
        errs, _ = lc.check(led, VALID.replace("evidence/emphasis.json", bad, 1))
        expect(f"missing evidence caught: {bad}", any("evidence path not found" in e for e in errs))
    errs, _ = lc.check(led, VALID.replace("evidence/emphasis.json", "evidence/emphasis.json:12", 1))
    expect("existing evidence with :line passes", errs == [])

    errs, _ = lc.check(led, VALID.replace("| 3편, 2026-08~10 |", "| 전체 채널 |"))
    expect("negative claim without a numeric bound caught", any("numeric bound" in e for e in errs))

    errs, _ = lc.check(led, VALID + ("\n## 재구성 의무\n\n| id | 성질 | 합격 조건 | 검증기 | 권위 | status |\n"
                                     "|---|---|---|---|---|---|\n| O1 | x | y | z | replay | pass |\n"))
    expect("header typo caught", any("expected | id | 성질" in e for e in errs))

    errs, _ = lc.check(led, VALID.replace("| U1 | (Q3)", "| U1 | (Q999)", 1))
    expect("unknown names a missing id", any("Q999" in e for e in errs))
    expect("unresolved Q3 not carried", any("unresolved Q3" in e for e in errs))

    errs, _ = lc.check(led, VALID.replace("| derived | replay |", "| observed | inference |", 1))
    expect("observed from inference caught", any("authority 'inference'" in e for e in errs))

# 4. negative control
errs, _ = lc.check(HERE / "negative_control_ledger.md")
expect(f"negative control fails with 11 errors (got {len(errs)})", len(errs) == 11)

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
