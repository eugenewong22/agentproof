import json, time

PATH = "events.jsonl"

def emit(event, **kw):
    """Log a real lifecycle transition. Never raises, never blocks (BUILD_GUIDE §3)."""
    try:
        print(f"  [{event}] " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)
        with open(PATH, "a") as f:
            f.write(json.dumps({"ts": round(time.time(), 3),
                                "event": event, **kw}) + "\n")
    except Exception:
        pass
