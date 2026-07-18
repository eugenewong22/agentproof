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
    if q in DEMO_ROLE.lower():          # demo-role priority: 'data analyst' collides with 3
        return DEMO_SECTOR, DEMO_TRACK, DEMO_ROLE   # other sectors' roles in sheet order
    for sector, track, role, *_ in _sheet("Job Role_Description"):
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

def get_ka(code, level):
    """Official per-level Knowledge & Ability checklist — the rubric that grounds every graded task."""
    items, prof = [], ""
    for _typ, c, _sec, _cat, _title, _desc, lvl, pdesc, item, kind in _sheet("TSC_CCS_K&A"):
        if c == code and normalize_level(lvl) == level and item:
            items.append({"item": str(item).strip(),
                          "kind": str(kind or "").strip().lower()})
            prof = pdesc or prof
    return {"proficiency_description": prof or "", "items": items}

def get_sector(role):
    for sector, track, jr, *_ in _sheet("Job Role_Description"):
        if jr == role:
            return {"sector": sector, "track": track}
    return {"sector": DEMO_SECTOR, "track": DEMO_TRACK}
