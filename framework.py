import openpyxl
from functools import lru_cache
from config import DATA_XLSX

DEMO_SECTOR = "Infocomm Technology"
DEMO_TRACK = "Data and Artificial Intelligence"
DEMO_ROLE = "Data Analyst / Associate Data Engineer"    # exact string, verified in xlsx

EXEC_KEYWORDS = ("data engineering", "database administration",
                 "data analytics", "data visualisation")

_LEGACY = {"basic": 2, "intermediate": 4, "advanced": 6}   # only affects rubric-only skills

def normalize_level(v):
    """Collapse dual scale ('1'-'6' strings + Basic/Intermediate/Advanced) to int. Never hardcode a max."""
    if v is None:
        return 0
    s = str(v).strip().lower()
    if s in _LEGACY:
        return _LEGACY[s]
    try:
        return int(float(s))
    except ValueError:
        return 0

@lru_cache(maxsize=None)
def _sheet(name):
    """One full read per sheet, cached. K&A sheet (~150K rows) takes ~15-30s on first touch."""
    wb = openpyxl.load_workbook(DATA_XLSX, read_only=True)
    ws = wb[name]
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True)
            if any(c is not None for c in r)]
    wb.close()
    return rows

def resolve_role(query):
    q = query.strip().lower()
    rows = _sheet("Job Role_Description")
    demo_aliases = {part.strip().lower() for part in DEMO_ROLE.split("/")}
    if q in demo_aliases:                # 'data analyst' otherwise collides with 3 roles
        return DEMO_SECTOR, DEMO_TRACK, DEMO_ROLE
    # Exact names must win over general substring matches: "Data Engineer" is
    # also a substring of the demo role "Data Analyst / Associate Data Engineer".
    for sector, track, role, *_ in rows:
        if role and q == role.strip().lower():
            return sector, track, role
    if q:
        for sector, track, role, *_ in rows:
            if role and q in role.lower():
                return sector, track, role
    print(f"WARN: role '{query}' not found; falling back to demo role")   # §8: never crash
    return DEMO_SECTOR, DEMO_TRACK, DEMO_ROLE

def retired_codes():
    return {r[0] for r in _sheet("TSC_CCS_Key_Retired") if r[0]}

def get_skills(role):
    dead = retired_codes()
    out = []
    for _sec, _trk, jr, title, typ, level, code in _sheet("Job Role_TSC_CCS"):
        if jr == role and code not in dead:
            out.append({"skill": title, "type": typ,
                        "required_level": normalize_level(level), "code": code})
    return out

def get_context(role):
    desc, perf = "", ""
    for _sec, _trk, jr, d, p in _sheet("Job Role_Description"):
        if jr == role:
            desc, perf = d or "", p or ""
            break
    cwfs = {}
    for _sec, _trk, jr, cwf, kt in _sheet("Job Role_CWF_KT"):
        if jr == role and cwf:
            cwfs.setdefault(cwf, []).append(kt or "")
    return {"description": desc, "performance_expectation": perf,
            "critical_work_functions": [{"cwf": k, "key_tasks": v} for k, v in cwfs.items()]}

def select_executable(skills, k=5):
    """Skills a coding grader can honestly test. Demo role yields 5: DE L2, DBA L2, DA L2, DA L3, DV L3."""
    return [s for s in skills
            if any(kw in s["skill"].lower() for kw in EXEC_KEYWORDS)][:k]

@lru_cache(maxsize=1)
def _ka_index():
    """One pass over the ~150K-row K&A sheet -> {(code, level): {prof, items}}. The sheet
    is huge; scanning it once per skill (12 agents * ~28 skills) would be 300+ full scans."""
    idx = {}
    for _typ, c, _sec, _cat, _title, _desc, lvl, pdesc, item, kind in _sheet("TSC_CCS_K&A"):
        if not c:
            continue
        e = idx.setdefault((c, normalize_level(lvl)),
                           {"proficiency_description": "", "items": []})
        if item:
            e["items"].append({"item": str(item).strip(),
                               "kind": str(kind or "").strip().lower()})
        if pdesc and not e["proficiency_description"]:
            e["proficiency_description"] = pdesc
    return idx

def get_ka(code, level):
    """Official per-level Knowledge & Ability checklist — the rubric that grounds every graded task."""
    e = _ka_index().get((code, normalize_level(level)))
    if not e:
        return {"proficiency_description": "", "items": []}
    return {"proficiency_description": e["proficiency_description"],
            "items": [dict(i) for i in e["items"]]}

def get_sector(role):
    for sector, track, jr, *_ in _sheet("Job Role_Description"):
        if jr == role:
            return {"sector": sector, "track": track}
    return {"sector": DEMO_SECTOR, "track": DEMO_TRACK}
