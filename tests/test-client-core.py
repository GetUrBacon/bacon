#!/usr/bin/env python3
"""
Dependency-free test suite for bacon_core.py — no pytest required.
Uses plain assert/print with exit 0 (all pass) or 1 (fail).

Isolates all file operations to a temp directory so tests don't touch ~/.bacon.
"""

import sys
import os
import json
import tempfile
import pathlib
import shutil
import time

# Add bin/ to path and import bacon_core
BIN = pathlib.Path(__file__).resolve().parent.parent / "bin"
sys.path.insert(0, str(BIN))
import bacon_core as b

# Create temp directory and redirect module constants
TMP = pathlib.Path(tempfile.mkdtemp())
b.CONFIG_DIR = TMP
b.TOKENS_FILE = TMP / "tokens.json"
b.CAMPAIGNS_FILE = TMP / "campaigns.json"
b.REPORTS_FILE = TMP / "reports.jsonl"
b.AUTH_CONFIG_CACHE_FILE = TMP / "auth_config_cache.json"
b.REFILL_STATE_FILE = TMP / "refill_state.json"

# Test results tracking
tests_passed = 0
tests_failed = 0
test_names = []


def reset_files():
    """Clean up test files between tests."""
    for f in [b.TOKENS_FILE, b.CAMPAIGNS_FILE, b.REPORTS_FILE,
              b.AUTH_CONFIG_CACHE_FILE, b.REFILL_STATE_FILE]:
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass


def test_select_targeted():
    """Test select_winner with intent-targeted campaigns."""
    global tests_passed, tests_failed
    test_names.append("test_select_targeted")
    try:
        campaigns = [
            {"id": "a", "target_signals": ["intent_auth"], "priority": 3},
            {"id": "b", "target_signals": [], "priority": 1},
            {"id": "c", "target_signals": ["intent_auth"], "priority": 2},
        ]
        winner = b.select_winner(campaigns, {"intent_auth"})
        assert winner is not None, "winner should not be None"
        assert winner["id"] == "c", f"Expected id='c', got id='{winner['id']}'"
        print("✓ test_select_targeted PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_select_targeted FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_select_targeted ERROR: {e}")
        tests_failed += 1


def test_select_untargeted_fallback():
    """Test select_winner falls back to untargeted pool when no intent match."""
    global tests_passed, tests_failed
    test_names.append("test_select_untargeted_fallback")
    try:
        campaigns = [
            {"id": "a", "target_signals": ["intent_auth"], "priority": 3},
            {"id": "b", "target_signals": [], "priority": 1},
            {"id": "c", "target_signals": ["intent_auth"], "priority": 2},
        ]
        winner = b.select_winner(campaigns, set())
        assert winner is not None, "winner should not be None"
        assert winner["id"] == "b", f"Expected id='b', got id='{winner['id']}'"
        print("✓ test_select_untargeted_fallback PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_select_untargeted_fallback FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_select_untargeted_fallback ERROR: {e}")
        tests_failed += 1


def test_select_empty():
    """Test select_winner handles empty/None campaigns gracefully."""
    global tests_passed, tests_failed
    test_names.append("test_select_empty")
    try:
        result1 = b.select_winner([], {"x"})
        assert result1 is None, f"select_winner([], ...) should return None, got {result1}"
        result2 = b.select_winner(None, {"x"})
        assert result2 is None, f"select_winner(None, ...) should return None, got {result2}"
        print("✓ test_select_empty PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_select_empty FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_select_empty ERROR: {e}")
        tests_failed += 1


