#!/usr/bin/env python3
"""
Dependency-free test suite for bacon-fetch in-reply renderers (clickable links).
Run: python3 tests/test-render.py
Exit: 0 on all pass, 1 on any fail.
"""

import sys
import pathlib

BIN = pathlib.Path(__file__).resolve().parent.parent / "bin"
BACON_FETCH = BIN / "bacon-fetch"

# Load bacon-fetch by executing it (main() is guarded by __name__ == "__main__",
# so it won't run). bin/ on sys.path so its `import bacon_core` resolves.
sys.path.insert(0, str(BIN))
ns = {"__file__": str(BACON_FETCH), "__name__": "bacon_fetch_under_test"}
exec(BACON_FETCH.read_text(), ns)

render_strip = ns["render_strip"]
render_card = ns["render_card"]
render_banner = ns["render_banner"]
render_inline = ns["render_inline"]

AD = {
    "id": "camp_x",
    "advertiser": "ZapLogin",
    "ad_text": "auth in one line",
    "tagline": "auth, fast",
    "logo": "🔐",
    "url": "https://zap.dev",
}


def test_inline_clickable():
    """inline_mention: markdown link with clean host text + UTM'd target."""
    line = render_inline(AD)
    assert "[zap.dev](" in line, f"expected clean host link text: {line!r}"
    assert "utm_source=bacon" in line and "utm_content=inline_mention" in line, line
    # the visible host (inside the brackets) must be clean — no utm leak
    assert "[zap.dev]" in line, f"host text must be bare: {line!r}"
    print("  ✓ test_inline_clickable: PASS")


def test_inline_no_url():
    """No url → no link, no utm."""
    line = render_inline({**AD, "url": ""})
    assert "[" not in line and "utm_" not in line, f"expected no link: {line!r}"
    print("  ✓ test_inline_no_url: PASS")


def test_card_and_banner_clickable():
    """card/marquee ship markdown links (best-effort; revert to plain if the
    model fences these blocks — see render_card note)."""
    card = render_card(AD)
    banner = render_banner(AD)
    assert "[zap.dev](" in card and "utm_content=card" in card, card
    assert "[zap.dev](" in banner and "utm_content=marquee" in banner, banner
    print("  ✓ test_card_and_banner_clickable: PASS")


def test_strip_unchanged():
    """strip has no url line — stays a plain labeled line."""
    s = render_strip(AD)
    assert s == "🥓 Sponsored: auth in one line", f"strip changed: {s!r}"
    assert "[" not in s and "utm_" not in s, s
    print("  ✓ test_strip_unchanged: PASS")


def main():
    print("=" * 70)
    print("Testing bacon-fetch in-reply renderers (clickable links)")
    print("=" * 70)
    tests = [
        test_inline_clickable,
        test_inline_no_url,
        test_card_and_banner_clickable,
        test_strip_unchanged,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: FAIL\n    {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {t.__name__}: ERROR\n    {type(e).__name__}: {e}")
            failed += 1
    print("=" * 70)
    print(f"Result: {passed}/{len(tests)} passed")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
