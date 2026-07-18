import os, requests

def _query(payload):
    user, pwd = os.getenv("OXYLABS_USERNAME"), os.getenv("OXYLABS_PASSWORD")
    if not user or not pwd:
        return None
    r = requests.post("https://realtime.oxylabs.io/v1/queries",
                      auth=(user, pwd), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_task_material(role_title):
    """Live postings digest. NEVER raises (§8); prints the §10 forced-visible line on success."""
    try:
        data = _query({"source": "google_search", "parse": True,
                       "query": f'"{role_title}" job Singapore responsibilities'})
        if not data:
            return None
        organic = data["results"][0]["content"]["results"]["organic"][:5]
        digest = "\n".join(f"- {r.get('title', '')}: {str(r.get('desc', ''))[:200]}"
                           for r in organic)
        print(f"Oxylabs: pulled {len(organic)} current postings for {role_title}")
        return digest or None
    except Exception as e:
        print(f"Oxylabs unavailable ({type(e).__name__}) — proceeding without seasoning")
        return None

def fetch_salary_band(role_title):
    """Salary range for Screen-4 market strip. Optional; None -> UI omits the band."""
    try:
        data = _query({"source": "google_search", "parse": True,
                       "query": f'"{role_title}" salary Singapore MyCareersFuture'})
        if not data:
            return None
        snippets = " ".join(str(r.get("desc", ""))
                            for r in data["results"][0]["content"]["results"]["organic"][:5])
        import re
        amts = [int(a.replace(",", "")) for a in
                re.findall(r"\$\s?([\d,]{4,7})", snippets)][:8]
        if len(amts) < 2:
            return None
        return {"low": min(amts), "high": max(amts), "currency": "SGD",
                "source": "live search"}
    except Exception:
        return None
