#!/usr/bin/env python3
"""
Test suite for bacon-statusline pure helpers.

Dependency-free, plain assert-based test script.
No pytest required.
"""

import sys
import time
import importlib.machinery
import importlib.util
from pathlib import Path

# Setup path to bin directory
BIN = Path(__file__).resolve().parent.parent / "bin"


def load(name):
    """Load a bin script as a module using importlib."""
    file_path = BIN / name
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(file_path))
    spec = importlib.util.spec_from_loader(name.replace("-", "_"), loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


print("=" * 70)
print("Testing bacon-statusline pure helpers")
print("=" * 70)

# Load the modules
try:
    sl = load("bacon-statusline")
    print("\n✓ bacon-statusline imported successfully")
except Exception as e:
    print(f"\n✗ Failed to import bacon-statusline: {e}")
    sys.exit(1)

try:
    refresh = load("bacon-refresh")
    print("✓ bacon-refresh imported successfully (smoke test)")
except Exception as e:
    print(f"✗ Failed to import bacon-refresh: {e}")
    sys.exit(1)

# Test results tracking
passed = 0
failed = 0
test_results = []


def test(name, condition, expected=True):
    """Helper to run a test and track results."""
    global passed, failed, test_results
    if condition == expected:
        print(f"✓ {name}")
        passed += 1
        test_results.append((name, True))
    else:
        print(f"✗ {name}")
        print(f"  Expected: {expected}, Got: {condition}")
        failed += 1
        test_results.append((name, False))


print("\n" + "=" * 70)
print("Running tests")
print("=" * 70 + "\n")

# --- Test 1: impression_url_from with default auction URL ---
result = sl.impression_url_from("https://api.geturbacon.dev/v1/auction")
expected = "https://api.geturbacon.dev/v1/impression"
test("test_impression_url_from_default", result == expected)

# --- Test 2: impression_url_from with localhost ---
result = sl.impression_url_from("http://127.0.0.1:8799/v1/auction")
expected = "http://127.0.0.1:8799/v1/impression"
test("test_impression_url_from_localhost", result == expected)

# --- Test 3: impression_url_from with fallback (weird URL) ---
result = sl.impression_url_from("https://x.example/weird")
# Should fallback to default base + /v1/impression
expected_suffix = "/v1/impression"
test("test_impression_url_from_fallback", result.endswith(expected_suffix))

# --- Test 4: osc8 with URL ---
result = sl.osc8("https://zaplogin.dev", "ZapLogin")
has_text = "ZapLogin" in result
has_url = "https://zaplogin.dev" in result
has_esc = "\033]8;;" in result  # ESC + ]8;;
test("test_osc8_with_url (text)", has_text)
test("test_osc8_with_url (url)", has_url)
test("test_osc8_with_url (esc frame)", has_esc)

# --- Test 5: osc8 with empty URL ---
result = sl.osc8("", "ZapLogin")
expected = "ZapLogin"
test("test_osc8_no_url", result == expected)

# --- Test 6: is_fresh with recent timestamp (True) ---
now = time.time()
ad = {"ts": now}
ttl = 600
result = sl.is_fresh(ad, ttl)
test("test_is_fresh_true", result is True)

# --- Test 7: is_fresh with stale timestamp (False) ---
old_time = time.time() - 10000  # 10000 seconds ago
ad = {"ts": old_time}
ttl = 600
result = sl.is_fresh(ad, ttl)
test("test_is_fresh_stale", result is False)

# --- Test 8: is_fresh with missing ts (False, fail-closed) ---
ad = {}  # missing "ts" key
ttl = 600
result = sl.is_fresh(ad, ttl)
test("test_is_fresh_bad", result is False)

# --- Test 9: bacon-refresh imports cleanly ---
test("test_refresh_imports", refresh is not None)

print("\n" + "=" * 70)
print(f"Result: {passed}/{passed + failed} passed")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