def test_base_url_default():
    """Test base_url with default config."""
    global tests_passed, tests_failed
    test_names.append("test_base_url_default")
    try:
        default_base = "https://api.geturbacon.dev"
        base = b.base_url({})
        assert base == default_base, f"Expected '{default_base}', got '{base}'"

        tokens_url_result = b.tokens_url({})
        assert tokens_url_result == default_base + "/v1/tokens", f"tokens_url mismatch: {tokens_url_result}"

        campaigns_sync_url_result = b.campaigns_sync_url({})
        assert campaigns_sync_url_result.endswith("/v1/campaigns/sync"), f"campaigns_sync_url doesn't end with /v1/campaigns/sync: {campaigns_sync_url_result}"

        batch_url_result = b.batch_url({})
        assert batch_url_result.endswith("/v1/impression/batch"), f"batch_url doesn't end with /v1/impression/batch: {batch_url_result}"

        print("✓ test_base_url_default PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_base_url_default FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_base_url_default ERROR: {e}")
        tests_failed += 1


def test_append_utm_params():
    """append_utm_params: adds Bacon UTMs to the target, preserves existing query,
    never clobbers advertiser keys, preserves path/fragment, no-op on empty."""
    global tests_passed, tests_failed
    test_names.append("test_append_utm_params")
    try:
        # no-op on empty
        assert b.append_utm_params("", "card", "c1") == "", "empty url must be a no-op"
        # all four utm_* present
        out = b.append_utm_params("https://acme.com", "inline_mention", "camp_x")
        for frag in ("utm_source=bacon", "utm_medium=cli", "utm_campaign=camp_x", "utm_content=inline_mention"):
            assert frag in out, f"missing {frag} in {out}"
        # preserves the advertiser's existing query param
        out2 = b.append_utm_params("https://acme.com/p?ref=abc", "card", "c1")
        assert "ref=abc" in out2 and "utm_source=bacon" in out2, out2
        # does NOT clobber an advertiser-set utm_source
        out3 = b.append_utm_params("https://acme.com?utm_source=their_own", "card", "c1")
        assert "utm_source=their_own" in out3, out3
        assert out3.count("utm_source=") == 1, f"duplicate utm_source in {out3}"
        # preserves path + fragment
        out4 = b.append_utm_params("https://acme.com/a/b#sec", "card", "c1")
        assert "/a/b" in out4 and out4.endswith("#sec"), out4
        # fail-open: garbage in → string out, no raise
        assert isinstance(b.append_utm_params("not a url", "card", "c1"), str)
        print("✓ test_append_utm_params PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_append_utm_params FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_append_utm_params ERROR: {e}")
        tests_failed += 1


def test_osc8():
    """osc8: empty url passes text through; non-empty wraps with the OSC 8 escape."""
    global tests_passed, tests_failed
    test_names.append("test_osc8")
    try:
        assert b.osc8("", "TEXT") == "TEXT", "empty url must pass text through"
        wrapped = b.osc8("https://acme.com", "TEXT")
        assert "\033]8;;" in wrapped and "https://acme.com" in wrapped and "TEXT" in wrapped, wrapped
        print("✓ test_osc8 PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_osc8 FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_osc8 ERROR: {e}")
        tests_failed += 1


def test_base_url_custom():
    """Test base_url with custom auction_url."""
    global tests_passed, tests_failed
    test_names.append("test_base_url_custom")
    try:
        config = {"auction_url": "http://localhost:8799/v1/auction"}
        result = b.base_url(config)
        expected = "http://localhost:8799"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✓ test_base_url_custom PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_base_url_custom FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_base_url_custom ERROR: {e}")
        tests_failed += 1


def test_token_bucket_roundtrip():
    """Test token bucket FIFO: append → count → pop → pop → None."""
    global tests_passed, tests_failed
    test_names.append("test_token_bucket_roundtrip")
    reset_files()
    try:
        # Append 2 tokens
        b.append_tokens([
            {"impression_id": "i1", "token": "t1"},
            {"impression_id": "i2", "token": "t2"},
        ])

        # Count should be 2
        count1 = b.tokens_count()
        assert count1 == 2, f"Expected count=2, got {count1}"

        # Pop first token
        token1 = b.pop_token()
        assert token1 is not None, "First pop_token should not be None"
        assert token1["impression_id"] == "i1", f"Expected i1, got {token1['impression_id']}"
        assert token1["token"] == "t1", f"Expected t1, got {token1['token']}"

        # Pop second token
        token2 = b.pop_token()
        assert token2 is not None, "Second pop_token should not be None"
        assert token2["impression_id"] == "i2", f"Expected i2, got {token2['impression_id']}"
        assert token2["token"] == "t2", f"Expected t2, got {token2['token']}"

        # Pop from empty bucket
        token3 = b.pop_token()
        assert token3 is None, f"pop_token on empty bucket should return None, got {token3}"

        # Count should be 0
        count2 = b.tokens_count()
        assert count2 == 0, f"Expected count=0, got {count2}"

        print("✓ test_token_bucket_roundtrip PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_token_bucket_roundtrip FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_token_bucket_roundtrip ERROR: {e}")
        tests_failed += 1


