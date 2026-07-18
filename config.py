import os
from dotenv import load_dotenv
load_dotenv()

import certifi   # macOS Python ships no CA bundle -> Daytona SSL verify fails without this
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

KIMI_MODEL = os.getenv("KIMI_MODEL", "gpt-5.5")                # final stack: OpenAI (user decision)
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.openai.com/v1")
MAX_PARALLEL = int(os.getenv("MAX_PARALLEL", "4"))     # §0.5 verified; drop to 1-2 on quota errors
SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "20"))
TARGET_COVERAGE = 90.0
MAX_ROUNDS = 2            # baseline + 1 refine round (production: 1 round gives visible lift)
DATA_XLSX = os.getenv("DATA_XLSX", "data/skillsfuture.xlsx")

from openai import OpenAI
_kimi = OpenAI(api_key=os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY") or "EMPTY",
               base_url=KIMI_BASE_URL)

def kimi_chat(messages, temperature=0.3, json_mode=False, max_tokens=4096):
    base = dict(model=KIMI_MODEL, messages=messages)
    if json_mode:
        base["response_format"] = {"type": "json_object"}
    # gpt-5.x wants max_completion_tokens and only default temperature;
    # Moonshot/older models want max_tokens. Try richest form, degrade on param errors.
    attempts = [
        {**base, "temperature": temperature, "max_completion_tokens": max_tokens},
        {**base, "max_completion_tokens": max_tokens},           # drop unsupported temperature
        {**base, "temperature": temperature, "max_tokens": max_tokens},   # legacy (Moonshot)
        {**base, "max_tokens": max_tokens},
    ]
    last = None
    for kw in attempts:
        try:
            return _kimi.chat.completions.create(**kw).choices[0].message.content
        except Exception as e:
            last = e
            m = str(e).lower()
            if "max_tokens" in m or "max_completion_tokens" in m or "temperature" in m:
                continue      # param-shape mismatch -> try next form
            raise
    raise last

def kimi_json(messages, temperature=0.2, validate=None, retries=2, max_tokens=4096):
    """Strict JSON with client-side validate-and-retry (§0.5 bug 5)."""
    import json as _json
    last = None
    for _ in range(retries + 1):
        try:
            obj = _json.loads(kimi_chat(messages, temperature, json_mode=True,
                                        max_tokens=max_tokens))
            if validate is None or validate(obj):
                return obj
            last = "validation failed"
        except Exception as e:
            last = str(e)
    raise ValueError(f"kimi_json failed after retries: {last}")

def make_daytona():
    try:
        from daytona import Daytona, DaytonaConfig
    except ImportError:                                   # §8 fallback package name
        from daytona_sdk import Daytona, DaytonaConfig
    return Daytona(DaytonaConfig(api_key=os.environ["DAYTONA_API_KEY"]))
