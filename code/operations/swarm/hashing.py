"""Canonical JSON hashing and append-only hash-chained JSONL events."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ReplayMismatch(ValueError):
    pass


class Events:
    """Hash-chained event log. With `expected`, every emitted record must equal the recorded one."""

    def __init__(self, path=None, expected=None):
        self.path, self.expected, self.records = path, expected, []

    def emit(self, kind, data):
        body = {"index": len(self.records), "previous": self.records[-1]["sha256"] if self.records else None,
                "kind": kind, "data": deepcopy(data)}
        record = {**body, "sha256": digest(body)}
        if self.expected is not None:
            index = len(self.records)
            if index >= len(self.expected):
                raise ReplayMismatch(f"replay emits extra event {index} ({kind})")
            if record != self.expected[index]:
                raise ReplayMismatch(f"replay differs at event {index} ({kind} vs {self.expected[index]['kind']})")
        self.records.append(record)
        if self.path:
            with open(self.path, "a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
        return record


def load_events(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        records = [json.loads(line) for line in stream if line.strip()]
    verify_chain(records)
    return records


def verify_chain(records):
    previous = None
    for index, record in enumerate(records):
        body = {key: record[key] for key in ("index", "previous", "kind", "data")}
        if record["index"] != index or record["previous"] != previous or digest(body) != record["sha256"]:
            raise ReplayMismatch(f"hash chain broken at event {index}")
        previous = record["sha256"]
    return True


def compress(path):
    path = Path(path)
    target = path.with_name(path.name + ".gz")
    with open(path, "rb") as source, gzip.GzipFile(target, "wb", mtime=0) as sink:
        sink.write(source.read())
    path.unlink()
    return target