def test_append_accumulates():
    """Test that append_tokens accumulates, doesn't clobber."""
    global tests_passed, tests_failed
    test_names.append("test_append_accumulates")
    reset_files()
    try:
        b.append_tokens([{"impression_id": "a", "token": "1"}])
        b.append_tokens([{"impression_id": "b", "token": "2"}])

        count = b.tokens_count()
        assert count == 2, f"Expected count=2 after two appends, got {count}"
        print("✓ test_append_accumulates PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_append_accumulates FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_append_accumulates ERROR: {e}")
        tests_failed += 1


def test_tokens_low():
    """Test tokens_low with default watermark of 10."""
    global tests_passed, tests_failed
    test_names.append("test_tokens_low")
    reset_files()
    try:
        # Empty bucket → tokens_low should be True
        low1 = b.tokens_low({})
        assert low1 is True, f"Empty bucket should be low, got {low1}"

        # Append 12 tokens → tokens_low should be False
        b.append_tokens([{"impression_id": f"i{i}", "token": f"t{i}"} for i in range(12)])
        low2 = b.tokens_low({})
        assert low2 is False, f"12 tokens should not be low, got {low2}"
        print("✓ test_tokens_low PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_tokens_low FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_tokens_low ERROR: {e}")
        tests_failed += 1


def test_buffer_report():
    """Test buffer_report appends JSON lines to REPORTS_FILE."""
    global tests_passed, tests_failed
    test_names.append("test_buffer_report")
    reset_files()
    try:
        b.buffer_report({"impression_id": "x", "surface": "context"})
        b.buffer_report({"impression_id": "y", "surface": "spinner"})

        # Read the file and verify 2 lines
        assert b.REPORTS_FILE.exists(), "REPORTS_FILE should exist after buffer_report"

        lines = b.REPORTS_FILE.read_text().strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"

        # Parse first line
        first = json.loads(lines[0])
        assert first["impression_id"] == "x", f"Expected impression_id='x', got {first['impression_id']}"

        # Parse second line
        second = json.loads(lines[1])
        assert second["impression_id"] == "y", f"Expected impression_id='y', got {second['impression_id']}"

        print("✓ test_buffer_report PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_buffer_report FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_buffer_report ERROR: {e}")
        tests_failed += 1


def test_campaigns_cache():
    """Test campaigns_cache: load, stale detection, TTL."""
    global tests_passed, tests_failed
    test_names.append("test_campaigns_cache")
    reset_files()
    try:
        # Write a fresh cache
        now = time.time()
        cache_data = {"ts": now, "campaigns": [{"id": "z"}]}
        b.CAMPAIGNS_FILE.write_text(json.dumps(cache_data))

        # Load and verify
        campaigns = b.load_campaigns()
        assert campaigns == [{"id": "z"}], f"Expected [{'id': 'z'}], got {campaigns}"

        # Check not stale (TTL 600s, diff is ~0)
        stale1 = b.campaigns_stale({"campaigns_ttl_sec": 600})
        assert stale1 is False, f"Fresh cache should not be stale, got {stale1}"

        # Rewrite with old timestamp
        old_ts = now - 10000
        cache_data["ts"] = old_ts
        b.CAMPAIGNS_FILE.write_text(json.dumps(cache_data))

        # Check stale now
        stale2 = b.campaigns_stale({"campaigns_ttl_sec": 600})
        assert stale2 is True, f"Old cache should be stale, got {stale2}"

        # Delete file and check stale + empty load
        b.CAMPAIGNS_FILE.unlink()
        stale3 = b.campaigns_stale({"campaigns_ttl_sec": 600})
        assert stale3 is True, f"Missing cache should be stale, got {stale3}"

        campaigns2 = b.load_campaigns()
        assert campaigns2 == [], f"Missing cache should return [], got {campaigns2}"

        print("✓ test_campaigns_cache PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_campaigns_cache FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_campaigns_cache ERROR: {e}")
        tests_failed += 1


