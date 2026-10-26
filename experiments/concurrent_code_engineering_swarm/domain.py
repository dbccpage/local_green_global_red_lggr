"""Real multi-module Python codebase workspace, local unit tests, and LGGR merge gate."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from lggr.streaming import (
    StreamingCodebaseCatalystEvolutionMonitor,
    StreamingCodebaseCoalitionalMonitor,
    StreamingCodebaseInterfaceMergeMonitor,
    StreamingCodebaseReplayOrderMonitor,
    StreamingDiamondCodebasePullbackMonitor,
    StreamingStatefulCodebaseDFAMonitor,
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


DEBT_SHIM_PRICING_SOURCE = """def _legacy_discount_shim(raw_subtotal):
    return int(raw_subtotal)

def compute_quote(items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    return {
        'subtotal_cents': subtotal,
        'discount_cents': discount,
        'net_cents': net,
        'legacy_subtotal_cents': subtotal,
    }
"""

DEBT_SHIM_TAX_ENGINE_SOURCE = """def _deprecated_tax_hook(net_val):
    return int(net_val)

def apply_tax(quote, tax_bps):
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    return {
        'net_cents': net,
        'tax_cents': tax,
        'gross_cents': gross,
        'deprecated_gross_v0': gross,
    }
"""

DEBT_SHIM_SETTLEMENT_ROUTER_SOURCE = """def _compat_fee_fallback(gross_val):
    return int(gross_val)

def route_settlement(taxed_quote, fee_bps):
    gross = int(taxed_quote['gross_cents'])
    tax = int(taxed_quote['tax_cents'])
    net = int(taxed_quote['net_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = net - fee
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
        'shim_payout_cents': payout,
    }
"""


def catalyst_fixture(seed: int) -> dict[str, Any]:
    """Construct the 3-module codebase state after iterative feature tickets (t = 1, 2, 3)."""
    kind = (
        "multi_ticket_catalyst_debt_breach",
        "infeasible_catalyst_budget_lock",
        "clean_catalyst_control",
    )[seed % 3]
    if kind == "multi_ticket_catalyst_debt_breach":
        sources = {
            "pricing": DEBT_SHIM_PRICING_SOURCE,
            "tax_engine": DEBT_SHIM_TAX_ENGINE_SOURCE,
            "settlement_router": DEBT_SHIM_SETTLEMENT_ROUTER_SOURCE,
        }
        previous_catalyst_debt = 4
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_catalyst_budget_lock":
        sources = {
            "pricing": DEBT_SHIM_PRICING_SOURCE,
            "tax_engine": DEBT_SHIM_TAX_ENGINE_SOURCE,
            "settlement_router": DEBT_SHIM_SETTLEMENT_ROUTER_SOURCE,
        }
        previous_catalyst_debt = 4
        infeasible = {
            "locked_legacy_consumers_require_all_shims": True,
            "minimum_required_shim_symbols": 6,
            "global_catalyst_ceiling": 4,
            "reason": (
                "Immutable external legacy callers lock all 6 compatibility shims "
                "(_legacy_discount_shim, legacy_subtotal_cents, _deprecated_tax_hook, "
                "deprecated_gross_v0, _compat_fee_fallback, shim_payout_cents -> C_t >= 6) "
                "while governance enforces global catalyst complexity ceiling tau_cat = 4."
            ),
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "pricing": CANONICAL_PRICING_SOURCE,
            "tax_engine": CANONICAL_TAX_SOURCE,
            "settlement_router": CANONICAL_SETTLEMENT_SOURCE,
        }
        previous_catalyst_debt = 0
        infeasible = None
        locked_workers = []

    return {
        "seed": seed,
        "kind": kind,
        "ticket_id": "ticket_3_conservation_and_rejuvenation",
        "previous_catalyst_debt": previous_catalyst_debt,
        "per_ticket_local_tolerance": 2,
        "global_catalyst_ceiling": 4,
        "sources": sources,
        "locked_workers": locked_workers,
        "infeasible_constraint": infeasible,
        "escalations": {},
    }


class CatalystCodeWorkspace(CodeWorkspace):
    """Sandboxed 3-agent Python codebase workspace tracking iterative feature-ticket catalyst state."""

    def inspect_module_debt(self, module_name: str, src: str) -> dict[str, Any]:
        spec = next(
            s
            for s in StreamingCodebaseCatalystEvolutionMonitor.CANONICAL_CATALYST_MODULE_SPEC.values()
            if s["module"] == module_name
        )
        local_res = run_local_unit_tests(module_name, src)
        sample_out = local_res.get("sample_output") if isinstance(local_res, dict) else None
        return StreamingCodebaseCatalystEvolutionMonitor.inspect_module_catalyst_debt(
            module_name,
            src,
            sample_out if isinstance(sample_out, dict) else None,
            spec["function"],
            spec["return_keys"],
        )

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = WORKER_MODULES[worker]
        if name == "inspect_workspace" and arguments == {}:
            base = super().tool(worker, name, arguments)
            own_src = self.state["sources"][module_name]
            base["ticket_id"] = self.state.get("ticket_id", "ticket_3_conservation_and_rejuvenation")
            base["per_ticket_local_tolerance"] = self.state.get("per_ticket_local_tolerance", 2)
            base["global_catalyst_ceiling"] = self.state.get("global_catalyst_ceiling", 4)
            base["module_catalyst_debt_report"] = self.inspect_module_debt(module_name, own_src)
            return base
        return super().tool(worker, name, arguments)


DFA_WORKER_MODULES: dict[str, str] = {
    "worker-0": "pricing_tx",
    "worker-1": "tax_tx",
    "worker-2": "settlement_tx",
}

UNRELEASED_PRICING_TX_SOURCE = """def execute_pricing_tx(session, items, discount_bps):
    session.acquire()
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    session.commit()
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

CANONICAL_PRICING_TX_SOURCE = """def execute_pricing_tx(session, items, discount_bps):
    session.acquire()
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    session.commit()
    session.release()
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

UNRELEASED_TAX_TX_SOURCE = """def execute_tax_tx(session, quote, tax_bps):
    session.acquire()
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    session.commit()
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': gross}
"""

CANONICAL_TAX_TX_SOURCE = """def execute_tax_tx(session, quote, tax_bps):
    session.acquire()
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    session.commit()
    session.release()
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': gross}
"""

UNRELEASED_SETTLEMENT_TX_SOURCE = """def execute_settlement_tx(session, taxed_quote, fee_bps):
    session.acquire()
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = gross - fee - tax
    session.commit()
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""

CANONICAL_SETTLEMENT_TX_SOURCE = """def execute_settlement_tx(session, taxed_quote, fee_bps):
    session.acquire()
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = gross - fee - tax
    session.commit()
    session.release()
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""


def run_dfa_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Run isolated module unit tests on a fresh TransactionSession initialized at q0_idle."""
    ast_info = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(module_name, source_code)
    if not ast_info["syntax_ok"] or not ast_info["sandbox_ok"]:
        return {
            "passed": False,
            "module": module_name,
            "error": ast_info.get("error") or str(ast_info.get("sandbox_violations")),
        }
    try:
        ns = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(module_name, source_code)
        sess = StreamingStatefulCodebaseDFAMonitor.new_session(raise_on_trap=False)
        if module_name == "pricing_tx":
            fn = ns.get("execute_pricing_tx")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing execute_pricing_tx"}
            out = fn(sess, [{"unit_cents": 400, "quantity": 2}, {"unit_cents": 200, "quantity": 1}], 1000)
            ok = (
                isinstance(out, dict)
                and out.get("subtotal_cents") == 1000
                and out.get("discount_cents") == 100
                and out.get("net_cents") == 900
                and sess.state in ("q0_idle", "q2_done")
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_session_tokens": list(sess.tokens),
                "local_session_end_state": sess.state,
            }
        if module_name == "tax_tx":
            fn = ns.get("execute_tax_tx")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing execute_tax_tx"}
            out = fn(sess, {"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900}, 2000)
            ok = (
                isinstance(out, dict)
                and out.get("net_cents") == 900
                and out.get("tax_cents") == 180
                and out.get("gross_cents") == 1080
                and sess.state in ("q0_idle", "q2_done")
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_session_tokens": list(sess.tokens),
                "local_session_end_state": sess.state,
            }
        if module_name == "settlement_tx":
            fn = ns.get("execute_settlement_tx")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing execute_settlement_tx"}
            out = fn(sess, {"net_cents": 900, "tax_cents": 180, "gross_cents": 1080}, 300)
            ok = (
                isinstance(out, dict)
                and out.get("gross_cents") == 1080
                and out.get("platform_fee_cents") == 27
                and out.get("tax_reserve_cents") == 180
                and out.get("merchant_payout_cents") == 873
                and sess.state in ("q0_idle", "q2_done")
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_session_tokens": list(sess.tokens),
                "local_session_end_state": sess.state,
            }
        return {"passed": False, "module": module_name, "error": f"unknown module {module_name}"}
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": f"{type(exc).__name__}: {exc}"}


def dfa_fixture(seed: int) -> dict[str, Any]:
    """Construct the 3-module stateful transaction codebase state."""
    kind = (
        "unreleased_session_lock_trap",
        "infeasible_dfa_hold_lock",
        "clean_dfa_reset_control",
    )[seed % 3]
    if kind == "unreleased_session_lock_trap":
        sources = {
            "pricing_tx": UNRELEASED_PRICING_TX_SOURCE,
            "tax_tx": UNRELEASED_TAX_TX_SOURCE,
            "settlement_tx": UNRELEASED_SETTLEMENT_TX_SOURCE,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_dfa_hold_lock":
        sources = {
            "pricing_tx": UNRELEASED_PRICING_TX_SOURCE,
            "tax_tx": UNRELEASED_TAX_TX_SOURCE,
            "settlement_tx": UNRELEASED_SETTLEMENT_TX_SOURCE,
        }
        infeasible = {
            "upstream_locked_module": "pricing_tx",
            "upstream_required_terminal_state": "q2_done",
            "downstream_required_entry_state": "q0_idle",
            "reason": (
                "Immutable upstream audit hook locks pricing_tx in post-commit state 'q2_done' "
                "(forbidding session.release()), while downstream tax_tx requires 'q0_idle' on entry."
            ),
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "pricing_tx": CANONICAL_PRICING_TX_SOURCE,
            "tax_tx": CANONICAL_TAX_TX_SOURCE,
            "settlement_tx": CANONICAL_SETTLEMENT_TX_SOURCE,
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


class StatefulDFACodeWorkspace:
    """Sandboxed 3-agent stateful transaction codebase workspace."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_dfa_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in DFA_WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = DFA_WORKER_MODULES[worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_dfa_local_unit_tests(module_name, own_src)
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
            return run_dfa_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {
                "escalated": True,
                "worker": worker,
                "reason": self.state["escalations"][worker],
            }

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_dfa_local_unit_tests(module_name, new_src)
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
                "scope": "isolated fresh-session unit tests passed; shared-session DFA concatenation is checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}


REPLAY_WORKER_MODULES: dict[str, str] = {
    "worker-0": "pricing_events",
    "worker-1": "tax_events",
    "worker-2": "settlement_events",
}

UNBARRIERED_PRICING_EVENTS_SOURCE = """def emit_pricing_events(bus, items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    bus.publish('pricing_escrow', net, causal_index=1)
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

CANONICAL_PRICING_EVENTS_SOURCE = """def emit_pricing_events(bus, items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    tax_withholding_buffer = (net * 2000) // 10000
    bus.publish('pricing_escrow', net - tax_withholding_buffer, causal_index=1)
    bus.commit_barrier(1)
    return {'subtotal_cents': subtotal, 'discount_cents': discount, 'net_cents': net}
"""

UNBARRIERED_TAX_EVENTS_SOURCE = """def emit_tax_events(bus, quote, tax_bps):
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    bus.publish('tax_escrow', tax, causal_index=2)
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': gross}
"""

CANONICAL_TAX_EVENTS_SOURCE = """def emit_tax_events(bus, quote, tax_bps):
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    bus.publish('tax_escrow', tax, causal_index=2)
    bus.commit_barrier(2)
    return {'net_cents': net, 'tax_cents': tax, 'gross_cents': gross}
"""

UNBARRIERED_SETTLEMENT_EVENTS_SOURCE = """def emit_settlement_events(bus, taxed_quote, fee_bps):
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = gross - fee - tax
    bus.publish('settlement_release', -(payout + fee), causal_index=3, priority_arrival=True)
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""

CANONICAL_SETTLEMENT_EVENTS_SOURCE = """def emit_settlement_events(bus, taxed_quote, fee_bps):
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    fee = (net * int(fee_bps)) // 10000
    payout = gross - fee - tax
    bus.publish('settlement_release', -(net - tax), causal_index=3, priority_arrival=False)
    bus.commit_barrier(3)
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""


def run_replay_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Run isolated module unit tests on a fresh AsyncEscrowBus(prefix_budget=900)."""
    ast_info = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(module_name, source_code)
    if not ast_info["syntax_ok"] or not ast_info["sandbox_ok"]:
        return {
            "passed": False,
            "module": module_name,
            "error": ast_info.get("error") or str(ast_info.get("sandbox_violations")),
        }
    try:
        ns = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(module_name, source_code)
        bus = StreamingCodebaseReplayOrderMonitor.new_bus(prefix_budget=900)
        if module_name == "pricing_events":
            fn = ns.get("emit_pricing_events")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing emit_pricing_events"}
            out = fn(bus, [{"unit_cents": 400, "quantity": 2}, {"unit_cents": 200, "quantity": 1}], 1000)
            ok = (
                isinstance(out, dict)
                and out.get("subtotal_cents") == 1000
                and out.get("discount_cents") == 100
                and out.get("net_cents") == 900
                and len(bus.events) == 1
                and bus.local_max_prefix() <= 900
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_bus_events": list(bus.events),
                "local_bus_barriers": list(bus.barriers),
                "local_max_prefix_cents": bus.local_max_prefix(),
            }
        if module_name == "tax_events":
            fn = ns.get("emit_tax_events")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing emit_tax_events"}
            out = fn(bus, {"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900}, 2000)
            ok = (
                isinstance(out, dict)
                and out.get("net_cents") == 900
                and out.get("tax_cents") == 180
                and out.get("gross_cents") == 1080
                and len(bus.events) == 1
                and bus.local_max_prefix() <= 900
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_bus_events": list(bus.events),
                "local_bus_barriers": list(bus.barriers),
                "local_max_prefix_cents": bus.local_max_prefix(),
            }
        if module_name == "settlement_events":
            fn = ns.get("emit_settlement_events")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing emit_settlement_events"}
            out = fn(bus, {"net_cents": 900, "tax_cents": 180, "gross_cents": 1080}, 300)
            ok = (
                isinstance(out, dict)
                and out.get("gross_cents") == 1080
                and out.get("platform_fee_cents") == 27
                and out.get("tax_reserve_cents") == 180
                and out.get("merchant_payout_cents") == 873
                and len(bus.events) == 1
                and bus.local_max_prefix() <= 900
            )
            return {
                "passed": bool(ok),
                "module": module_name,
                "sample_output": out,
                "local_bus_events": list(bus.events),
                "local_bus_barriers": list(bus.barriers),
                "local_max_prefix_cents": bus.local_max_prefix(),
            }
        return {"passed": False, "module": module_name, "error": f"unknown module {module_name}"}
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": f"{type(exc).__name__}: {exc}"}


def replay_fixture(seed: int) -> dict[str, Any]:
    """Construct the 3-module asynchronous event-driven escrow codebase state."""
    kind = (
        "arrival_masked_replay_breach",
        "infeasible_escrow_prefix_budget_contradiction",
        "clean_replay_barrier_control",
    )[seed % 3]
    if kind == "arrival_masked_replay_breach":
        sources = {
            "pricing_events": UNBARRIERED_PRICING_EVENTS_SOURCE,
            "tax_events": UNBARRIERED_TAX_EVENTS_SOURCE,
            "settlement_events": UNBARRIERED_SETTLEMENT_EVENTS_SOURCE,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_escrow_prefix_budget_contradiction":
        sources = {
            "pricing_events": UNBARRIERED_PRICING_EVENTS_SOURCE,
            "tax_events": UNBARRIERED_TAX_EVENTS_SOURCE,
            "settlement_events": UNBARRIERED_SETTLEMENT_EVENTS_SOURCE,
        }
        infeasible = {
            "upstream_locked_module": "pricing_events",
            "locked_escrow_reservation_cents": 1000,
            "global_prefix_budget_cents": 900,
            "reason": (
                "Immutable upstream hold policy forces pricing_events to reserve unnetted subtotal "
                "1000 cents (> prefix_budget 900 cents) while global escrow bus enforces B_prefix = 900."
            ),
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "pricing_events": CANONICAL_PRICING_EVENTS_SOURCE,
            "tax_events": CANONICAL_TAX_EVENTS_SOURCE,
            "settlement_events": CANONICAL_SETTLEMENT_EVENTS_SOURCE,
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


class ReplayOrderCodeWorkspace:
    """Sandboxed 3-agent asynchronous event-driven escrow codebase workspace."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_replay_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in REPLAY_WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = REPLAY_WORKER_MODULES[worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_replay_local_unit_tests(module_name, own_src)
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
            return run_replay_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {
                "escalated": True,
                "worker": worker,
                "reason": self.state["escalations"][worker],
            }

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_replay_local_unit_tests(module_name, new_src)
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
                "scope": "isolated fresh-bus unit tests passed; shared-bus replay-order envelope & causal barriers are checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}


COALITIONAL_WORKER_MODULES: dict[str, str] = {
    "worker-0": "pricing_coalition",
    "worker-1": "tax_coalition",
    "worker-2": "settlement_coalition",
}

SHIM_PRICING_COALITION_SOURCE = """def compute_pricing_coalition(items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    return {
        'subtotal_cents': subtotal,
        'discount_cents': discount,
        'net_cents': net,
        'fee_basis_cents': subtotal,
    }
"""

CANONICAL_PRICING_COALITION_SOURCE = """def compute_pricing_coalition(items, discount_bps):
    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)
    discount = (subtotal * int(discount_bps)) // 10000
    net = subtotal - discount
    return {
        'subtotal_cents': subtotal,
        'discount_cents': discount,
        'net_cents': net,
        'fee_basis_cents': net,
    }
"""

CANONICAL_TAX_COALITION_SOURCE = """def compute_tax_coalition(quote, tax_bps):
    net = int(quote['net_cents'])
    tax = (net * int(tax_bps)) // 10000
    gross = net + tax
    basis = int(quote.get('fee_basis_cents', net))
    return {
        'net_cents': net,
        'tax_cents': tax,
        'gross_cents': gross,
        'fee_basis_cents': basis,
    }
"""

SHIM_SETTLEMENT_COALITION_SOURCE = """def compute_settlement_coalition(taxed_quote, fee_bps):
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    basis = max(int(taxed_quote.get('fee_basis_cents', net)), 1000)
    fee = (basis * int(fee_bps)) // 10000
    payout = gross - fee - tax
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""

CANONICAL_SETTLEMENT_COALITION_SOURCE = """def compute_settlement_coalition(taxed_quote, fee_bps):
    net = int(taxed_quote['net_cents'])
    tax = int(taxed_quote['tax_cents'])
    gross = int(taxed_quote['gross_cents'])
    basis = int(taxed_quote.get('fee_basis_cents', net))
    fee = (basis * int(fee_bps)) // 10000
    payout = gross - fee - tax
    return {
        'gross_cents': gross,
        'platform_fee_cents': fee,
        'tax_reserve_cents': tax,
        'merchant_payout_cents': payout,
    }
"""


def run_coalitional_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Run isolated module unit tests on coalitional settlement modules."""
    ast_info = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(module_name, source_code)
    if not ast_info["syntax_ok"] or not ast_info["sandbox_ok"]:
        return {
            "passed": False,
            "module": module_name,
            "error": ast_info.get("error") or str(ast_info.get("sandbox_violations")),
        }
    try:
        ns = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(module_name, source_code)
        if module_name == "pricing_coalition":
            fn = ns.get("compute_pricing_coalition")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_pricing_coalition"}
            out = fn([{"unit_cents": 400, "quantity": 2}, {"unit_cents": 200, "quantity": 1}], 1000)
            ok = (
                isinstance(out, dict)
                and out.get("subtotal_cents") == 1000
                and out.get("discount_cents") == 100
                and out.get("net_cents") == 900
                and out.get("fee_basis_cents") in (900, 1000)
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}
        if module_name == "tax_coalition":
            fn = ns.get("compute_tax_coalition")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_tax_coalition"}
            out = fn(
                {"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900, "fee_basis_cents": 900},
                2000,
            )
            ok = (
                isinstance(out, dict)
                and out.get("net_cents") == 900
                and out.get("tax_cents") == 180
                and out.get("gross_cents") == 1080
                and out.get("fee_basis_cents") == 900
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}
        if module_name == "settlement_coalition":
            fn = ns.get("compute_settlement_coalition")
            if not callable(fn):
                return {"passed": False, "module": module_name, "error": "missing compute_settlement_coalition"}
            # Local unit test checks zero-fee baseline (fee_bps=0), passing under both basis=900 and basis=1000
            out = fn(
                {"net_cents": 900, "tax_cents": 180, "gross_cents": 1080, "fee_basis_cents": 900},
                0,
            )
            ok = (
                isinstance(out, dict)
                and out.get("gross_cents") == 1080
                and out.get("platform_fee_cents") == 0
                and out.get("tax_reserve_cents") == 180
                and out.get("merchant_payout_cents") == 900
            )
            return {"passed": bool(ok), "module": module_name, "sample_output": out}
        return {"passed": False, "module": module_name, "error": f"unknown module {module_name}"}
    except Exception as exc:
        return {"passed": False, "module": module_name, "error": f"{type(exc).__name__}: {exc}"}


def coalitional_fixture(seed: int) -> dict[str, Any]:
    """Construct the 3-module coalitional fault-masking codebase state."""
    kind = (
        "synergistic_leave_one_out_masked_shims",
        "infeasible_coalitional_fee_floor_lock",
        "clean_coalitional_control",
    )[seed % 3]
    if kind == "synergistic_leave_one_out_masked_shims":
        sources = {
            "pricing_coalition": SHIM_PRICING_COALITION_SOURCE,
            "tax_coalition": CANONICAL_TAX_COALITION_SOURCE,
            "settlement_coalition": SHIM_SETTLEMENT_COALITION_SOURCE,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_coalitional_fee_floor_lock":
        sources = {
            "pricing_coalition": SHIM_PRICING_COALITION_SOURCE,
            "tax_coalition": CANONICAL_TAX_COALITION_SOURCE,
            "settlement_coalition": SHIM_SETTLEMENT_COALITION_SOURCE,
        }
        infeasible = {
            "upstream_locked_module": "pricing_coalition",
            "locked_fee_basis_cents": 1000,
            "required_canonical_fee_cents": 27,
            "reason": (
                "Immutable upstream tariff lock forces pricing_coalition to emit fee_basis_cents = 1000 "
                "(30-cent fee at 300 bps) while downstream settlement audit requires 27-cent fee."
            ),
        }
        locked_workers = ["worker-0"]
    else:
        sources = {
            "pricing_coalition": CANONICAL_PRICING_COALITION_SOURCE,
            "tax_coalition": CANONICAL_TAX_COALITION_SOURCE,
            "settlement_coalition": CANONICAL_SETTLEMENT_COALITION_SOURCE,
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


class CoalitionalCodeWorkspace:
    """Sandboxed 3-agent coalitional fault-masking codebase workspace."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_coalitional_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in COALITIONAL_WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = COALITIONAL_WORKER_MODULES[worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_coalitional_local_unit_tests(module_name, own_src)
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
            return run_coalitional_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {
                "escalated": True,
                "worker": worker,
                "reason": self.state["escalations"][worker],
            }

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_coalitional_local_unit_tests(module_name, new_src)
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
                "scope": "isolated unit tests passed; 2^3 coalitional Shapley attribution is checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}


# ---------------------------------------------------------------------------
# 3-Module Mayer-Vietoris Disconnected Overlap Coboundary Codebase (`--topology mayer_vietoris`)
# ---------------------------------------------------------------------------

MV_WORKER_MODULES: dict[str, str] = {
    "worker-0": "pricing_mv",
    "worker-1": "tax_mv",
    "worker-2": "settlement_mv",
}

CANONICAL_PRICING_MV_SOURCE = (
    "def compute_pricing_mv(items, discount_bps):\n"
    "    subtotal = sum(int(x['unit_cents']) * int(x['quantity']) for x in items)\n"
    "    discount = (subtotal * int(discount_bps)) // 10000\n"
    "    net = subtotal - discount\n"
    "    return {\n"
    "        'subtotal_cents': subtotal,\n"
    "        'discount_cents': discount,\n"
    "        'net_cents': net,\n"
    "        'usd_anchor_cents': 0,\n"
    "    }\n"
)

CANONICAL_TAX_MV_SOURCE = (
    "def compute_tax_mv(quote, tax_bps):\n"
    "    net = int(quote['net_cents'])\n"
    "    tax = (net * int(tax_bps)) // 10000\n"
    "    gross = net + tax\n"
    "    return {\n"
    "        'net_cents': net,\n"
    "        'tax_cents': tax,\n"
    "        'gross_cents': gross,\n"
    "        'eur_clearing_delta_cents': tax,\n"
    "    }\n"
)

CANONICAL_SETTLEMENT_MV_SOURCE = (
    "def compute_settlement_mv(taxed_quote, fee_bps):\n"
    "    net = int(taxed_quote['net_cents'])\n"
    "    tax = int(taxed_quote['tax_cents'])\n"
    "    gross = int(taxed_quote['gross_cents'])\n"
    "    fee = (net * int(fee_bps)) // 10000\n"
    "    payout = gross - fee - tax\n"
    "    return {\n"
    "        'gross_cents': gross,\n"
    "        'platform_fee_cents': fee,\n"
    "        'tax_reserve_cents': tax,\n"
    "        'merchant_payout_cents': payout,\n"
    "        'clearing_offset_cents': tax,\n"
    "    }\n"
)


def run_mv_local_unit_tests(module_name: str, source_code: str) -> dict[str, Any]:
    """Run isolated subswarm unit tests on a single Mayer-Vietoris module."""
    func_map = {
        "pricing_mv": "compute_pricing_mv",
        "tax_mv": "compute_tax_mv",
        "settlement_mv": "compute_settlement_mv",
    }
    if module_name not in func_map:
        return {"passed": False, "error": f"Unknown Mayer-Vietoris module: {module_name}"}

    ast_info = StreamingCodebaseInterfaceMergeMonitor.inspect_module_ast(module_name, source_code)
    if not ast_info["syntax_ok"] or not ast_info["sandbox_ok"]:
        return {
            "passed": False,
            "module": module_name,
            "error": ast_info.get("error") or str(ast_info.get("sandbox_violations")),
        }

    try:
        env = StreamingCodebaseInterfaceMergeMonitor.execute_module_namespace(
            module_name, source_code
        )
    except Exception as exc:
        return {"passed": False, "error": f"SandboxCompileError: {exc}"}

    fn = env.get(func_map[module_name])
    if not callable(fn):
        return {"passed": False, "error": f"Missing function {func_map[module_name]} in {module_name}.py"}

    try:
        if module_name == "pricing_mv":
            res = fn([{"sku": "a", "unit_cents": 600, "quantity": 1}, {"sku": "b", "unit_cents": 400, "quantity": 1}], 1000)
            if not isinstance(res, dict):
                return {"passed": False, "error": "compute_pricing_mv must return a dict"}
            ok = (
                int(res.get("subtotal_cents", -1)) == 1000
                and int(res.get("discount_cents", -1)) == 100
                and int(res.get("net_cents", -1)) == 900
                and int(res.get("usd_anchor_cents", -1)) == 0
            )
            return {
                "passed": ok,
                "return_keys": sorted(res.keys()),
                "sample_output": res,
                "error": None if ok else "pricing_mv arithmetic or usd_anchor_cents mismatch",
            }

        if module_name == "tax_mv":
            res = fn({"subtotal_cents": 1000, "discount_cents": 100, "net_cents": 900, "usd_anchor_cents": 0}, 2000)
            if not isinstance(res, dict):
                return {"passed": False, "error": "compute_tax_mv must return a dict"}
            eur_delta = int(res.get("eur_clearing_delta_cents", -1))
            ok = (
                int(res.get("net_cents", -1)) == 900
                and int(res.get("tax_cents", -1)) == 180
                and int(res.get("gross_cents", -1)) == 1080
                and eur_delta in (150, 180, 210)
            )
            return {
                "passed": ok,
                "return_keys": sorted(res.keys()),
                "eur_clearing_delta_cents": eur_delta,
                "sample_output": res,
                "error": None if ok else f"tax_mv local check failed (eur_clearing_delta_cents={eur_delta})",
            }

        res = fn(
            {
                "net_cents": 900,
                "tax_cents": 180,
                "gross_cents": 1080,
                "eur_clearing_delta_cents": 180,
            },
            300,
        )
        if not isinstance(res, dict):
            return {"passed": False, "error": "compute_settlement_mv must return a dict"}
        clearing_offset = int(res.get("clearing_offset_cents", -1))
        ok = (
            int(res.get("gross_cents", -1)) == 1080
            and int(res.get("platform_fee_cents", -1)) == 27
            and int(res.get("tax_reserve_cents", -1)) == 180
            and int(res.get("merchant_payout_cents", -1)) == 873
            and clearing_offset in (150, 180, 210)
        )
        return {
            "passed": ok,
            "return_keys": sorted(res.keys()),
            "clearing_offset_cents": clearing_offset,
            "sample_output": res,
            "error": None if ok else f"settlement_mv local check failed (clearing_offset_cents={clearing_offset})",
        }
    except Exception as exc:
        return {"passed": False, "error": f"{type(exc).__name__}: {exc}"}


def mv_fixture(seed: int) -> dict[str, Any]:
    """Generate deterministic 3-agent Mayer-Vietoris codebase scenario for `seed`."""
    kind = [
        "disconnected_overlap_coboundary_jump",
        "infeasible_mayer_vietoris_clearing_lock",
        "clean_mayer_vietoris_control",
    ][seed % 3]

    src_t_fault = (
        "def compute_tax_mv(quote, tax_bps):\n"
        "    net = int(quote['net_cents'])\n"
        "    tax = (net * int(tax_bps)) // 10000\n"
        "    gross = net + tax\n"
        "    return {\n"
        "        'net_cents': net,\n"
        "        'tax_cents': tax,\n"
        "        'gross_cents': gross,\n"
        "        'eur_clearing_delta_cents': tax + 30,\n"
        "    }\n"
    )
    src_s_fault = (
        "def compute_settlement_mv(taxed_quote, fee_bps):\n"
        "    net = int(taxed_quote['net_cents'])\n"
        "    tax = int(taxed_quote['tax_cents'])\n"
        "    gross = int(taxed_quote['gross_cents'])\n"
        "    fee = (net * int(fee_bps)) // 10000\n"
        "    payout = gross - fee - tax\n"
        "    return {\n"
        "        'gross_cents': gross,\n"
        "        'platform_fee_cents': fee,\n"
        "        'tax_reserve_cents': tax,\n"
        "        'merchant_payout_cents': payout,\n"
        "        'clearing_offset_cents': tax - 30,\n"
        "    }\n"
    )

    if kind == "disconnected_overlap_coboundary_jump":
        sources = {
            "pricing_mv": CANONICAL_PRICING_MV_SOURCE,
            "tax_mv": src_t_fault,
            "settlement_mv": src_s_fault,
        }
        infeasible = None
        locked_workers: list[str] = []
    elif kind == "infeasible_mayer_vietoris_clearing_lock":
        sources = {
            "pricing_mv": CANONICAL_PRICING_MV_SOURCE,
            "tax_mv": src_t_fault,
            "settlement_mv": src_s_fault,
        }
        infeasible = {
            "type": "LOCKED_DISCONNECTED_OVERLAP_GAUGE_CONTRADICTION",
            "locked_module": "tax_mv",
            "locked_eur_clearing_delta_cents": 210,
            "locked_fu_w1_cents": 1110,
            "required_global_clearing_w1_cents": 1080,
            "reason": (
                "Subswarm U (`tax_mv.py`) is locked with `'eur_clearing_delta_cents': 210` (`f_U(w1) = 1110`), "
                "while global settlement conservation requires `f_U(w1) = f_V(w1) = gross_cents = 1080`."
            ),
        }
        locked_workers = ["worker-1"]
    else:
        sources = {
            "pricing_mv": CANONICAL_PRICING_MV_SOURCE,
            "tax_mv": CANONICAL_TAX_MV_SOURCE,
            "settlement_mv": CANONICAL_SETTLEMENT_MV_SOURCE,
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


class MayerVietorisCodeWorkspace:
    """Sandboxed 3-agent Mayer-Vietoris disconnected overlap codebase workspace."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = deepcopy(state)

    def local_verdicts(self) -> dict[str, bool]:
        return {
            mname: bool(run_mv_local_unit_tests(mname, src)["passed"])
            for mname, src in self.state["sources"].items()
        }

    def tool(self, worker: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if worker not in MV_WORKER_MODULES:
            return {"accepted": False, "error": f"unknown worker {worker}"}
        module_name = MV_WORKER_MODULES[worker]

        if name == "inspect_workspace" and arguments == {}:
            own_src = self.state["sources"][module_name]
            local_res = run_mv_local_unit_tests(module_name, own_src)
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
            return run_mv_local_unit_tests(module_name, own_src)

        if name == "escalate":
            reason = arguments.get("reason")
            if set(arguments) != {"reason"} or not isinstance(reason, str) or not reason.strip():
                return {"accepted": False, "error": "escalate requires a non-empty string 'reason'"}
            self.state["escalations"][worker] = reason.strip()[:1000]
            return {
                "escalated": True,
                "worker": worker,
                "reason": self.state["escalations"][worker],
            }

        if name == "submit_module_patch":
            if worker in self.state["locked_workers"]:
                return {"accepted": False, "error": "owned module is locked; escalate if contract is infeasible"}
            new_src = arguments.get("source_code")
            if set(arguments) != {"source_code"} or not isinstance(new_src, str) or not new_src.strip():
                return {"accepted": False, "error": "submit_module_patch requires non-empty 'source_code'"}
            local_res = run_mv_local_unit_tests(module_name, new_src)
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
                "scope": "isolated subswarm unit tests passed; Mayer-Vietoris disconnected overlap gluing is checked at merge gate",
            }

        return {"accepted": False, "error": f"unsupported tool {name} or malformed arguments"}






