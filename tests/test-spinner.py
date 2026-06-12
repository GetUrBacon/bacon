#!/usr/bin/env python3
"""
Dependency-free test suite for bacon-plugin spinnerVerbs functions.
Run: python3 tests/test-spinner.py
Exit: 0 on all pass, 1 on any fail.
"""

import sys
import pathlib

# =========================================================================
# Load bacon-session by executing and extracting functions
# =========================================================================

BIN = pathlib.Path(__file__).resolve().parent.parent / "bin"
BACON_SESSION = BIN / "bacon-session"

# Read the bacon-session file and execute it to get the functions
bacon_session_code = BACON_SESSION.read_text()

# Create a namespace to hold the functions. Provide __file__ + bin on sys.path
# so the module's `import bacon_core` shim (which uses __file__) resolves.
sys.path.insert(0, str(BIN))
bs_namespace = {"__file__": str(BACON_SESSION), "__name__": "bacon_session_under_test"}

# Execute the bacon-session code (skips main() since we're not __main__)
exec(bacon_session_code, bs_namespace)

# Extract the functions we need
is_our_verb = bs_namespace['is_our_verb']
build_verb = bs_namespace['build_verb']
# URL derivation moved to bacon_core (see tests/test-client-core.py)

# =========================================================================
# Test Cases
# =========================================================================

def test_is_our_verb_emoji_roundtrip():
    """
    REGRESSION TEST: is_our_verb({"mode":"replace","verbs":["🥓 ZapLogin — x ↗"]})
    must return True. This test guards that ensure_ascii=False is used to preserve
    the literal emoji in JSON serialization (without it, the emoji would be escaped
    as \\ud83e\\udd53 and detection would fail).
    """
    verb = "🥓 ZapLogin — x ↗"
    value = {"mode": "replace", "verbs": [verb]}
    result = is_our_verb(value)
    assert result is True, f"Expected True, got {result} for emoji verb"
    print("  ✓ test_is_our_verb_emoji_roundtrip: PASS")


def test_is_our_verb_user_value():
    """
    is_our_verb({"mode":"replace","verbs":["Cogitating..."]}) should return False.
    A normal user verb without the bacon emoji is not ours.
    """
    value = {"mode": "replace", "verbs": ["Cogitating..."]}
    result = is_our_verb(value)
    assert result is False, f"Expected False, got {result} for user verb"
    print("  ✓ test_is_our_verb_user_value: PASS")


def test_is_our_verb_none():
    """
    is_our_verb(None) and is_our_verb({}) should both return False without exception.
    """
    result_none = is_our_verb(None)
    assert result_none is False, f"Expected False for None, got {result_none}"

    result_empty = is_our_verb({})
    assert result_empty is False, f"Expected False for {{}}, got {result_empty}"

    print("  ✓ test_is_our_verb_none: PASS")


def test_build_verb_has_marker():
    """
    build_verb({"advertiser":"ZapLogin","tagline":"auth fast","ad_text":"x"})
    should return a string containing the bacon emoji "🥓", "ZapLogin", and "auth fast".
    """
    ad = {
        "advertiser": "ZapLogin",
        "tagline": "auth fast",
        "ad_text": "x"
    }
    result = build_verb(ad)

    assert "🥓" in result, f"Expected emoji in result: {result}"
    assert "ZapLogin" in result, f"Expected 'ZapLogin' in result: {result}"
    assert "auth fast" in result, f"Expected 'auth fast' in result: {result}"

    print("  ✓ test_build_verb_has_marker: PASS")


def test_build_verb_fallback_adtext():
    """
    build_verb({"advertiser":"BlobDB","ad_text":"the db"}) with no tagline
    should fall back to ad_text and include "the db" in the result.
    """
    ad = {
        "advertiser": "BlobDB",
        "ad_text": "the db"
    }
    result = build_verb(ad)

    assert "the db" in result, f"Expected 'the db' in result: {result}"
    assert "BlobDB" in result, f"Expected 'BlobDB' in result: {result}"

    print("  ✓ test_build_verb_fallback_adtext: PASS")


# =========================================================================
# Main
# =========================================================================

def main():
    print("=" * 70)
    print("Testing bacon-plugin spinnerVerbs functions")
    print("=" * 70)

    tests = [
        test_is_our_verb_emoji_roundtrip,
        test_is_our_verb_user_value,
        test_is_our_verb_none,
        test_build_verb_has_marker,
        test_build_verb_fallback_adtext,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {test.__name__}: FAIL")
            print(f"    {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: ERROR")
            print(f"    {type(e).__name__}: {e}")
            failed += 1

    print("=" * 70)
    print(f"Result: {passed}/{len(tests)} passed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
