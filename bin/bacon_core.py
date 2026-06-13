"""
bacon_core.py — shared importable module for the client-side auction pipeline.

Other bin scripts load this with:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    import bacon_core

All functions are fail-open: they return None / [] / False on any error and
never raise. Uses only stdlib.
"""

import base64
import fcntl
import json
import os
import random
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

AUCTION_URL_DEFAULT = "https://api.geturbacon.dev/v1/auction"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Read ~/.bacon/config.json; return {} on any error."""
    try:
        if not CONFIG_FILE.exists():
            return {}
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}


def _decode_jwt_payload(token: str) -> dict:
    """
    Decode the payload segment of a JWT (no signature verification).
    The token was obtained over TLS from Clerk, so signature check is not needed here.
    Returns {} on any error.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        seg = parts[1]
        # Pad to a multiple of 4 for base64 decoding
        seg += "=" * (4 - len(seg) % 4)
        return json.loads(base64.urlsafe_b64decode(seg))
    except Exception:
        return {}


def _token_is_expired(token: str, skew_seconds: int = 10) -> bool:
    """
    Return True if the JWT's `exp` claim is in the past (with a small clock skew).
    Returns False (not expired / unknown) on any error so we fail-open.
    """
    try:
        payload = _decode_jwt_payload(token)
        exp = payload.get("exp")
        if exp is None:
            return False  # no exp claim — treat as valid
        return time.time() > (exp - skew_seconds)
    except Exception:
        return False


def _try_refresh_token(refresh_token: str, config: dict) -> str | None:
    """
    Exchange a refresh_token for a new id_token via the Clerk token endpoint.
    Returns the new id_token on success, None on any error.
    Never raises.
    """
    try:
        import urllib.request
        import urllib.parse
        import urllib.error

        # Fetch OAuth config to get the token URL
        config_url = "https://api.geturbacon.dev/v1/auth/config"
        try:
            with urllib.request.urlopen(
                urllib.request.Request(config_url, headers={"User-Agent": "bacon-core/1.0"}),
                timeout=5,
            ) as resp:
                oauth = json.loads(resp.read())
        except Exception:
            return None

        token_url = oauth.get("token_url", "")
        client_id = oauth.get("client_id", "")
        if not token_url or not client_id:
            return None

        body = urllib.parse.urlencode({
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
        }).encode()
        req = urllib.request.Request(
            token_url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "bacon-core/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                tokens = json.loads(resp.read())
        except urllib.error.HTTPError:
            return None

        new_id_token = tokens.get("id_token", "")
        if not new_id_token:
            return None

        # Persist the new token (and updated refresh_token if the server rotates it)
        try:
            cfg = load_config()
            cfg["clerk_token"] = new_id_token
            new_refresh = tokens.get("refresh_token")
            if new_refresh:
                cfg["clerk_refresh_token"] = new_refresh
            _write_config_secure(cfg)
        except Exception:
            pass

        return new_id_token
    except Exception:
        return None


def _write_config_secure(cfg: dict) -> None:
    """
    Write cfg to CONFIG_FILE with 0o600 permissions.
    Uses os.open with O_CREAT|O_WRONLY|O_TRUNC and mode 0o600
    to ensure the file is created with restricted permissions.
    Never raises.
    """
    try:
        CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)
        data = json.dumps(cfg, indent=2)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(str(CONFIG_FILE), flags, 0o600)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(data)
        except Exception:
            pass
    except Exception:
        pass


def get_clerk_token() -> str | None:
    """
    Read the Clerk JWT token from config if present and valid (not expired).
    If the stored id_token is expired and a refresh_token is available,
    attempt a silent refresh before returning.
    Returns None if the token is not stored, invalid, or cannot be refreshed.
    Never raises; fail-open.
    """
    try:
        cfg = load_config()
        token = cfg.get("clerk_token", "").strip()
        if not token:
            return None
        # Basic structure validation: JWT must have 3 dot-separated parts
        if token.count(".") != 2:
            return None

        # Check expiry; if still valid, return immediately
        if not _token_is_expired(token):
            return token

        # Token is expired — try refresh if we have a refresh_token
        refresh_token = cfg.get("clerk_refresh_token", "").strip()
        if refresh_token:
            new_token = _try_refresh_token(refresh_token, cfg)
            if new_token:
                return new_token

        # Expired and no refresh succeeded — treat as absent
        return None
    except Exception:
        return None


def get_auth_header() -> dict:
    """
    Return a dict to add to HTTP headers for the Authorization header.
    If a valid Clerk token exists, return {"Authorization": "Bearer <token>"}.
    Otherwise return an empty dict (dual-mode: token-less installs still work).
    Never raises; never logs token values.
    """
    try:
        token = get_clerk_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
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

def select_winner(campaigns: list, intent_labels, config: dict | None = None) -> dict | None:
    """
    Port of the server-side auction, run entirely client-side.

    intent_labels — set or list of label strings e.g. {"intent_auth"}.
    config        — optional config dict; when provided, campaigns whose
                    ``category`` appears in ``blocked_categories`` are
                    excluded before the auction runs.

    Selection is a WEIGHTED-RANDOM rotation (weight ∝ 1/priority, so priority 1 =
    highest bidder wins most often) rather than always the single top bid. This
    keeps the auction bid-respecting while rotating every eligible campaign in —
    so the no-intent surfaces (spinner/statusline) don't show the same advertiser
    forever, and tied-intent campaigns share the inventory.
    """
    try:
        if not campaigns:
            return None

        # Apply blocked_categories filter from local config (fail-open).
        blocked = set()
        if config:
            try:
                blocked = set(config.get("blocked_categories") or [])
            except Exception:
                pass
        if blocked:
            campaigns = [c for c in campaigns if c.get("category", "") not in blocked]
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

        # Weighted-random rotation: weight ∝ 1/priority. Higher bidders win more
        # often, but lower bidders still rotate in (no single advertiser owns a
        # surface). A pool of one returns that one deterministically.
        weights = [1.0 / max(1, c.get("priority", 1_000_000)) for c in pool]
        if sum(weights) <= 0:
            return min(pool, key=lambda c: c.get("priority", 1_000_000))
        return random.choices(pool, weights=weights, k=1)[0]
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
