"""
bacon_core.py — shared importable module for the client-side auction pipeline.

Other bin scripts load this with:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import bacon_core

All functions are fail-open: they return None / [] / False on any error and
never raise. Uses only stdlib.
"""

import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

CONFIG_DIR   = Path.home() / ".bacon"
CAMPAIGNS_FILE = CONFIG_DIR / "campaigns.json"   # {"ts": float, "campaigns": [...]}
TOKENS_FILE  = CONFIG_DIR / "tokens.json"        # list of {"impression_id","token"}
REPORTS_FILE = CONFIG_DIR / "reports.jsonl"      # one JSON object per line

AUCTION_URL_DEFAULT = "https://bacon-backend-production.up.railway.app/v1/auction"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Read ~/.bacon/config.json; return {} on any error."""
    try:
        cfg_file = CONFIG_DIR / "config.json"
        if not cfg_file.exists():
            return {}
        return json.loads(cfg_file.read_text())
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def base_url(config: dict) -> str:
    """
    Derive the base URL (no trailing slash, no /v1/auction) from config.
    Falls back to AUCTION_URL_DEFAULT base on any malformed value.
    """
    try:
        url = config.get("auction_url", AUCTION_URL_DEFAULT).rstrip("/")
        if url.endswith("/v1/auction"):
            return url[: -len("/v1/auction")]
        # Not a recognised auction path — use the default base
    except Exception:
        pass
    return AUCTION_URL_DEFAULT.rstrip("/")[: -len("/v1/auction")]


def campaigns_sync_url(config: dict) -> str:
    return base_url(config) + "/v1/campaigns/sync"


def tokens_url(config: dict) -> str:
    return base_url(config) + "/v1/tokens"


def batch_url(config: dict) -> str:
    return base_url(config) + "/v1/impression/batch"


# ---------------------------------------------------------------------------
# Campaigns cache
# ---------------------------------------------------------------------------

def load_campaigns() -> list:
    """Return the cached campaigns list, or [] if missing/unreadable."""
    try:
        if not CAMPAIGNS_FILE.exists():
            return []
        data = json.loads(CAMPAIGNS_FILE.read_text())
        return data.get("campaigns", [])
    except Exception:
        return []


def campaigns_stale(config: dict) -> bool:
    """
    True if CAMPAIGNS_FILE is missing or older than campaigns_ttl_sec
    (default 600 s).
    """
    try:
        if not CAMPAIGNS_FILE.exists():
            return True
        data = json.loads(CAMPAIGNS_FILE.read_text())
        ttl = config.get("campaigns_ttl_sec", 600)
        return (time.time() - data.get("ts", 0)) > ttl
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Client-side auction
# ---------------------------------------------------------------------------

def select_winner(campaigns: list, intent_labels) -> dict | None:
    """
    Port of the server-side auction, run entirely client-side.

    intent_labels — set or list of label strings e.g. {"intent_auth"}.

    Priority 1 = highest bidder (smallest number wins).
    """
    try:
        if not campaigns:
            return None
        labels = set(intent_labels)
        targeted = [
            c for c in campaigns
            if c.get("target_signals") and labels & set(c["target_signals"])
        ]
        if targeted:
            pool = targeted
        else:
            pool = [c for c in campaigns if not c.get("target_signals")]
        if not pool:
            pool = campaigns
        return min(pool, key=lambda c: c.get("priority", 1_000_000))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Token bucket — atomic ops via fcntl.flock
# ---------------------------------------------------------------------------

def _read_tokens_locked(f) -> list:
    """Read and parse the token list from an already-open, locked file."""
    f.seek(0)
    raw = f.read()
    if not raw:
        return []
    return json.loads(raw)


def pop_token() -> dict | None:
    """
    Atomically take one {"impression_id","token"} from TOKENS_FILE.
    Returns None if the file is missing or the bucket is empty.
    Safe against concurrent hook processes taking the same token.
    """
    try:
        if not TOKENS_FILE.exists():
            return None
        with open(TOKENS_FILE, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                tokens = _read_tokens_locked(f)
                if not tokens:
                    return None
                token = tokens.pop(0)
                f.seek(0)
                f.truncate()
                f.write(json.dumps(tokens))
                return token
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception:
        return None


def tokens_count() -> int:
    """Return the number of tokens currently in the bucket (0 on error)."""
    try:
        if not TOKENS_FILE.exists():
            return 0
        return len(json.loads(TOKENS_FILE.read_text()))
    except Exception:
        return 0


def tokens_low(config: dict) -> bool:
    """True when the bucket is below refill_low_watermark (default 10)."""
    return tokens_count() < config.get("refill_low_watermark", 10)


def append_tokens(new_tokens: list) -> None:
    """Atomically append new_tokens to TOKENS_FILE (creates file if missing)."""
    if not new_tokens:
        return
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
        # Open for read+write if exists, else create
        flags = os.O_RDWR | os.O_CREAT
        fd = os.open(str(TOKENS_FILE), flags, 0o600)
        try:
            with os.fdopen(fd, "r+") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.seek(0)
                    raw = f.read()
                    existing = json.loads(raw) if raw.strip() else []
                    existing.extend(new_tokens)
                    f.seek(0)
                    f.truncate()
                    f.write(json.dumps(existing))
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception:
            # fdopen took ownership; fd already closed
            pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Report buffer — atomic append via flock
# ---------------------------------------------------------------------------

def buffer_report(rec: dict) -> None:
    """Atomically append rec as one JSON line to REPORTS_FILE."""
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        fd = os.open(str(REPORTS_FILE), flags, 0o600)
        try:
            with os.fdopen(fd, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(json.dumps(rec) + "\n")
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception:
            pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Spawn refill daemon
# ---------------------------------------------------------------------------

def spawn_refill() -> None:
    """
    Launch bin/bacon-refill detached (same pattern as bacon-fetch launches
    bacon-report: start_new_session=True, stdout/stderr → DEVNULL).
    Fail-open.
    """
    try:
        refill_script = Path(__file__).parent / "bacon-refill"
        subprocess.Popen(
            [sys.executable, str(refill_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass
