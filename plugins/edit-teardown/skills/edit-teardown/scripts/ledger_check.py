"""Form check for a teardown ledger (templates/ledger.md shape).

Usage:  python3 ledger_check.py LEDGER.md [LEDGER.md ...]
Exit 0 when no errors (warnings allowed), 1 otherwise.

What it checks: frontmatter pins the target; a table under a ledger section has that section's exact
header; every table uses the fixed enums; inference is never 'observed'; every non-unknown finding points
at evidence and evidence file paths exist (with or without a folder, with or without a :line suffix);
inferred findings carry a limitation; negative findings state a numeric bound; a closed ledger names every
unresolved question id in the unknowns table, and the unknowns table names no id the checklist lacks;
a 'pass' obligation rests on a replay. Pinned cases: test_ledger_check.py.
What it does NOT check: whether any finding is true. Open the evidence for anything a decision rests on.
"""
import os
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        if _stream.isatty():
            _stream.reconfigure(errors="replace")
        else:
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

KINDS = {"product", "youtube", "paper", "business"}
LEDGER_STATUS = {"open", "closed"}
CHECK_STATUS = {"answered", "partial", "unresolved"}
STATES = {"observed", "derived", "inferred", "unknown"}
AUTHORITIES = {"artifact", "replay", "history", "external", "statement", "inference"}
OBLIGATION_STATUS = {"open", "pass", "fail"}

TABLES = {
    "checklist": ["id", "질문", "필요한 증거", "상태"],
    "findings": ["id", "주장", "상태", "권위", "증거", "범위", "한계"],
    "unknowns": ["id", "질문", "필요한 권위", "다음 탐침"],
    "obligations": ["id", "성질", "합격 조건", "검증기", "권위", "상태"],
}

# Negative claims ("none / never / 0 found") must carry a numeric bound. "없는지 확인했다" (checked whether
# there is any) is a method, not a claim, so 없는 followed by 지 is excluded. Cases: test_ledger_check.py.
NEGATIVE = re.compile(
    r"없(?:다|음|었|고|이|어|으며|던|는(?!지))|전무|전혀|하나도|아무\s?것도|"
    r"지\s?않(?:는|았|음|고|다|으며)|안\s(?:쓰|쓴|써|보|본|봤|나|난|나오|나온|한|했|된|됐)|"
    r"못\s?(?:찾|했|본|봤|잡)|찾지\s?못|"
    r"(?<![\d.,])0(?![\d.,])\s*(?:%|개|건|편|회|곳|번|명|초)|"
    r"\b(?:never|none|absent|not found|no longer|zero)\b",
    re.IGNORECASE,
)
PATH_EXT = re.compile(
    r"\.(json|jsonl|md|txt|csv|tsv|png|jpg|jpeg|webp|gif|mp4|mov|har|saz|py|mjs|cjs|js|ts|html|pdf|log|npy|"
    r"ipynb|pptx|xlsx)$", re.I)
LOC_SUFFIX = re.compile(r"(?::\d+(?:-\d+)?)+$")  # file.json:12 or preload.js:1:22764
SECTION_TABLE = {"질문 체크리스트": "checklist", "발견": "findings", "미해결": "unknowns", "재구성 의무": "obligations"}
QREF = re.compile(r"(?<![A-Za-z0-9])Q\d+(?!\d)")


def clean(cell):
    cell = cell.strip()
    return "" if cell in {"-", "\u2014", "\u2013"} else cell


def strip_code(text):
    return text.replace("`", "")


def parse_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, 0
    meta = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, i + 1
        if ":" in lines[i]:
            key, value = lines[i].split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, 0


