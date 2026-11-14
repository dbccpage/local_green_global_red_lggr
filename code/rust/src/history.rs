//! Cumulative-budget witness composition: telescoping, endpoint vs every-prefix
//! admissibility, and the audit of a supplied witness trace.
//!
//! The audit replays the finite budget model of the example histories. Findings are
//! separate; the primary status is the first kind present in a fixed priority list.

use crate::canon::digest;
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

/// Sum of signed increments equals endpoint minus baseline (telescoping).
pub fn telescope(xs: &[i64]) -> (i64, i64) {
    let sum: i64 = xs.windows(2).map(|w| w[1] - w[0]).sum();
    (sum, xs.last().copied().unwrap_or(0) - xs.first().copied().unwrap_or(0))
}

/// Every step satisfies |x_i - x_{i-1}| <= step_bound.
pub fn local_steps_ok(xs: &[i64], step_bound: i64) -> bool {
    xs.windows(2).all(|w| (w[1] - w[0]).abs() <= step_bound)
}

pub fn endpoint_ok(xs: &[i64], total_bound: i64) -> bool {
    match (xs.first(), xs.last()) {
        (Some(a), Some(b)) => (b - a).abs() <= total_bound,
        _ => true,
    }
}

pub fn every_prefix_ok(xs: &[i64], total_bound: i64) -> bool {
    xs.iter().all(|x| (x - xs[0]).abs() <= total_bound)
}

/// Index of the first prefix whose cumulative drift exceeds the bound.
pub fn first_prefix_violation(xs: &[i64], total_bound: i64) -> Option<usize> {
    xs.iter().position(|x| (x - xs[0]).abs() > total_bound)
}

/// Unsigned step-magnitude report (|dx_1|, ..., |dx_n|).
pub fn unsigned_report(xs: &[i64]) -> Vec<i64> {
    xs.windows(2).map(|w| (w[1] - w[0]).abs()).collect()
}

