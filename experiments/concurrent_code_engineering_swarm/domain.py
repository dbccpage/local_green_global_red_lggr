"""Real multi-module Python codebase workspace, local unit tests, and LGGR merge gate."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from lggr.streaming import (
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingDiamondCodebasePullbackMonitor,
)

CODE_SWARM_MODELS: list[str] = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4.5",
    "deepseek/deepseek-chat",
]

DIAMOND_SWARM_MODELS: list[str] = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4.5",
    "deepseek/deepseek-chat",
    "openai/gpt-4o-mini",
]

WORKER_MODULES: dict[str, str] = {
    "worker-0": "pricing",
    "worker-1": "tax_engine",
    "worker-2": "settlement_router",
}

DIAMOND_WORKER_MODULES: dict[str, str] = {
    "worker-0": "quote_anchor",
    "worker-1": "tax_branch",
    "worker-2": "fee_branch",
    "worker-3": "diamond_aggregator",
}

DIAMOND_WORKTREE_BRANCHES: dict[str, str] = {
    "worker-0": "wt/branch-a-anchor",
    "worker-1": "wt/branch-b-tax",
    "worker-2": "wt/branch-c-fee",
    "worker-3": "wt/branch-d-aggregator",
}

CANONICAL_PRICING_SOURCE = """def compute_quote(items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

MISMATCHED_TAX_SOURCE = """def apply_tax(quote, tax_bps):
    net = int(quote['net_amount_cents'])
    tax = (net * int(tax_bps)) // 10000
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': net + tax}
"""

CANONICAL_TAX_SOURCE = """def apply_tax(quote, tax_bps):
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': net + tax}
"""

DRIFTED_SETTLEMENT_SOURCE = """def route_settlement(taxed_quote, fee_bps):
    gross = int(taxed_quote['gross_cents'])
    tax = int(taxed_quote['tax_cents'])
    fee = (gross * int(fee_bps)) // 10000
    payout = gross - fee - tax
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""

CANONICAL_SETTLEMENT_SOURCE = """def route_settlement(taxed_quote, fee_bps):
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = gross - fee - tax
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""


def run_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Execute the module's isolated local unit test suite.

    Notice why Local Green (L = 1) occurs naturally in real unit suites:
    - pricing's local unit test checks subtotal=1000, discount=100, and accepts either
      'net_cents' or 'net_amount_cents' == 900.
    - tax_engine's local unit test uses a permissive mock quote containing both
      'net_cents' and 'net_amount_cents'.
    - settlement_router's local unit test checks fee_bps=0 and sum conservation, which
      does not catch computing platform_fee_cents on gross_cents instead of net_cents.
    """
    try:
        ns = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(
            module_name, source_code
        )
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": str(exc)}

    try:
        if module_name == "pricing":
            fn = ns.get("compute_quote")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_quote(items, discount_bps)"}
            out = fn([{"unit_cents": 400, "quantity": 2}, {"unit_cents": 200, "quantity": 1}], 1000)
            net_val = out.get("net_cents", out.get("net_amount_cents"))
            ok = (
                isinstance(out, dict)
                and out.get("subtotal_cents") == 1000
                and out.get("discount_cents") == 100
                and net_val == 900
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        if module_name == "tax_engine":
            fn = ns.get("apply_tax")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing apply_tax(quote, tax_bps)"}
            # Permissive unit-test mock includes both alias keys
            mock_quote = {"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900, "net_amount_cents": 900}
            out = fn(mock_quote, 2000)
            ok = (
                isinstance(out, dict)
                and out.get("tax_cents") == 180
                and out.get("gross_cents") == 1080
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        if module_name == "settlement_router":
            fn = ns.get("route_settlement")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing route_settlement(taxed_quote, fee_bps)"}
            # Local unit test tests zero-fee case and basic conservation
            mock_taxed = {"net_cents": 900, "tax_cents": 180, "gross_cents": 1080}
            out0 = fn(mock_taxed, 0)
            ok = (
                isinstance(out0, dict)
                and out0.get("gross_cents") == 1080
                and out0.get("platform_fee_cents") == 0
                and out0.get("tax_reserve_cents") == 180
                and out0.get("merchant_payout_cents") == 900
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out0}

        return {"passed": False, "module": module_name, "error": f"unknown module {module_name}"}
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": f"{type(exc).__name__}: {exc}"}


def fixture(seed: int) -> dict[str, Any]:
    """Construct the initial 3-module codebase state for a given seed."""
    kind = ("schema_and_fee_drift", "infeasible_contract", "clean_control")[seed % 3]
    if kind == "schema_and_fee_drift":
        sources = {
            "pricing": CANONICAL_PRICING_SOURCE,
            "tax_engine": MISMATCHED_TAX_SOURCE,
            "settlement_router": DRIFTED_SETTLEMENT_SOURCE,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_contract":
        sources = {
            "pricing": CANONICAL_PRICING_SOURCE,
            "tax_engine": CANONICAL_TAX_SOURCE,
            "settlement_router": CANONICAL_SETTLEMENT_SOURCE,
        }
        infeasible = {
            "upstream_locked_module": "pricing",
            "upstream_max_batch_items": 3,
            "downstream_required_min_batch_items": 5,
            "reason": "Immutable upstream pricing contract caps batch size at 3 items while downstream compliance requires >= 5 items per batch.",
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "pricing": CANONICAL_PRICING_SOURCE,
            "tax_engine": CANONICAL_TAX_SOURCE,
            "settlement_router": CANONICAL_SETTLEMENT_SOURCE,
        }
        infeasible = None
        locked_workers = []

    return {
        "seed": seed,
        "kind": kind,
        "sources": sources,
        "locked_workers": locked_workers,
        "infeasible_constraint": infeasible,
        "escalations": {},
    }


class CodeWorkspace:
    """Sandboxed multi-agent Python codebase workspace with per-module unit tests."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = WORKER_MODULES[worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_local_unit_tests(module_name, own_src)
            peer_ast = {
                m: StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(m, s)["functions"]
                for m, s in self.state["sources"].items()
            }
            return {
                "worker": worker,
                "owned_module": module_name,
                "locked": worker in self.state["locked_workers"],
                "source_code": own_src,
                "local_unit_test_result": local_res,
                "peer_module_signatures": peer_ast,
                "infeasible_constraint": self.state["infeasible_constraint"],
            }

        if name == "run_local_tests" and arguments == {}:
            own_src = self.state["sources"][module_name]
            return run_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {"escalated": True, "worker": worker, "reason": self.state["escalations"][worker]}

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_local_unit_tests(module_name, new_src)
            if not local_res.get("passed"):
                return {
                    "accepted": False,
                    "error": "patch failed local unit tests",
                    "local_unit_test_result": local_res,
                }
            self.state["sources"][module_name] = new_src
            return {
                "accepted": True,
                "module": module_name,
                "local_unit_test_result": local_res,
                "scope": "local module unit tests passed; cross-module integration is checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}


CANONICAL_QUOTE_ANCHOR_SOURCE = """def emit_base_quote(items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

INCOMPATIBLE_TAX_BRANCH_SOURCE = """def compute_tax_branch(base_quote, tax_bps):
    net = int(base_quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    return {'branch_net_cents': net, 'tax_cents': tax, 'basis_tag': 'NET_V1'}
"""

CANONICAL_TAX_BRANCH_SOURCE = """def compute_tax_branch(base_quote, tax_bps):
    net = int(base_quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    return {'net_cents': net, 'tax_cents': tax, 'basis_tag': 'NET_V1'}
"""

INCOMPATIBLE_FEE_BRANCH_SOURCE = """def compute_fee_branch(base_quote, fee_bps):
    gross_base = int(base_quote['net_amount_cents'])
    fee = (gross_base * int(fee_bps)) // 10000
    return {'net_cents': gross_base, 'platform_fee_cents': fee, 'basis_tag': 'GROSS_V2'}
"""

CANONICAL_FEE_BRANCH_SOURCE = """def compute_fee_branch(base_quote, fee_bps):
    net = int(base_quote['net_cents'])
    fee = (net * int(fee_bps)) // 10000
    return {'net_cents': net, 'platform_fee_cents': fee, 'basis_tag': 'NET_V1'}
"""

DRIFTED_DIAMOND_AGGREGATOR_SOURCE = """def aggregate_diamond_settlement(tax_leg, fee_leg):
    net = int(tax_leg['net_cents'])
    tax = int(tax_leg['tax_cents'])
    fee = int(fee_leg['platform_fee_cents'])
    gross = net + tax
    payout = gross - fee
    return {
        'net_cents': net,
        'tax_cents': tax,
        'platform_fee_cents': fee,
        'gross_cents': gross,
        'merchant_payout_cents': payout,
    }
"""

CANONICAL_DIAMOND_AGGREGATOR_SOURCE = """def aggregate_diamond_settlement(tax_leg, fee_leg):
    if int(tax_leg['net_cents']) != int(fee_leg['net_cents']):
        raise ValueError('pullback net_cents mismatch between tax_leg and fee_leg')
    if tax_leg.get('basis_tag') != 'NET_V1' or fee_leg.get('basis_tag') != 'NET_V1':
        raise ValueError('pullback basis_tag mismatch')
    net = int(tax_leg['net_cents'])
    tax = int(tax_leg['tax_cents'])
    fee = int(fee_leg['platform_fee_cents'])
    gross = net + tax
    payout = net - fee
    return {
        'net_cents': net,
        'tax_cents': tax,
        'platform_fee_cents': fee,
        'gross_cents': gross,
        'merchant_payout_cents': payout,
    }
"""


def run_diamond_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Execute each diamond module's isolated worktree unit test suite."""
    try:
        ns = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(
            module_name, source_code
        )
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": str(exc)}

    try:
        if module_name == "quote_anchor":
            fn = ns.get("emit_base_quote")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing emit_base_quote(items, discount_bps)"}
            out = fn([{"unit_cents": 400, "quantity": 2}, {"unit_cents": 200, "quantity": 1}], 1000)
            ok = (
                isinstance(out, dict)
                and out.get("subtotal_cents") == 1000
                and out.get("discount_cents") == 100
                and out.get("net_cents") == 900
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        if module_name == "tax_branch":
            fn = ns.get("compute_tax_branch")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_tax_branch(base_quote, tax_bps)"}
            mock_base = {"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900}
            out = fn(mock_base, 2000)
            net_val = out.get("net_cents", out.get("branch_net_cents")) if isinstance(out, dict) else None
            ok = (
                isinstance(out, dict)
                and net_val == 900
                and out.get("tax_cents") == 180
                and out.get("basis_tag") in ("NET_V1", "GROSS_V2")
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        if module_name == "fee_branch":
            fn = ns.get("compute_fee_branch")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_fee_branch(base_quote, fee_bps)"}
            # Branch-C local unit test uses a permissive mock containing both 'net_cents' and 'net_amount_cents'
            mock_base = {
                "subtotal_cents": 1000,
                "discount_cents": 100,
                "net_cents": 900,
                "net_amount_cents": 1000,
            }
            out = fn(mock_base, 300)
            ok = (
                isinstance(out, dict)
                and out.get("platform_fee_cents") in (27, 30)
                and out.get("basis_tag") in ("NET_V1", "GROSS_V2")
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        if module_name == "diamond_aggregator":
            fn = ns.get("aggregate_diamond_settlement")
            if not callable(fn):
                return {
                    "passed": False,
                    "module": module_name,
                    "error": "missing aggregate_diamond_settlement(tax_leg, fee_leg)",
                }
            # Local worktree unit test checks zero-tax case (tax_cents=0), so payout = gross - fee
            # passes locally (900 - 27 = 873) while failing conservation when tax_cents > 0!
            mock_tax = {"net_cents": 900, "tax_cents": 0, "basis_tag": "NET_V1"}
            mock_fee = {"net_cents": 900, "platform_fee_cents": 27, "basis_tag": "NET_V1"}
            out = fn(mock_tax, mock_fee)
            ok = (
                isinstance(out, dict)
                and out.get("net_cents") == 900
                and out.get("tax_cents") == 0
                and out.get("platform_fee_cents") == 27
                and out.get("gross_cents") == 900
                and out.get("merchant_payout_cents") == 873
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}

        return {"passed": False, "module": module_name, "error": f"unknown module {module_name}"}
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": f"{type(exc).__name__}: {exc}"}


def diamond_fixture(seed: int) -> dict[str, Any]:
    """Construct the 4-module diamond codebase state across 4 worktree branches."""
    kind = (
        "incompatible_middle_branch_extensions",
        "infeasible_diamond_contract",
        "clean_diamond_control",
    )[seed % 3]
    if kind == "incompatible_middle_branch_extensions":
        sources = {
            "quote_anchor": CANONICAL_QUOTE_ANCHOR_SOURCE,
            "tax_branch": INCOMPATIBLE_TAX_BRANCH_SOURCE,
            "fee_branch": INCOMPATIBLE_FEE_BRANCH_SOURCE,
            "diamond_aggregator": DRIFTED_DIAMOND_AGGREGATOR_SOURCE,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_diamond_contract":
        sources = {
            "quote_anchor": CANONICAL_QUOTE_ANCHOR_SOURCE,
            "tax_branch": CANONICAL_TAX_BRANCH_SOURCE,
            "fee_branch": CANONICAL_FEE_BRANCH_SOURCE,
            "diamond_aggregator": CANONICAL_DIAMOND_AGGREGATOR_SOURCE,
        }
        infeasible = {
            "upstream_locked_module": "quote_anchor",
            "upstream_currency_precision_decimals": 2,
            "downstream_required_subcent_decimals": 4,
            "reason": "Immutable upstream quote_anchor locks integer cent precision (2 decimals) while downstream diamond_aggregator compliance requires 4-decimal sub-cent settlement.",
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "quote_anchor": CANONICAL_QUOTE_ANCHOR_SOURCE,
            "tax_branch": CANONICAL_TAX_BRANCH_SOURCE,
            "fee_branch": CANONICAL_FEE_BRANCH_SOURCE,
            "diamond_aggregator": CANONICAL_DIAMOND_AGGREGATOR_SOURCE,
        }
        infeasible = None
        locked_workers = []

    return {
        "seed": seed,
        "kind": kind,
        "worktree_branches": dict(DIAMOND_WORKTREE_BRANCHES),
        "sources": sources,
        "locked_workers": locked_workers,
        "infeasible_constraint": infeasible,
        "escalations": {},
    }


class DiamondCodeWorkspace:
    """Sandboxed 4-agent diamond-dependency Python codebase workspace with git worktree branch metadata."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_diamond_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in DIAMOND_WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = DIAMOND_WORKER_MODULES[worker]
        wt_branch = self.state["worktree_branches"][worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_diamond_local_unit_tests(module_name, own_src)
            peer_ast = {
                m: StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(m, s)["functions"]
                for m, s in self.state["sources"].items()
            }
            return {
                "worker": worker,
                "worktree_branch": wt_branch,
                "owned_module": module_name,
                "diamond_topology": "quote_anchor (A) -> [tax_branch (B), fee_branch (C)] -> diamond_aggregator (D)",
                "locked": worker in self.state["locked_workers"],
                "source_code": own_src,
                "local_unit_test_result": local_res,
                "peer_module_signatures": peer_ast,
                "infeasible_constraint": self.state["infeasible_constraint"],
            }

        if name == "run_local_tests" and arguments == {}:
            own_src = self.state["sources"][module_name]
            return run_diamond_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {
                "escalated": True,
                "worker": worker,
                "worktree_branch": wt_branch,
                "reason": self.state["escalations"][worker],
            }

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_diamond_local_unit_tests(module_name, new_src)
            if not local_res.get("passed"):
                return {
                    "accepted": False,
                    "worktree_branch": wt_branch,
                    "error": "patch failed local unit tests",
                    "local_unit_test_result": local_res,
                }
            self.state["sources"][module_name] = new_src
            return {
                "accepted": True,
                "worktree_branch": wt_branch,
                "module": module_name,
                "local_unit_test_result": local_res,
                "scope": "local worktree module unit tests passed; diamond pullback integration is checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}