def parse_tables(lines, start):
    """Return ({table_name: [(line_no, {col: cell})]}, header_errors).

    A table is recognised by its exact header. A table sitting under one of the four ledger sections
    (## 질문 체크리스트 / 발견 / 미해결 / 재구성 의무) whose header does not match is an error, so a typo in a
    header cannot make a whole table silently skip every check."""
    found, header_errors = {}, []
    section = None
    i = start
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            section = SECTION_TABLE.get(line[3:].strip())
        if line.lstrip().startswith("|"):
            header = [clean(c) for c in split_row(line)]
            name = next((n for n, cols in TABLES.items() if header == cols), None)
            if section and name != section:
                header_errors.append(
                    f"line {i + 1}: table under the {section} section has header {header}; "
                    f"expected | {' | '.join(TABLES[section])} |")
            j = i + 1
            if j < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[j]):
                j += 1
            rows = []
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = [clean(c) for c in split_row(lines[j])]
                if name:
                    cells += [""] * (len(header) - len(cells))
                    rows.append((j + 1, dict(zip(header, cells))))
                j += 1
            if name:
                found.setdefault(name, []).extend(rows)
            i = j
        else:
            i += 1
    return found, header_errors


def split_row(line):
    body = line.strip().replace("\\|", "\u0000")
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.replace("\u0000", "|") for c in body.split("|")]


def evidence_paths(cell):
    """Yield path-like pieces from an evidence cell (URLs and prose skipped).

    A piece is a path when it ends in a known file extension, with or without a folder and with an optional
    :line[:col] suffix, or when it contains a slash and ends with one (a folder)."""
    for piece in re.split(r"[\s,;]+", strip_code(cell)):
        piece = piece.strip("()[]<>\"'")
        piece = piece.split("#", 1)[0]
        if not piece or "://" in piece or piece.startswith("www."):
            continue
        bare = LOC_SUFFIX.sub("", piece)
        if PATH_EXT.search(bare) or (("/" in bare or "\\" in bare) and bare.endswith(("/", "\\"))):
            yield bare


def resolve(piece, base):
    expanded = os.path.expandvars(piece)
    if "$" in expanded:
        return None  # variable not set here; cannot judge
    p = Path(expanded)
    return p if p.is_absolute() else (base / p)


