"""Bounded live provider calls and exact request/response offline playback."""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
import hashlib
import re
import time
import urllib.error
import urllib.request

from lggr.benchmarks import load_openrouter_credentials

MODELS = ["openai/gpt-4o-mini", "anthropic/claude-haiku-4.5", "google/gemini-2.5-flash-lite",
          "openai/gpt-4o-mini", "anthropic/claude-haiku-4.5"]
MAX_CALLS, MAX_BYTES, MAX_OUTPUT = 600, 60000, 512


def event_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).hexdigest()


class RunStopped(Exception):
    pass


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Events:
    def __init__(self, path=None, expected=None):
        self.path, self.expected, self.records = path, expected, []
    def emit(self, kind, data):
        body = {"index": len(self.records), "previous": self.records[-1]["sha256"] if self.records else None,
                "kind": kind, "data": deepcopy(data)}
        record = {**body, "sha256": event_digest(body)}
        if self.expected is not None:
            if len(self.records) >= len(self.expected) or record != self.expected[len(self.records)]:
                raise ValueError(f"replay differs at event {len(self.records)} ({kind})")
        self.records.append(record)
        if self.path:
            with open(self.path, "a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
        return record


def request(model, messages):
    from .runner import TOOLS
    return {"model": model, "messages": deepcopy(messages), "tools": TOOLS, "tool_choice": "auto",
            "temperature": 0, "max_tokens": MAX_OUTPUT,
            "provider": {"max_price": {"prompt": 1, "completion": 5}, "allow_fallbacks": False}}


def reservation(payload):
    # UTF-8 bytes plus generous protocol overhead exceed text token count.
    size = len(json.dumps(payload, ensure_ascii=True).encode())
    if size > MAX_BYTES:
        raise RunStopped("request context byte limit")
    return Decimal(size + 4096) / 1000000 + Decimal(MAX_OUTPUT) * 5 / 1000000


def response_message(raw, model):
    actual = raw.get("model", "")
    if actual != model and not re.fullmatch(re.escape(model) + r"-\d{4}-\d{2}-\d{2}", actual):
        raise ValueError("provider response model differs from requested identity")
    choices = raw.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0].get("message"), dict):
        raise ValueError("provider response has no single assistant message")
    if choices[0].get("finish_reason") in ("length", "error", "content_filter"):
        raise ValueError("provider output incomplete or filtered")
    message = choices[0]["message"]
    return {key: deepcopy(message[key]) for key in ("role", "content", "tool_calls") if key in message}


def charge(raw, reserved):
    cost = raw.get("usage", {}).get("cost")
    if type(cost) in (int, float, str):
        try:
            value = Decimal(str(cost))
            if value.is_finite() and value >= 0:
                return value, True
        except InvalidOperation:
            pass
    return reserved, False


class LiveClient:
    def __init__(self, events, budget):
        self.events, self.limit = events, Decimal(str(budget))
        self.key, _ = load_openrouter_credentials()
        if not self.key:
            raise RunStopped("OpenRouter credentials unavailable")
        self.spent, self.calls = Decimal(0), 0

    def complete(self, model, messages):
        payload = request(model, messages)
        reserved = reservation(payload)
        if self.calls >= MAX_CALLS or self.spent + reserved > self.limit:
            raise RunStopped("API attempt or spending ceiling reached")
        self.calls += 1
        self.spent += reserved
        self.events.emit("api_request", {"request": payload, "reserved_usd": str(reserved)})
        started = time.monotonic()
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
              data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + self.key,
              "Content-Type": "application/json"}, method="POST")
        try:
            opener = urllib.request.build_opener(_RejectRedirects())
            with opener.open(req, timeout=60) as response:
                raw = json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            code = getattr(error, "code", None)
            if isinstance(error, urllib.error.HTTPError):
                error.close()
            self.events.emit("api_error", {"http_status": code, "kind": type(error).__name__,
                             "charged_upper_bound_usd": str(reserved)})
            raise RunStopped("provider request failed; reserved cost retained") from None
        charged, reported = charge(raw, reserved)
        self.spent += charged - reserved
        self.events.emit("api_response", {"response": raw, "elapsed_seconds": round(time.monotonic()-started, 6),
                         "charged_usd": str(charged), "cost_reported": reported})
        if charged > reserved:
            raise RunStopped("provider charge exceeded conservative reservation")
        return response_message(raw, model)


class ReplayClient:
    def __init__(self, events, source):
        self.events, self.source = events, source
        self.spent, self.calls = Decimal(0), 0
        self.limit = Decimal(source[0]["data"]["config"]["budget_usd"])
    def complete(self, model, messages):
        index = len(self.events.records)
        payload = request(model, messages)
        reserved = reservation(payload)
        if self.calls >= MAX_CALLS or self.spent + reserved > self.limit:
            raise RunStopped("API attempt or spending ceiling reached")
        self.events.emit("api_request", {"request": payload, "reserved_usd": str(reserved)})
        self.calls += 1
        next_ = self.source[len(self.events.records)]
        self.events.emit(next_["kind"], next_["data"])
        if next_["kind"] == "api_error":
            if next_["data"]["charged_upper_bound_usd"] != str(reserved):
                raise ValueError("transport cost reservation differs")
            self.spent += reserved
            raise RunStopped("provider request failed; reserved cost retained")
        if next_["kind"] != "api_response":
            raise ValueError("expected provider response event")
        charged, reported = charge(next_["data"]["response"], reserved)
        if next_["data"]["charged_usd"] != str(charged) or next_["data"]["cost_reported"] != reported:
            raise ValueError("cost summary differs from provider response")
        self.spent += charged
        if charged > reserved:
            raise RunStopped("provider charge exceeded conservative reservation")
        return response_message(next_["data"]["response"], model)
