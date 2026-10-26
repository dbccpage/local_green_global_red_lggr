"""Tool schemas (strict), workspace state and validated host-side tool execution."""
import json

from .domain import global_contract_text, local_contract_text, local_report

STATUSES = ["success", "concern", "blocked"]
VERDICTS = ["accept", "reject", "defer", "model_mismatch"]
MAX_TEXT = 2000


def _tool(name, description, properties, required=None):
    return {"name": name, "description": description, "strict": True,
            "input_schema": {"type": "object", "properties": properties,
                             "required": list(properties) if required is None else required,
                             "additionalProperties": False}}


S = {"type": "string"}
LOCAL_TOOLS = [
    _tool("read_contract", "Read a public contract: 'global' (global contract and hidden-parameter domains) or a module name (its local contract). Free.", {"name": S}),
    _tool("read_file", "Read a workspace file, e.g. modules/<name>.cfg. Free.", {"path": S}),
    _tool("write_file", "Replace the full content of YOUR OWN module file (implementers only). Free.", {"path": S, "content": S}),
    _tool("run_local_tests", "Run the local tests of YOUR OWN module (implementers only). Free; never reveals hidden values.", {}),
    _tool("post_note", "Post a short note to the team board with your current status (success, concern or blocked). Free.",
          {"text": S, "status": {"type": "string", "enum": STATUSES}}),
]
CONTROLLER_TOOLS = [
    _tool("run_check", "Controller phase only: run one candidate check by id. Costs its listed units from the verification budget.", {"check_id": S}),
    _tool("submit_verdict", "Controller phase only: submit the final verdict on the frozen snapshot and end the session.",
          {"verdict": {"type": "string", "enum": VERDICTS}, "explanation": S, "cited_check_ids": {"type": "array", "items": S}}),
]
MEMORY_TOOLS = [
    _tool("memory_append", "Store a durable team memory record. source_ref names what it is based on, e.g. 'contract:global', 'contract:<module>' or 'file:<path>'.",
          {"key": S, "content": S, "source_ref": S}),
    _tool("memory_recall", "Search team memory (substring of key or content; empty query lists everything).", {"query": S}),
    _tool("memory_mark_obligation", "Record an open obligation the team must honour later, tied to a source_ref.", {"text": S, "source_ref": S}),
    _tool("memory_list_obligations", "List recorded obligations.", {}),
]
SWARM_TOOLS = LOCAL_TOOLS + CONTROLLER_TOOLS
RSI_TOOLS = LOCAL_TOOLS + MEMORY_TOOLS
TOOLSETS = {"swarm": SWARM_TOOLS, "rsi": RSI_TOOLS}

PERMISSIONS = {
    "proposal": {"read_contract", "read_file", "write_file", "run_local_tests", "post_note"},
    "repair": {"read_contract", "read_file", "write_file", "run_local_tests", "post_note"},
    "controller": {"read_contract", "read_file", "run_check", "submit_verdict"},
    "rsi_learn": {"read_contract", "read_file", "write_file", "run_local_tests", "post_note",
                  "memory_append", "memory_recall", "memory_mark_obligation", "memory_list_obligations"},
    "rsi_restart": {"read_contract", "read_file", "run_local_tests", "post_note",
                    "memory_append", "memory_recall", "memory_mark_obligation", "memory_list_obligations"},
}
PERMISSIONS["rsi_use"] = PERMISSIONS["rsi_learn"]


class ToolError(Exception):
    pass


class Denied(ToolError):
    """A well-formed call refused by phase permissions or file ownership."""


def validate(toolset, name, args):
    spec = next((t for t in TOOLSETS[toolset] if t["name"] == name), None)
    if spec is None:
        raise ToolError(f"unknown tool {name!r}")
    schema = spec["input_schema"]
    if not isinstance(args, dict) or set(args) != set(schema["properties"]):
        raise ToolError("arguments must contain exactly: " + ", ".join(schema["properties"]))
    for key, prop in schema["properties"].items():
        value = args[key]
        if prop["type"] == "string":
            if not isinstance(value, str) or len(value) > MAX_TEXT:
                raise ToolError(f"{key} must be a string of at most {MAX_TEXT} characters")
            if "enum" in prop and value not in prop["enum"]:
                raise ToolError(f"{key} must be one of {prop['enum']}")
        elif prop["type"] == "array":
            if not isinstance(value, list) or len(value) > 16 or not all(isinstance(v, str) and len(v) <= 16 for v in value):
                raise ToolError(f"{key} must be a list of at most 16 short strings")
    return args


def template(module):
    lines = [f"# module {module['name']}: set every parameter as `name = integer` (see your local contract)"]
    lines += [f"# {p} = ?" for p in module["params"]]
    return "\n".join(lines) + "\n"


class Workspace:
    """Files, team board and per-agent status for one (instance, draw[, arm])."""

    def __init__(self, instance):
        self.instance = instance
        self.files = {m["file"]: template(m) for m in instance["modules"]}
        self.owner = {m["owner"]: m for m in instance["modules"]}
        self.board, self.status, self.write_order = [], {}, []

    def fork(self, instance=None):
        other = Workspace.__new__(Workspace)
        other.instance = instance or self.instance
        other.files, other.owner = dict(self.files), {m["owner"]: m for m in other.instance["modules"]}
        other.board, other.status, other.write_order = list(self.board), dict(self.status), list(self.write_order)
        return other

    def contract(self, name):
        if name == "global":
            return global_contract_text(self.instance)
        module = next((m for m in self.instance["modules"] if m["name"] == name), None)
        if module is None:
            raise ToolError("contract name must be 'global' or one of: " + ", ".join(m["name"] for m in self.instance["modules"]))
        return local_contract_text(module)

    def source_text(self, ref):
        kind, _, name = ref.partition(":")
        if kind == "contract":
            return self.contract(name)
        if kind == "file" and name in self.files:
            return self.files[name]
        raise ToolError("source_ref must be 'contract:global', 'contract:<module>' or 'file:<path>'")

    def execute(self, agent, phase, wave, name, args, memory=None, checks=None):
        """Return (text, is_error). `checks` is the controller's check handler."""
        if name not in PERMISSIONS[phase]:
            raise Denied(f"{name} is not available in the {phase} phase")
        if name == "read_contract":
            return self.contract(args["name"])
        if name == "read_file":
            if args["path"] not in self.files:
                raise ToolError("no such file; files: " + ", ".join(sorted(self.files)))
            return self.files[args["path"]]
        if name == "write_file":
            module = self.owner.get(agent)
            if module is None or args["path"] != module["file"]:
                raise Denied("you may write only your own module file" + (f" ({module['file']})" if module else "; you own none"))
            self.files[module["file"]] = args["content"]
            self.write_order = [m for m in self.write_order if m != module["name"]] + [module["name"]]
            return f"wrote {module['file']} ({len(args['content'])} characters)"
        if name == "run_local_tests":
            module = self.owner.get(agent)
            if module is None:
                raise Denied("you own no module; local tests are run by module owners")
            return json.dumps(local_report(self.instance, module, self.files), sort_keys=True)
        if name == "post_note":
            self.board.append({"agent": agent, "wave": wave, "phase": phase, "status": args["status"], "text": args["text"]})
            self.status[agent] = args["status"]
            return "posted"
        if name.startswith("memory_"):
            return memory.call(agent, name, args, self.source_text)
        if name in ("run_check", "submit_verdict"):
            return checks(name, args)
        raise ToolError(f"unknown tool {name!r}")
