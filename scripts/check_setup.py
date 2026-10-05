"""Run this before the workshop: python scripts/check_setup.py"""

import importlib
import os
import sys

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results = []


def record(status, label, detail=""):
    results.append((status, label, detail))


def check_python():
    v = sys.version_info
    if v >= (3, 10):
        record(PASS, "Python version", f"{v.major}.{v.minor}.{v.micro}")
    else:
        record(FAIL, "Python version", f"{v.major}.{v.minor} found, 3.10+ required")


def check_package(name, label):
    try:
        mod = importlib.import_module(name)
        record(PASS, label, getattr(mod, "__version__", "installed"))
    except ImportError:
        record(FAIL, label, "not installed — run: pip install -r requirements.txt")


def check_provider_key():
    if not os.environ.get("OPENAI_API_KEY"):
        if os.environ.get("USE_CANNED_RESPONSES") == "1":
            record(WARN, "OPENAI_API_KEY", "unset, but USE_CANNED_RESPONSES=1 — tracing works; model cells and Module 4 need a key")
        else:
            record(FAIL, "OPENAI_API_KEY", "unset — set it, or set USE_CANNED_RESPONSES=1 to follow along without one")
        return
    try:
        import openai
    except ImportError:
        record(FAIL, "OPENAI_API_KEY", "set, but openai is not installed — run: pip install -r requirements.txt")
        return
    # A set key can still be mistyped or revoked; listing models is free and proves it works.
    try:
        openai.OpenAI(timeout=15, max_retries=0).models.list()
        record(PASS, "OPENAI_API_KEY", "set and accepted by OpenAI")
    except openai.AuthenticationError:
        record(FAIL, "OPENAI_API_KEY", "rejected by OpenAI — check the key, or create a new one")
    except openai.PermissionDeniedError:
        record(WARN, "OPENAI_API_KEY", "set, but this key can't list models, so it couldn't be verified")
    except Exception as exc:
        record(WARN, "OPENAI_API_KEY", f"set, but OpenAI couldn't be reached ({type(exc).__name__})")


def check_opik_connection():
    try:
        import opik
        from opik.config import OpikConfig
        from opik.rest_api.core.api_error import ApiError
    except ImportError:
        record(FAIL, "Opik connection", "opik not installed")
        return
    target = OpikConfig().url_override
    where = "Opik Cloud" if "comet.com" in target else target
    try:
        opik.Opik().auth_check()
        record(PASS, "Opik connection", where)
    except ApiError as exc:
        reason = "not authenticated" if exc.status_code in (401, 403) else f"HTTP {exc.status_code}"
        record(FAIL, "Opik connection", f"{where}: {reason} — run: opik configure")
    except Exception as exc:
        fix = "check your network, then: opik configure" if where == "Opik Cloud" else "is it running? Check OPIK_URL_OVERRIDE (SETUP.md)"
        record(FAIL, "Opik connection", f"can't reach {where} ({type(exc).__name__}) — {fix}")


def check_agent():
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from workshop.corpus import load_corpus

        record(PASS, "Workshop corpus", f"{len(load_corpus())} documents loaded")
    except Exception as exc:
        record(FAIL, "Workshop corpus", f"{type(exc).__name__}: {exc}")


for check in (check_python, check_provider_key, check_agent):
    check()
check_package("opik", "opik package")
check_package("openai", "openai package")
check_opik_connection()

width = max(len(label) for _, label, _ in results)
print()
for status, label, detail in results:
    print(f"  [{status}] {label.ljust(width)}  {detail}")
print()

failures = [r for r in results if r[0] == FAIL]
if failures:
    print(f"{len(failures)} check(s) failed. See TROUBLESHOOTING.md.")
    sys.exit(1)
print("All checks passed — you're ready for the workshop.")
