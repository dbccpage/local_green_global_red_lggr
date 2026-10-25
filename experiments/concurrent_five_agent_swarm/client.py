"""Pre-reserved concurrent requests with replay of every prompt and tool output."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import json
import threading
import time
import urllib.request

from experiments.live_five_agent_swarm.client import (
    request, reservation, charge, response_message, open_private, RunStopped,
    load_openrouter_credentials,
)

MAX_CALLS = 3000


def peak_inflight(observations):
    points = []
    for item in observations:
        start, end = item["started_ns"], item["finished_ns"]
        if type(start) is not int or type(end) is not int or not 0 <= start <= end:
            raise ValueError("invalid request time interval")
        points.extend(((start, 1), (end, -1)))
    active = peak = 0
    for _, delta in sorted(points):
        active += delta
        peak = max(peak, active)
    return peak


class BatchClient:
    """One coordinator owns budget/events; network threads return observations only.

    Reserve the entire batch before launching ANY calls, so overlapping requests
    cannot overspend the ceiling by racing on a shared balance. Unknown costs
    remain reserved. The coordinator waits for every launched request before
    settling a failure and releasing the run's budget allocation.
    """
    def __init__(self, events, budget, source=None, transport=None):
        self.events, self.limit, self.source = events, Decimal(str(budget)), source
        if not self.limit.is_finite() or not 0 < self.limit <= 10:
            raise ValueError("invalid budget")
        self.spent, self.calls, self.wave = Decimal(0), 0, 0
        self.max_inflight, self.concurrent_waves = 0, 0
        self.lock = threading.Lock()
        self.transport = transport or self.send
        self.key = None
        if source is None and transport is None:
            self.key, _ = load_openrouter_credentials()
            if not self.key:
                raise RunStopped("OpenRouter credentials unavailable")

    def send(self, payload):
        started = time.monotonic_ns()
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + self.key,
                "Content-Type": "application/json"}, method="POST")
        try:
            with open_private(req, timeout=60) as stream:
                body = stream.read().decode("utf-8")
            try:
                result = {"response": json.loads(body)}
            except ValueError:
                result = {"error": "invalid_json", "response_text": body}
        except Exception as error:
            result = {"error": type(error).__name__, "http_status": getattr(error, "code", None)}
            if isinstance(error, urllib.error.HTTPError):
                error.close()
        return {**result, "started_ns": started, "finished_ns": time.monotonic_ns()}

    def batch(self, calls):
        # Also protect against accidentally invoking this coordinator concurrently.
        with self.lock:
            return self._batch(calls)

    def _batch(self, calls):
        if not 1 <= len(calls) <= 5:
            raise ValueError("one to five requests per wave required")
        payloads = [request(model, messages) for model, messages in calls]
        reserves = [reservation(p) for p in payloads]
        if self.calls + len(calls) > MAX_CALLS or self.spent + sum(reserves) > self.limit:
            raise RunStopped("API attempt or spending ceiling reached")
        self.wave += 1
        identifiers = list(range(self.calls, self.calls+len(calls)))
        self.calls += len(calls)
        self.spent += sum(reserves)
        for ident, payload, reserved in zip(identifiers, payloads, reserves):
            self.events.emit("api_request", {"request_id": ident, "wave": self.wave,
                             "request": payload, "reserved_usd": str(reserved)})
        if self.source is None:
            with ThreadPoolExecutor(max_workers=len(calls)) as pool:
                observed = list(pool.map(self.transport, payloads))
        else:
            pos = len(self.events.records)
            observed = [self.source[pos+i]["data"]["observation"] for i in range(len(calls))]
        peak = peak_inflight(observed)
        self.max_inflight = max(self.max_inflight, peak)
        self.concurrent_waves += int(peak > 1)
        messages, stopped = [], False
        for ident, payload, reserved, obs in zip(identifiers, payloads, reserves, observed):
            if "response" in obs:
                raw = obs["response"]
                charged, reported = charge(raw, reserved)
                self.spent += charged-reserved
                self.events.emit("api_response", {"request_id": ident, "wave": self.wave,
                    "response": raw, "observation": obs, "charged_usd": str(charged), "cost_reported": reported})
                stopped |= charged > reserved
                try:
                    messages.append(response_message(raw, payload["model"]))
                except ValueError as error:
                    messages.append(error)
            else:
                self.events.emit("api_error", {"request_id": ident, "wave": self.wave,
                    "observation": obs, "charged_upper_bound_usd": str(reserved)})
                stopped = True
        self.events.emit("wave_result", {"wave": self.wave, "requests": len(calls), "peak_inflight": peak,
                                         "charged_or_reserved_usd": str(self.spent)})
        if stopped:
            raise RunStopped("provider failure or over-reservation charge; all in-flight requests settled")
        return messages