def test_load_config():
    """Test load_config returns {} for missing file."""
    global tests_passed, tests_failed
    test_names.append("test_load_config")
    reset_files()
    try:
        # No config file exists
        config = b.load_config()
        assert config == {}, f"load_config should return {{}}, got {config}"

        # Write a config and load it
        b.CONFIG_DIR.mkdir(exist_ok=True)
        config_file = b.CONFIG_DIR / "config.json"
        test_config = {"auction_url": "http://test:8000/v1/auction", "refill_low_watermark": 20}
        config_file.write_text(json.dumps(test_config))

        config2 = b.load_config()
        assert config2 == test_config, f"Expected {test_config}, got {config2}"

        print("✓ test_load_config PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_load_config FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_load_config ERROR: {e}")
        tests_failed += 1


def test_auth_config_cache_hit_skips_network():
    """_get_oauth_config() must return the on-disk cache without hitting the
    network when the cache is fresh (< AUTH_CONFIG_TTL_SEC old)."""
    global tests_passed, tests_failed
    test_names.append("test_auth_config_cache_hit_skips_network")
    reset_files()
    try:
        b._write_auth_config_cache({"token_url": "https://cached/token", "client_id": "c1"})

        def _boom(*a, **k):
            raise AssertionError("network should not be called on a cache hit")

        import urllib.request
        orig_urlopen = urllib.request.urlopen
        urllib.request.urlopen = _boom
        try:
            oauth = b._get_oauth_config()
        finally:
            urllib.request.urlopen = orig_urlopen

        assert oauth == {"token_url": "https://cached/token", "client_id": "c1"}, oauth
        print("✓ test_auth_config_cache_hit_skips_network PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_auth_config_cache_hit_skips_network FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_auth_config_cache_hit_skips_network ERROR: {e}")
        tests_failed += 1


def test_auth_config_cache_expired_refetches():
    """An expired on-disk cache must be ignored and refreshed from the network,
    then rewritten to disk."""
    global tests_passed, tests_failed
    test_names.append("test_auth_config_cache_expired_refetches")
    reset_files()
    try:
        stale = {"ts": time.time() - (b.AUTH_CONFIG_TTL_SEC + 10),
                  "oauth": {"token_url": "https://stale/token"}}
        b.AUTH_CONFIG_CACHE_FILE.write_text(json.dumps(stale))

        class _FakeResp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps({"token_url": "https://fresh/token", "client_id": "c2"}).encode()

        import urllib.request
        orig_urlopen = urllib.request.urlopen
        urllib.request.urlopen = lambda *a, **k: _FakeResp()
        try:
            oauth = b._get_oauth_config()
        finally:
            urllib.request.urlopen = orig_urlopen

        assert oauth.get("token_url") == "https://fresh/token", oauth
        on_disk = json.loads(b.AUTH_CONFIG_CACHE_FILE.read_text())
        assert on_disk["oauth"]["token_url"] == "https://fresh/token", on_disk
        print("✓ test_auth_config_cache_expired_refetches PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_auth_config_cache_expired_refetches FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_auth_config_cache_expired_refetches ERROR: {e}")
        tests_failed += 1


