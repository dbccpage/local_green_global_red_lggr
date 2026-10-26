"""Anthropic Messages transport (no automatic retries), recorded playback, and wave execution.

Every request is counted with the free count_tokens endpoint first; over
MAX_INPUT tokens it is refused before dispatch. Any non-success (4xx, 5xx,
transport error, timeout, max_tokens or refusal stop) is a failure and is never
retried. Credentials are read only from ANTHROPIC_API_KEY (process environment,
or the Windows user-scope variable of that name) and never recorded.
"""
from concurrent.futures import ThreadPoolExecutor
import os
import threading
import time

from .hashing import digest
from .ledger import MAX_INPUT

MODEL = "claude-haiku-5-5"
API_VERSION = "2023-06-01"
KEEP_HEADERS = ("request-id", "anthropic-organization-id", "anthropic-ratelimit-requests-remaining",
                "anthropic-ratelimit-input-tokens-remaining", "anthropic-ratelimit-output-tokens-remaining",
                "retry-after")


class HaltRun(Exception):
    pass


def api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key and os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as handle:
                key = winreg.QueryValueEx(handle, "ANTHROPIC_API_KEY")[0]
        except OSError:
            key = None
    return key or None


def count_params(payload):
    return {k: payload[k] for k in ("model", "system", "tools", "messages", "thinking", "tool_choice") if k in payload}


class AnthropicTransport:
    live = True

    def __init__(self, concurrency=16, min_interval=0.0):
        import anthropic
        key = api_key()
        if not key:
            raise HaltRun("ANTHROPIC_API_KEY is not set")
        self.anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=key, max_retries=0, timeout=180.0)
        self.sdk_version = anthropic.__version__
        self.concurrency, self.min_interval = concurrency, min_interval
        self._gate, self._last = threading.Lock(), 0.0

    def model_info(self):
        return self.client.models.retrieve(MODEL).to_dict()

    def _pace(self):
        with self._gate:
            wait = self._last + self.min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def _failure(self, stage, error):
        a = self.anthropic
        status = getattr(error, "status_code", None)
        kind = type(error).__name__
        detail = None
        if isinstance(error, a.APIStatusError):
            try:
                detail = error.response.json()
            except Exception:
                detail = {"text": error.response.text[:2000]}
        elif not isinstance(error, (a.APIConnectionError, a.APITimeoutError)):
            detail = {"text": str(error)[:500]}
        return {"stage": stage, "kind": kind, "http_status": status, "detail": detail}

    def call(self, key, payload):
        started = time.monotonic()
        try:
            self._pace()
            counted = self.client.messages.count_tokens(**count_params(payload)).input_tokens
        except Exception as error:  # noqa: BLE001 - every error is a recorded failure
            return {"outcome": "failure", "failure": self._failure("count_tokens", error), "elapsed": round(time.monotonic() - started, 3)}
        if counted > MAX_INPUT:
            return {"outcome": "refused_input", "count": counted, "elapsed": round(time.monotonic() - started, 3)}
        try:
            self._pace()
            raw = self.client.messages.with_raw_response.create(**payload)
            body = raw.http_response.json()
            headers = {h: raw.headers.get(h) for h in KEEP_HEADERS if raw.headers.get(h) is not None}
        except Exception as error:  # noqa: BLE001
            return {"outcome": "failure", "count": counted, "failure": self._failure("create", error),
                    "elapsed": round(time.monotonic() - started, 3)}
        return {"outcome": "ok", "count": counted, "body": body, "headers": headers,
                "elapsed": round(time.monotonic() - started, 3)}


class ReplayTransport:
    """Returns recorded per-request results; the payload hash must match the recording."""
    live = False

    def __init__(self, recorded, sdk_version):
        self.recorded, self.sdk_version, self.concurrency = recorded, sdk_version, 1

    def call(self, key, payload):
        item = self.recorded.get(key)
        if item is None:
            raise HaltRun(f"no recorded result for {key}")
        if item["payload_sha256"] != digest(payload):
            raise HaltRun(f"request {key} differs from the recorded payload")
        return item["result"]


class FakeTransport:
    """Deterministic offline transport for tests: `script(key, payload)` returns a response body."""
    live = False

    def __init__(self, script, sdk_version="fake"):
        self.script, self.sdk_version, self.concurrency = script, sdk_version, 4

    def call(self, key, payload):
        body = self.script(key, payload)
        if isinstance(body, dict) and body.get("__failure__"):
            return {"outcome": "failure", "count": 100, "failure": body["__failure__"], "elapsed": 0.0}
        if isinstance(body, dict) and body.get("__refuse__"):
            return {"outcome": "refused_input", "count": MAX_INPUT + 1, "elapsed": 0.0}
        return {"outcome": "ok", "count": 100, "body": body, "headers": {}, "elapsed": 0.0}


def response_failure(body, expected_model):
    """Classify a 200 response: returns a failure dict or None. Halts on model drift."""
    if not isinstance(body, dict) or body.get("type") != "message" or not isinstance(body.get("content"), list):
        return {"stage": "response", "kind": "malformed_response"}
    if expected_model is not None and body.get("model") != expected_model:
        raise HaltRun(f"resolved model changed: {body.get('model')!r} != {expected_model!r}")
    if body.get("stop_reason") in ("max_tokens", "refusal", "pause_turn", None):
        return {"stage": "response", "kind": "stop_" + str(body.get("stop_reason")), "stop_details": body.get("stop_details")}
    return None


def run_wave(transport, ledger, requests):
    """Reserve, dispatch concurrently, settle; returns {key: result} with charge info.

    `requests` is a list of (key, payload). All launched requests settle before return.
    """
    if not requests:
        return {}, "0"
    keys = [k for k, _ in requests]
    reserved = ledger.reserve_wave(keys)
    results = {}
    if transport.concurrency > 1:
        with ThreadPoolExecutor(max_workers=transport.concurrency) as pool:
            futures = {k: pool.submit(transport.call, k, p) for k, p in requests}
            for k in keys:
                try:
                    results[k] = futures[k].result()
                except HaltRun:
                    raise
                except Exception as error:  # noqa: BLE001
                    results[k] = {"outcome": "failure", "failure": {"stage": "host", "kind": type(error).__name__}, "elapsed": 0.0}
    else:
        for k, p in requests:
            results[k] = transport.call(k, p)
    # A halt above leaves reservations outstanding; reopening the ledger retains them.
    for k in keys:
        r = results[k]
        if r["outcome"] == "ok":
            usage = r["body"].get("usage") or {}
            try:
                r["charged_usd"] = str(ledger.settle(k, usage))
            except ValueError:
                r["charged_usd"] = str(ledger.fail(k))
                r["outcome"], r["failure"] = "failure", {"stage": "usage", "kind": "invalid_usage"}
        elif r["outcome"] == "refused_input":
            r["charged_usd"] = str(ledger.release(k))
        else:
            r["charged_usd"] = str(ledger.fail(k))
    return results, reserved
