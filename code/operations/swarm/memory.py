"""Team memory stores for the RSI arms: plain (C) and source-bound (D)."""
import hashlib
import json


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class Memory:
    def __init__(self, bound):
        self.bound, self.records, self.obligations = bound, [], []

    def call(self, agent, name, args, source_text):
        if name in ("memory_append", "memory_mark_obligation"):
            source = _sha(source_text(args["source_ref"]))  # both arms validate the reference
        if name == "memory_append":
            record = {"seq": len(self.records), "agent": agent, "key": args["key"], "content": args["content"],
                      "source_ref": args["source_ref"]}
            if self.bound:
                record["source_sha256"] = source
            self.records.append(record)
            return f"stored record {record['seq']}"
        if name == "memory_mark_obligation":
            item = {"id": len(self.obligations), "agent": agent, "text": args["text"], "source_ref": args["source_ref"]}
            if self.bound:
                item["source_sha256"] = source
            self.obligations.append(item)
            return f"recorded obligation {item['id']}"
        if name == "memory_list_obligations":
            return json.dumps({"obligations": [self._view(o, source_text) for o in self.obligations]}, sort_keys=True)
        if name == "memory_recall":
            query = args["query"].lower()
            hits = [r for r in self.records if query in r["key"].lower() or query in r["content"].lower()][-20:]
            out = {"records": [self._view(r, source_text) for r in hits]}
            if self.bound:
                out["open_obligations"] = [self._view(o, source_text) for o in self.obligations]
            return json.dumps(out, sort_keys=True)
        raise ValueError(name)

    def _view(self, item, source_text):
        view = {k: v for k, v in item.items() if k != "source_sha256"}
        if self.bound:
            try:
                current = _sha(source_text(item["source_ref"]))
            except Exception:
                current = None
            view["stale"] = current != item["source_sha256"]
            if "key" in item:
                view["conflict"] = any(r["key"] == item["key"] and r["content"] != item["content"] for r in self.records)
        return view

    def state(self):
        return {"bound": self.bound, "records": self.records, "obligations": self.obligations}
