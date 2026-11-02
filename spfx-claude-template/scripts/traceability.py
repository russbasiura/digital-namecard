#!/usr/bin/env python3
"""Requirements traceability matrix + coverage gate.

Scans spfx/src and tests/e2e for requirement IDs:
  - code:  comments like `// REQ-014`
  - tests: test names starting with `[REQ-014]` (Jest *.test.ts(x) and Playwright *.spec.ts)
Writes docs/TRACEABILITY.md. Exits 1 if any in-scope `Must` requirement has no test.

Usage: python3 -I scripts/traceability.py [--report-only]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQS = ROOT / "requirements" / "requirements.json"
STATUS = ROOT / "requirements" / "status.json"
OUT = ROOT / "docs" / "TRACEABILITY.md"
SKIP_DIRS = {"node_modules", "lib", "lib-commonjs", "dist", "temp", "release", "artifacts", ".auth"}


def files(base, exts):
    if not base.exists():
        return
    for p in base.rglob("*"):
        if p.is_file() and p.suffix in exts and not (set(p.parts) & SKIP_DIRS):
            yield p


def main():
    report_only = "--report-only" in sys.argv
    if not REQS.exists():
        sys.exit("requirements/requirements.json missing — run /ingest")
    reqs = json.loads(REQS.read_text())["requirements"]
    status = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    ids = [r["id"] for r in reqs]
    id_re = re.compile("|".join(re.escape(i) for i in sorted(ids, key=len, reverse=True))) if ids else None

    code_refs = {i: set() for i in ids}
    test_refs = {i: set() for i in ids}
    test_name = re.compile(r"""\b(?:it|test|describe)(?:\.\w+)?\(\s*[`'"]\s*\[([^\]]+)\]""")
    for p in list(files(ROOT / "spfx" / "src", {".ts", ".tsx"})) + list(files(ROOT / "tests", {".ts", ".tsx"})):
        rel = str(p.relative_to(ROOT))
        text = p.read_text(errors="ignore")
        is_test = bool(re.search(r"\.(test|spec)\.tsx?$", p.name))
        if is_test:
            for m in test_name.finditer(text):
                for tid in re.split(r"[,\s]+", m.group(1)):
                    if tid in test_refs:
                        test_refs[tid].add(rel)
        elif id_re:
            for m in id_re.finditer(text):
                code_refs[m.group(0)].add(rel)

    # Playwright pages.json entries declare the requirements their visual/a11y/smoke tests verify.
    pages = ROOT / "tests" / "e2e" / "pages.json"
    if pages.exists():
        for pg in json.loads(pages.read_text()).get("pages", []):
            for rid in pg.get("requirements", []):
                if rid in test_refs:
                    test_refs[rid].add(f"tests/e2e/pages.json#{pg.get('name')}")

    rows, gaps = [], []
    totals = {}
    for r in reqs:
        st = status.get(r["id"], {}).get("status", "in-scope") if isinstance(status.get(r["id"]), dict) else status.get(r["id"], "in-scope")
        delivered = bool(code_refs[r["id"]]) and bool(test_refs[r["id"]])
        pr = r.get("priority", "Unspecified")
        t = totals.setdefault(pr, [0, 0])
        if st == "in-scope":
            t[1] += 1
            t[0] += delivered
        if st == "in-scope" and pr == "Must" and not test_refs[r["id"]]:
            gaps.append(r["id"])
        mark = "✅" if delivered else ("⏸️ " + st if st != "in-scope" else "❌")
        rows.append(f"| {r['id']} | {pr} | {r.get('title','')[:70].replace('|','/')} | {mark} | "
                    f"{'<br>'.join(sorted(code_refs[r['id']])) or '—'} | {'<br>'.join(sorted(test_refs[r['id']])) or '—'} |")

    summary = ", ".join(f"{k}: {v[0]}/{v[1]}" for k, v in sorted(totals.items()))
    md = ["# Requirements Traceability", "", f"Coverage (delivered = code + test, in-scope only): **{summary}**", "",
          "| ID | Priority | Requirement | Status | Code | Tests |", "|---|---|---|---|---|---|", *rows, ""]
    if gaps:
        md += ["## Gate failures", "", "In-scope `Must` requirements with no test:", "", *[f"- {g}" for g in gaps], ""]
    if not report_only:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text("\n".join(md))
        print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Coverage: {summary}")
    if gaps:
        print(f"FAIL: {len(gaps)} Must requirement(s) without tests: {', '.join(gaps)}")
        sys.exit(0 if report_only else 1)
    print("PASS")


if __name__ == "__main__":
    main()
