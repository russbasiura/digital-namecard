#!/usr/bin/env python3
"""Parse BRD workbook(s) in requirements/*.xlsx into requirements/requirements.json.

Column layouts vary, so this is heuristic: it finds the header row on each sheet, maps
columns to canonical fields by keyword, keeps every original column under "raw", and
extracts embedded images. Sheets are classified: requirement sheets
(by name, e.g. 'Requirements', 'Nonfunctional'), acceptance-criteria sheets (linked to requirements by
requirement ID), and context sheets (roles, data dictionary, rules...) saved to requirements/context/. Claude reviews and corrects the output afterwards (Phase 1).

Usage: python3 -I scripts/parse-brd.py [path/to/file.xlsx ...]
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl missing: pip install openpyxl")

ROOT = Path(__file__).resolve().parent.parent
REQ_DIR = ROOT / "requirements"
OUT = REQ_DIR / "requirements.json"
IMG_DIR = REQ_DIR / "design" / "_from-brd"

# canonical field -> keywords (lowercase, matched as substrings of header text)
FIELD_KEYWORDS = {
    "id": ["req id", "requirement id", "req #", "req no", "id", "ref", "#", "number", "no."],
    "title": ["title", "name", "summary", "feature", "requirement name", "short description"],
    "description": ["description", "requirement", "details", "detail", "user story", "story", "statement", "need"],
    "acceptance_criteria": ["acceptance", "criteria", "definition of done", "test", "validation", "expected"],
    "priority": ["priority", "moscow", "importance", "must/should", "rank", "criticality"],
    "category": ["category", "module", "area", "section", "epic", "group", "component", "functional area", "screen", "page"],
    "type": ["type", "functional/non", "nfr", "classification"],
    "actor": ["actor", "role", "persona", "user type", "as a"],
    "status": ["status", "state", "phase", "release", "in scope", "scope"],
    "notes": ["notes", "comment", "remarks", "assumption", "dependency", "question"],
}
PRIORITY_MAP = {
    "must": "Must", "must have": "Must", "m": "Must", "high": "Must", "critical": "Must", "1": "Must", "p1": "Must", "mandatory": "Must",
    "should": "Should", "should have": "Should", "s": "Should", "medium": "Should", "2": "Should", "p2": "Should",
    "could": "Could", "could have": "Could", "c": "Could", "low": "Could", "3": "Could", "p3": "Could", "nice to have": "Could",
    "won't": "Won't", "wont": "Won't", "won't have": "Won't", "w": "Won't", "future": "Won't", "out of scope": "Won't",
}


def norm(v):
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.date().isoformat()
    return re.sub(r"\s+", " ", str(v)).strip()


def score_header(row):
    texts = [norm(c).lower() for c in row if norm(c)]
    if len(texts) < 2:
        return 0
    hits = sum(1 for t in texts for kws in FIELD_KEYWORDS.values() if any(k == t or (len(k) > 2 and k in t) for k in kws))
    return hits


def map_columns(headers):
    mapping, used = {}, set()
    # exact matches first, then substring matches; longest keyword wins
    for exact in (True, False):
        for field, kws in FIELD_KEYWORDS.items():
            if field in mapping:
                continue
            best = None
            for idx, h in enumerate(headers):
                if idx in used or not h:
                    continue
                hl = h.lower()
                for k in kws:
                    ok = hl == k if exact else (len(k) > 2 and k in hl)
                    if ok and (best is None or len(k) > best[1]):
                        best = (idx, len(k))
            if best:
                mapping[field] = best[0]
                used.add(best[0])
    return mapping


def parse_sheet(ws, source):
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], None
    header_idx = max(range(min(25, len(rows))), key=lambda i: score_header(rows[i]))
    if score_header(rows[header_idx]) < 2:
        return [], f"{source}: no recognizable header row (skipped — review manually)"
    headers = [norm(h) for h in rows[header_idx]]
    mapping = map_columns(headers)
    warn = None
    if "description" not in mapping and "title" not in mapping:
        return [], f"{source}: header found but no requirement text column (skipped — review manually)"
    reqs = []
    for r_i, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        cells = [norm(c) for c in row]
        if not any(cells):
            continue
        raw = {headers[i] or f"col{i+1}": cells[i] for i in range(min(len(headers), len(cells))) if cells[i]}
        get = lambda f: cells[mapping[f]] if f in mapping and mapping[f] < len(cells) else ""
        text = get("description") or get("title")
        if not text:
            continue
        pr_raw = get("priority")
        ac_idx = mapping.get("acceptance_criteria")
        ac_raw = str(row[ac_idx]) if ac_idx is not None and ac_idx < len(row) and row[ac_idx] is not None else ""
        reqs.append({
            "id": get("id"),
            "title": get("title") or text[:80],
            "description": get("description") or get("title"),
            "acceptance_criteria": [s.strip(" -•*\t") for s in re.split(r"\r?\n|;\s|•", ac_raw) if s.strip(" -•*\t")],
            "priority": PRIORITY_MAP.get(pr_raw.lower(), pr_raw or "Unspecified"),
            "category": get("category"),
            "type": get("type"),
            "actor": get("actor"),
            "status": get("status"),
            "notes": get("notes"),
            "source": {"file": source.split("!")[0], "sheet": ws.title, "row": r_i},
            "raw": raw,
        })
    missing = [f for f in ("id", "priority", "acceptance_criteria") if f not in mapping]
    if missing:
        warn = f"{source}: no column detected for {', '.join(missing)} — infer from text/other sheets"
    return reqs, warn


REQ_SHEET_RE = re.compile(r"requirement|user stor|functional|nfr|backlog|epic|feature", re.I)
AC_SHEET_RE = re.compile(r"acceptance|test case|uat|scenario", re.I)
CTX_DIR = REQ_DIR / "context"


def header_info(ws):
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return rows, None, []
    idx = max(range(min(25, len(rows))), key=lambda i: score_header(rows[i]))
    if score_header(rows[idx]) < 2:
        return rows, None, []
    return rows, idx, [norm(h) for h in rows[idx]]


def dump_context(ws, source):
    """Non-requirement sheets (roles, data dictionary, workflow, rules...) -> requirements/context/<sheet>.json."""
    rows, idx, headers = header_info(ws)
    records = []
    if idx is not None:
        for row in rows[idx + 1:]:
            cells = [norm(c) for c in row]
            if any(cells):
                records.append({headers[i] or f"col{i+1}": cells[i] for i in range(min(len(headers), len(cells))) if cells[i]})
    else:
        records = [[norm(c) for c in row if norm(c)] for row in rows if any(norm(c) for c in row)]
    CTX_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", ws.title).strip("_")
    path = CTX_DIR / f"{safe}.json"
    path.write_text(json.dumps({"source": source, "records": records}, indent=2, ensure_ascii=False) + "\n")
    return {"sheet": ws.title, "file": str(path.relative_to(ROOT)), "records": len(records)}


def parse_acceptance(ws):
    """Acceptance-criteria sheet -> {requirement_id: [criteria...]}."""
    rows, idx, headers = header_info(ws)
    if idx is None:
        return {}, 0
    low = [h.lower() for h in headers]
    find = lambda pred: next((i for i, h in enumerate(low) if h and pred(h)), None)
    req_col = find(lambda h: "requirement id" in h or "req id" in h or h in ("requirement", "req", "requirement ids"))
    ac_col = find(lambda h: ("ac id" in h or "acceptance id" in h or "test id" in h or h == "id") and h != (low[req_col] if req_col is not None else None))
    parts = [i for i, h in enumerate(low) if h in ("given", "when", "then")]
    if not parts:
        parts = [i for i, h in enumerate(low) if any(k in h for k in ("criteria", "scenario", "description", "expected"))][:2]
    if req_col is None or not parts:
        return {}, 0
    out, n = {}, 0
    for row in rows[idx + 1:]:
        cells = [norm(c) for c in row]
        if not any(cells) or req_col >= len(cells) or not cells[req_col]:
            continue
        text = " ".join(f"{headers[i]}: {cells[i]}" if low[i] in ("given", "when", "then") else cells[i]
                        for i in parts if i < len(cells) and cells[i])
        if ac_col is not None and ac_col < len(cells) and cells[ac_col]:
            text = f"{cells[ac_col]} — {text}"
        for rid in re.split(r"[,;\s]+", cells[req_col]):
            if rid:
                out.setdefault(rid, []).append(text)
        n += 1
    return out, n


def extract_images(wb, xlsx_name):
    count = 0
    for ws in wb.worksheets:
        for i, img in enumerate(getattr(ws, "_images", []), start=1):
            try:
                data = img._data()
                ext = (getattr(img, "format", None) or "png").lower()
                IMG_DIR.mkdir(parents=True, exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{Path(xlsx_name).stem}_{ws.title}_{i}")
                (IMG_DIR / f"{safe}.{ext}").write_bytes(data)
                count += 1
            except Exception as e:  # noqa: BLE001
                print(f"  warn: could not extract image {i} on {ws.title}: {e}")
    return count


def main():
    files = [Path(p) for p in sys.argv[1:]] or sorted(REQ_DIR.glob("*.xlsx"))
    files = [f for f in files if not f.name.startswith("~$")]
    if not files:
        sys.exit("No .xlsx found in requirements/ — Hard Stop 3 (BRD missing)")
    all_reqs, warnings, sheets, context, ac_map = [], [], [], [], {}
    for f in files:
        wb = openpyxl.load_workbook(f, data_only=True)
        n_img = extract_images(wb, f.name)
        if n_img:
            print(f"  extracted {n_img} embedded image(s) from {f.name} -> {IMG_DIR.relative_to(ROOT)}")
        named_req = [ws for ws in wb.worksheets if REQ_SHEET_RE.search(ws.title) and not AC_SHEET_RE.search(ws.title)]
        for ws in wb.worksheets:
            src = f"{f.name}!{ws.title}"
            if AC_SHEET_RE.search(ws.title):
                acs, n_ac = parse_acceptance(ws)
                if n_ac:
                    for rid, items in acs.items():
                        ac_map.setdefault(rid, []).extend(items)
                    sheets.append({"file": f.name, "sheet": ws.title, "kind": "acceptance", "records": n_ac})
                    continue
            is_req = ws in named_req if named_req else True
            if is_req:
                reqs, warn = parse_sheet(ws, src)
                if reqs:
                    sheets.append({"file": f.name, "sheet": ws.title, "kind": "requirements", "records": len(reqs)})
                    all_reqs.extend(reqs)
                    if warn:
                        warnings.append(warn)
                    continue
            info = dump_context(ws, src)
            context.append(info)
            sheets.append({"file": f.name, "sheet": ws.title, "kind": "context", "records": info["records"]})
    # assign IDs where missing and de-duplicate
    seen = set()
    n = 0
    for r in all_reqs:
        if not r["id"] or r["id"] in seen:
            n += 1
            while f"REQ-{n:03d}" in seen:
                n += 1
            r["original_id"] = r["id"] or None
            r["id"] = f"REQ-{n:03d}"
        seen.add(r["id"])
    linked = 0
    for r in all_reqs:
        for key in {r["id"], r.get("original_id") or ""} - {""}:
            if key in ac_map:
                r["acceptance_criteria"].extend(ac_map[key])
                linked += 1
    unmatched = sorted(set(ac_map) - {r["id"] for r in all_reqs} - {r.get("original_id") for r in all_reqs})
    if unmatched:
        warnings.append(f"acceptance criteria reference unknown requirement IDs: {', '.join(unmatched[:20])}")
    out = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [f.name for f in files],
        "sheets": sheets,
        "warnings": warnings,
        "reviewed_by_claude": False,
        "context_sheets": context,
        "requirements": all_reqs,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(all_reqs)} requirements, "
          f"{sum(len(v) for v in ac_map.values())} acceptance criteria linked to {linked} requirement(s), "
          f"{len(context)} context sheet(s) -> {CTX_DIR.relative_to(ROOT)}/")
    for w in warnings:
        print(f"  warn: {w}")
    by_p = {}
    for r in all_reqs:
        by_p[r["priority"]] = by_p.get(r["priority"], 0) + 1
    print("  by priority:", ", ".join(f"{k}={v}" for k, v in sorted(by_p.items())))


if __name__ == "__main__":
    main()