def check(path, text=None):
    """Check one ledger. `text` overrides the file's content (tests); paths still resolve from `path`."""
    errors, warnings = [], []
    if text is None:
        text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    base = Path(path).resolve().parent

    meta, body_start = parse_frontmatter(lines)
    if not meta:
        errors.append("frontmatter missing (--- ... ---)")
    for key in ("target", "kind", "question", "date", "snapshot", "status"):
        value = meta.get(key, "")
        if not value or value.startswith("<"):
            errors.append(f"frontmatter '{key}' empty or still a template placeholder")
    if meta.get("kind") and meta["kind"] not in KINDS:
        errors.append(f"frontmatter kind '{meta['kind']}' not in {sorted(KINDS)}")
    if meta.get("status") and meta["status"] not in LEDGER_STATUS:
        errors.append(f"frontmatter status '{meta['status']}' not in {sorted(LEDGER_STATUS)}")
    if meta.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
        errors.append(f"frontmatter date '{meta['date']}' is not YYYY-MM-DD")

    tables, header_errors = parse_tables(lines, body_start)
    errors.extend(header_errors)
    for name in ("checklist", "findings"):
        if not tables.get(name):
            errors.append(f"table '{name}' missing or empty (header must be: | {' | '.join(TABLES[name])} |)")

    for name, rows in tables.items():
        ids = [r["id"] for _, r in rows if r.get("id")]
        dup = {x for x in ids if ids.count(x) > 1}
        if dup:
            errors.append(f"{name}: duplicate ids {sorted(dup)}")
        for ln, r in rows:
            if not r.get("id"):
                errors.append(f"line {ln} ({name}): empty id")

    unresolved = []
    for ln, r in tables.get("checklist", []):
        st = strip_code(r["상태"])
        if st not in CHECK_STATUS:
            errors.append(f"line {ln} checklist {r['id']}: 상태 '{st}' not in {sorted(CHECK_STATUS)}")
        if st == "unresolved":
            unresolved.append(r["id"])
        if not r["질문"]:
            errors.append(f"line {ln} checklist {r['id']}: 질문 empty")

    for ln, r in tables.get("findings", []):
        fid, st, auth = r["id"], strip_code(r["상태"]), strip_code(r["권위"])
        if st not in STATES:
            errors.append(f"line {ln} finding {fid}: 상태 '{st}' not in {sorted(STATES)}")
        if auth not in AUTHORITIES:
            errors.append(f"line {ln} finding {fid}: 권위 '{auth}' not in {sorted(AUTHORITIES)}")
        if auth == "inference" and st not in {"inferred", "unknown"}:
            errors.append(f"line {ln} finding {fid}: authority 'inference' can only be inferred/unknown, got '{st}'")
        if not r["주장"]:
            errors.append(f"line {ln} finding {fid}: 주장 empty")
        if st != "unknown" and not r["증거"]:
            errors.append(f"line {ln} finding {fid}: 증거 empty (only 'unknown' may lack evidence)")
        if st == "inferred" and not r["한계"]:
            errors.append(f"line {ln} finding {fid}: inferred finding needs a 한계 (what would confirm it)")
        if st != "unknown" and NEGATIVE.search(r["주장"]) and not re.search(r"\d", r["범위"]):
            errors.append(f"line {ln} finding {fid}: negative claim without a numeric bound in 범위")
        for piece in evidence_paths(r["증거"]):
            target = resolve(piece, base)
            if target is None:
                warnings.append(f"line {ln} finding {fid}: cannot resolve '{piece}' (variable unset)")
            elif not target.exists():
                errors.append(f"line {ln} finding {fid}: evidence path not found: {piece}")

    for ln, r in tables.get("obligations", []):
        oid, st, auth = r["id"], strip_code(r["상태"]), strip_code(r["권위"])
        if st not in OBLIGATION_STATUS:
            errors.append(f"line {ln} obligation {oid}: 상태 '{st}' not in {sorted(OBLIGATION_STATUS)}")
        if not r["합격 조건"]:
            errors.append(f"line {ln} obligation {oid}: 합격 조건 empty")
        if not r["검증기"]:
            errors.append(f"line {ln} obligation {oid}: 검증기 empty")
        if st == "pass" and auth != "replay":
            errors.append(f"line {ln} obligation {oid}: 'pass' needs authority 'replay', got '{auth}'")

    # Each unresolved question is carried into 미해결 by naming its id there, e.g. "(Q3) ...".
    check_ids = {r["id"] for _, r in tables.get("checklist", [])}
    refs = {}
    for ln, r in tables.get("unknowns", []):
        for q in QREF.findall(" ".join(v for k, v in r.items() if k != "id")):
            refs.setdefault(q, ln)
    for q, ln in sorted(refs.items()):
        if q not in check_ids:
            errors.append(f"line {ln} unknowns: refers to {q}, which is not in the checklist")
    if meta.get("status") == "closed":
        for q in unresolved:
            if q not in refs:
                errors.append(f"closed ledger: unresolved {q} is not carried into 미해결 (name it there, e.g. '({q})')")
    for ln, r in tables.get("unknowns", []):
        if not r["필요한 권위"] or not r["다음 탐침"]:
            warnings.append(f"line {ln} unknown {r['id']}: 필요한 권위 / 다음 탐침 empty")

    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    failed = False
    for path in argv[1:]:
        errors, warnings = check(path)
        status = "FAIL" if errors else "PASS"
        print(f"{status}  {path}  ({len(errors)} error(s), {len(warnings)} warning(s))")
        for e in errors:
            print(f"  error    {e}")
        for w in warnings:
            print(f"  warning  {w}")
        failed |= bool(errors)
    print("form check only: it does not test whether any finding is true.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
