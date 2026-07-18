from config import kimi_chat, make_daytona

reply = kimi_chat([{"role": "user", "content": "Reply with exactly: KIMI OK"}],
                  temperature=0)[:40]
print(f"KIMI: OK ({reply})")
d = make_daytona()
sb = d.create()
try:
    r = sb.process.code_run("print(2+2)")
    out = (getattr(r, "result", "") or "").strip()
    assert "4" in out, f"sandbox stdout was {out!r}"
    print(f"DAYTONA: OK (2+2={out} | sandbox {sb.id})")
finally:
    try:
        sb.delete()
    except Exception:
        d.delete(sb)                 # SDK versions differ on where delete lives
print("SMOKE OK")