/// Signed step report (dx_1, ..., dx_n).
pub fn signed_report(xs: &[i64]) -> Vec<i64> {
    xs.windows(2).map(|w| w[1] - w[0]).collect()
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Finding {
    pub kind: &'static str,
    pub code: &'static str,
}

#[derive(Debug, Clone)]
pub struct Audit {
    pub status: &'static str,
    pub findings: Vec<Finding>,
    pub policy_sha256: String,
    pub signed_total: Option<i64>,
    pub endpoint_verdict: Option<bool>,
    pub every_prefix_verdict: Option<bool>,
    pub obligations: BTreeSet<String>,
}

const PRIORITY: [&str; 6] = [
    "INVALID_WITNESS",
    "AUTHORITY_REQUIRED",
    "UNSUPPORTED",
    "LOCAL_REJECTED",
    "OBSTRUCTION_DETECTED",
    "WITNESS_INCOMPLETE",
];

fn int(v: &Value) -> Option<i64> {
    v.as_i64()
}

fn local_accepts(policy: &Value, a: i64, b: i64) -> bool {
    let allowed: Vec<i64> = policy["allowed_states"].as_array().unwrap().iter().filter_map(int).collect();
    allowed.contains(&a) && allowed.contains(&b) && (b - a).abs() <= policy["max_step"].as_i64().unwrap()
}

/// Audit a document `{policy, baseline, witnesses, prior_obligations?}`.
pub fn audit(doc: &Value) -> Audit {
    let policy = &doc["policy"];
    let policy_sha = digest(policy);
    let allowed: Vec<i64> = policy["allowed_states"].as_array().unwrap().iter().filter_map(int).collect();
    let max_total = policy["max_total"].as_i64().unwrap();
    let scope = policy["query_scope"].as_str().unwrap();
    let baseline = &doc["baseline"];
    let steps = doc["witnesses"].as_array().cloned().unwrap_or_default();
    let mut findings = Vec::new();
    let mut add = |k: &'static str, c: &'static str| findings.push(Finding { kind: k, code: c });
    let mut obligations: BTreeSet<String> = doc["prior_obligations"]
        .as_array()
        .map(|a| a.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_default();

    let mut values: BTreeMap<String, i64> = BTreeMap::new();
    let mut structural = true;
    let mut states = vec![baseline.clone()];
    for w in &steps {
        states.push(w["source"].clone());
        states.push(w["target"].clone());
    }
    for s in &states {
        if let Some(v) = int(&s["value"]) {
            let id = s["state_id"].as_str().unwrap().to_string();
            if let Some(prev) = values.get(&id) {
                if *prev != v {
                    structural = false;
                    add("INVALID_WITNESS", "CONFLICTING_STATE");
                }
            }
            values.insert(id, v);
        }
    }

    let mut ids = BTreeSet::new();
    let mut expected = baseline["state_id"].as_str().unwrap().to_string();
    let mut same_rep = true;
    let mut deltas: Vec<Option<i64>> = Vec::new();
    for w in &steps {
        if let Some(obs) = w["obligations"].as_array() {
            obligations.extend(obs.iter().filter_map(|v| v.as_str().map(String::from)));
        }
        if !ids.insert(w["witness_id"].as_str().unwrap().to_string()) {
            structural = false;
            add("INVALID_WITNESS", "DUPLICATE_WITNESS");
        }
        let src = w["source"]["state_id"].as_str().unwrap();
        if src != expected {
            structural = false;
            add("INVALID_WITNESS", "BOUNDARY_MISMATCH");
        }
        expected = w["target"]["state_id"].as_str().unwrap().to_string();
        if w["policy_sha256"].as_str() != Some(policy_sha.as_str()) {
            add("AUTHORITY_REQUIRED", "POLICY_MANIFEST_CHANGED");
        }
        for f in ["evaluator_id", "spec_id", "authority_id"] {
            if w[f] != policy[f] {
                add("AUTHORITY_REQUIRED", "SEMANTIC_SCOPE_CHANGED");
            }
        }
        let rep_ok = w["representation_id"] == policy["representation_id"];
        if !rep_ok {
            same_rep = false;
            add("UNSUPPORTED", "REPRESENTATION_TRANSPORT_REQUIRED");
        }
        let a = values.get(src).copied();
        let b = values.get(w["target"]["state_id"].as_str().unwrap()).copied();
        match (a, b) {
            (Some(a), Some(b)) if rep_ok => {
                let accepted = local_accepts(policy, a, b);
                let smoke = allowed.contains(&b);
                if let Some(m) = int(&w["observed_magnitude"]) {
                    if m != (b - a).abs() {
                        add("INVALID_WITNESS", "MAGNITUDE_MISMATCH");
                    }
                }
                let same_meaning = w["evaluator_id"] == policy["evaluator_id"]
                    && w["spec_id"] == policy["spec_id"]
                    && w["policy_sha256"].as_str() == Some(policy_sha.as_str());
                if same_meaning
                    && (w["local_accepted"].as_bool() != Some(accepted) || w["smoke_passed"].as_bool() != Some(smoke))
                {
                    add("INVALID_WITNESS", "VERDICT_MISMATCH");
                }
                if !accepted || !smoke {
                    add("LOCAL_REJECTED", "LOCAL_RULE_FAILED");
                }
                deltas.push(Some(b - a));
            }
            (Some(_), Some(_)) => deltas.push(None),
            _ => {
                add("WITNESS_INCOMPLETE", "MISSING_ENDPOINT");
                deltas.push(None);
            }
        }
    }
    let base = int(&baseline["value"]);
    match base {
        None => add("WITNESS_INCOMPLETE", "BASELINE_UNOBSERVED"),
        Some(b) if !allowed.contains(&b) => {
            structural = false;
            add("INVALID_WITNESS", "BASELINE_OUTSIDE_DOMAIN");
        }
        _ => {}
    }
    let (mut total, mut endpoint_v, mut prefix_v) = (None, None, None);
    if structural && same_rep && base.is_some() && deltas.iter().all(|d| d.is_some()) {
        let ds: Vec<i64> = deltas.iter().map(|d| d.unwrap()).collect();
        let t: i64 = ds.iter().sum();
        let mut partial = 0;
        let mut prefixes_ok = true;
        for d in &ds {
            partial += d;
            prefixes_ok &= partial.abs() <= max_total;
        }
        let e_ok = t.abs() <= max_total;
        let global = if scope == "endpoint" { e_ok } else { prefixes_ok };
        if !global {
            add("OBSTRUCTION_DETECTED", "PROTECTED_QUERY_FALSE");
        }
        total = Some(t);
        endpoint_v = Some(e_ok);
        prefix_v = Some(prefixes_ok);
    }
    if !obligations.is_empty() {
        add("WITNESS_INCOMPLETE", "OPEN_OBLIGATIONS");
    }
    let status = PRIORITY
        .iter()
        .find(|k| findings.iter().any(|f| f.kind == **k))
        .copied()
        .unwrap_or("COMPOSITION_VERIFIED");
    Audit {
        status,
        findings,
        policy_sha256: policy_sha,
        signed_total: total,
        endpoint_verdict: endpoint_v,
        every_prefix_verdict: prefix_v,
        obligations,
    }
}

/// Summary JSON for the derivation binary.
pub fn audit_json(a: &Audit) -> Value {
    json!({
        "status": a.status,
        "findings": a.findings.iter().map(|f| json!({"kind": f.kind, "code": f.code})).collect::<Vec<_>>(),
        "policy_sha256": a.policy_sha256,
        "signed_total": a.signed_total,
        "endpoint_verdict": a.endpoint_verdict,
        "every_prefix_verdict": a.every_prefix_verdict,
        "unresolved_obligations": a.obligations.iter().collect::<Vec<_>>(),
    })
}