def test_refill_cooldown_blocks_rapid_reattempts():
    """_refill_recently_attempted() must claim the slot on first call and
    report 'recently attempted' on an immediate second call."""
    global tests_passed, tests_failed
    test_names.append("test_refill_cooldown_blocks_rapid_reattempts")
    reset_files()
    try:
        first = b._refill_recently_attempted()
        second = b._refill_recently_attempted()
        assert first is False, f"first call should claim the slot, got {first}"
        assert second is True, f"second call within cooldown should be blocked, got {second}"
        print("✓ test_refill_cooldown_blocks_rapid_reattempts PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_refill_cooldown_blocks_rapid_reattempts FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_refill_cooldown_blocks_rapid_reattempts ERROR: {e}")
        tests_failed += 1


def test_refill_cooldown_expires():
    """Once REFILL_COOLDOWN_SEC has elapsed, a new attempt must be allowed."""
    global tests_passed, tests_failed
    test_names.append("test_refill_cooldown_expires")
    reset_files()
    try:
        b.REFILL_STATE_FILE.write_text(json.dumps({
            "last_attempt": time.time() - (b.REFILL_COOLDOWN_SEC + 5)
        }))
        blocked = b._refill_recently_attempted()
        assert blocked is False, f"expired cooldown should allow a new attempt, got {blocked}"
        print("✓ test_refill_cooldown_expires PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_refill_cooldown_expires FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_refill_cooldown_expires ERROR: {e}")
        tests_failed += 1


def test_spawn_refill_respects_cooldown():
    """spawn_refill() must not Popen a second time within the cooldown window."""
    global tests_passed, tests_failed
    test_names.append("test_spawn_refill_respects_cooldown")
    reset_files()
    try:
        calls = []
        orig_popen = b.subprocess.Popen
        b.subprocess.Popen = lambda *a, **k: calls.append((a, k))
        try:
            b.spawn_refill()
            b.spawn_refill()
        finally:
            b.subprocess.Popen = orig_popen

        assert len(calls) == 1, f"expected exactly 1 Popen call, got {len(calls)}"
        print("✓ test_spawn_refill_respects_cooldown PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_spawn_refill_respects_cooldown FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_spawn_refill_respects_cooldown ERROR: {e}")
        tests_failed += 1


def test_record_refill_auth_status():
    """record_refill_auth_status() persists auth_ok for bacon-earnings to read."""
    global tests_passed, tests_failed
    test_names.append("test_record_refill_auth_status")
    reset_files()
    try:
        b.record_refill_auth_status(False)
        state = json.loads(b.REFILL_STATE_FILE.read_text())
        assert state.get("auth_ok") is False, state
        b.record_refill_auth_status(True)
        state2 = json.loads(b.REFILL_STATE_FILE.read_text())
        assert state2.get("auth_ok") is True, state2
        print("✓ test_record_refill_auth_status PASSED")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ test_record_refill_auth_status FAILED: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ test_record_refill_auth_status ERROR: {e}")
        tests_failed += 1


def main():
    """Run all tests and report results."""
    global tests_passed, tests_failed

    print("=" * 70)
    print("bacon_core.py Test Suite")
    print("=" * 70)
    print()

    # Run all tests
    test_select_targeted()
    test_select_untargeted_fallback()
    test_select_empty()
    test_base_url_default()
    test_base_url_custom()
    test_append_utm_params()
    test_osc8()
    test_token_bucket_roundtrip()
    test_append_accumulates()
    test_tokens_low()
    test_buffer_report()
    test_campaigns_cache()
    test_load_config()
    test_auth_config_cache_hit_skips_network()
    test_auth_config_cache_expired_refetches()
    test_refill_cooldown_blocks_rapid_reattempts()
    test_refill_cooldown_expires()
    test_spawn_refill_respects_cooldown()
    test_record_refill_auth_status()

    print()
    print("=" * 70)
    print(f"Result: {tests_passed}/{tests_passed + tests_failed} passed")
    print("=" * 70)

    # Clean up temp directory
    try:
        shutil.rmtree(TMP)
    except Exception:
        pass

    # Exit with appropriate code
    sys.exit(0 if tests_failed == 0 else 1)


if __name__ == "__main__":
    main()
