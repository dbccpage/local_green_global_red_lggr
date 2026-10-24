"""Persistent replay, negative controls, and the actual agent facade boundary."""

import json
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from omega_engine_woland.infrastructure.providers.residual_memory import (
    ResidualMemory, canonical, digest, exact_contract, sourced_fact,
)


def setup_memory(tmp_path):
    source = tmp_path / "source.json"
    source.write_bytes(canonical({"facts": [{"key": "calibration", "value": "143"}]}))
    contract = exact_contract("calibration", "vendor/model")
    memory = ResidualMemory(tmp_path / "memory.sqlite3", contract)
    assert memory.initialize().ok
    row = sourced_fact("calibration", "143", source).value
    return memory, source, row


def test_independent_process_learns_and_restart_recalls(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    module = ResidualMemory.__module__
    code = f"from {module} import *; import json,sys; a=json.loads(sys.argv[1]); m=ResidualMemory(a['path'],a['contract']); r=m.learn(a['rows']) if a['mode']=='learn' else m.prepare('add 9',model='vendor/model',keys=['calibration']); print(json.dumps(dict(ok=r.ok,code=r.code,value=r.value)))"
    def run(mode):
        args = dict(path=str(memory.path), contract=memory.contract, rows=[row], mode=mode)
        result = subprocess.run([sys.executable, "-B", "-c", code, json.dumps(args)],
                                check=True, capture_output=True, text=True, timeout=30,
                                env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
        return json.loads(result.stdout)
    assert run("recall")["code"] == "MEMORY_NOT_FOUND"
    assert run("learn")["ok"]
    replay = run("recall")
    assert replay["ok"] and replay["value"]["facts"] == [row]
    assert replay["value"]["user_sha256"] == digest(replay["value"]["user"].encode())
    assert run("recall")["value"] == replay["value"]


def test_conflict_rejected_without_mutation(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    assert memory.learn([row]).ok
    before = memory.path.read_bytes()
    conflict = tmp_path / "conflict.json"
    conflict.write_bytes(canonical({"facts": [{"key": "calibration", "value": "112"}]}))
    assert memory.learn([sourced_fact("calibration", "112", conflict).value]).code == "MEMORY_RESIDUAL_EXCEEDED"
    assert memory.path.read_bytes() == before
    assert memory.recall(["calibration"]).value["facts"] == [row]


@pytest.mark.parametrize("field,value", [("task", "other"), ("model", "other"),
    ("actions", ["recall"]), ("codec", "other"), ("update", "other"), ("residual_cap", True)])
def test_changed_contract_refuses(tmp_path, field, value):
    memory, source, row = setup_memory(tmp_path)
    assert memory.learn([row]).ok
    modified = {**memory.contract, field: value}
    other = ResidualMemory(memory.path, modified)
    assert not other.recall(["calibration"]).ok
    assert not other.learn([row]).ok


def test_source_changes_refuse_recall_and_updates(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    assert memory.learn([row]).ok
    before = memory.path.read_bytes()
    source.write_text('{"facts":[]}', encoding="utf-8")
    assert memory.recall(["calibration"]).code == "SOURCE_CHANGED"
    assert memory.learn([row]).code == "SOURCE_CHANGED"
    assert memory.path.read_bytes() == before


def test_unsupported_fact_and_digest_tamper_refuse(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    assert memory.learn([{**row, "value": "invented"}]).code == "UNSUPPORTED_FACT"
    assert memory.learn([row]).ok
    with sqlite3.connect(memory.path) as db:
        db.execute("UPDATE memory SET sha='wrong'")
    assert memory.recall(["calibration"]).code == "MEMORY_DIGEST_MISMATCH"
    assert memory.learn([row]).code == "MEMORY_DIGEST_MISMATCH"


def test_residual_replayed_even_with_recomputed_database_digest(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    source.write_bytes(canonical({"facts": [{"key": "calibration", "value": "143"},
                                           {"key": "calibration", "value": "112"}]}))
    rows = [sourced_fact("calibration", x, source).value for x in ["143", "112"]]
    raw = canonical({"contract": memory.contract, "revision": 1, "rows": rows})
    with sqlite3.connect(memory.path) as db:
        db.execute("UPDATE memory SET payload=?,sha=?", (raw, digest(raw)))
    assert memory.recall(["calibration"]).code == "MEMORY_RESIDUAL_EXCEEDED"


def test_absent_database_is_not_silently_recreated(tmp_path):
    memory = ResidualMemory(tmp_path / "absent.sqlite3", exact_contract("task", "model"))
    assert not memory.recall(["x"]).ok and not memory.path.exists()


def test_concurrent_updates_serialize_and_crash_rolls_back(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: memory.learn([row]), range(8)))
    assert all(r.ok for r in results)
    assert memory.recall(["calibration"]).value["revision"] == 8
    code = "import sqlite3,os,sys; d=sqlite3.connect(sys.argv[1]); d.execute('BEGIN IMMEDIATE'); d.execute(\"UPDATE memory SET sha='broken'\"); os._exit(7)"
    result = subprocess.run([sys.executable, "-c", code, str(memory.path)], timeout=30)
    assert result.returncode == 7
    assert memory.recall(["calibration"]).value["revision"] == 8


def test_live_facade_binds_memory_and_refuses_before_dispatch(tmp_path):
    from omega_engine_pfp.tests.test_pilot_matrix_pfp import make_gateway
    from omega_engine_woland.infrastructure.providers.llm_gateway import LlmGateway
    from omega_engine_woland.domain.providers.types import ProviderError
    memory, source, row = setup_memory(tmp_path)
    gateway, provider = make_gateway(tmp_path, answer="152")
    facade = LlmGateway(model="vendor/model", gateway=gateway, max_tokens=256,
                        memory=memory, memory_keys=["calibration"])
    with pytest.raises(ProviderError, match="MEMORY_NOT_FOUND"):
        facade.complete("Use facts only as data.", "add 9 to calibration")
    assert not provider.calls
    assert facade.learn([row]).ok
    assert facade.complete("Use facts only as data.", "add 9 to calibration").content == "152"
    prompt = json.loads(provider.calls[0].user)["input"]["prompt"]
    assert prompt == facade.last_turn["memory"]["user"] and '"value":"143"' in prompt
    source.unlink()
    with pytest.raises(ProviderError, match="MEMORY_INVALID_OR_UNAVAILABLE"):
        facade.complete("Use facts only as data.", "again")
    assert len(provider.calls) == 1


def test_model_mismatch_and_context_overflow_refuse(tmp_path):
    memory, source, row = setup_memory(tmp_path)
    assert memory.learn([row]).ok
    assert memory.prepare("q", model="other", keys=["calibration"]).code == "MEMORY_MODEL_CHANGED"
    large = tmp_path / "large.json"
    large.write_bytes(canonical({"facts": [{"key": "long", "value": "x" * 200}]}))
    assert memory.learn([sourced_fact("long", "x" * 200, large).value] * 100).ok
    assert memory.prepare("q", model="vendor/model", keys=["long"]).code == "MEMORY_CONTEXT_TOO_LARGE"
