//! Re-derive the verdict of every file in `examples/`, the cookbook instances and the
//! recorded receipts, using only the Rust kernels. Test names are cited in the DAG.

use lggr_derivations::{canon, chain, descent, history, linear, q, streaming, transport};
use serde_json::{json, Value};
use std::path::PathBuf;

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn load(rel: &str) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root().join(rel)).unwrap()).unwrap()
}

fn mat(v: &Value) -> linear::Matrix {
    linear::matrix_from_json(v).unwrap()
}

fn vecq(v: &Value) -> linear::Vector {
    linear::vector_from_json(v).unwrap()
}

// LGGR-C12: the five history examples separate into five distinct audit outcomes.
#[test]
fn c12_history_examples_audit_outcomes() {
    let expect = [
        ("good_history", "COMPOSITION_VERIFIED", None),
        ("bad_history", "OBSTRUCTION_DETECTED", Some("PROTECTED_QUERY_FALSE")),
        ("reports_only", "WITNESS_INCOMPLETE", Some("MISSING_ENDPOINT")),
        ("open_obligation", "WITNESS_INCOMPLETE", Some("OPEN_OBLIGATIONS")),
        ("authority_changed", "AUTHORITY_REQUIRED", Some("SEMANTIC_SCOPE_CHANGED")),
    ];
    for (name, status, code) in expect {
        let a = history::audit(&load(&format!("examples/{name}.json")));
        assert_eq!(a.status, status, "{name}");
        if let Some(c) = code {
            assert!(a.findings.iter().any(|f| f.code == c), "{name}: {c}");
        }
    }
    let bad = history::audit(&load("examples/bad_history.json"));
    assert_eq!((bad.signed_total, bad.endpoint_verdict), (Some(2), Some(false)));
}

// LGGR-C13: the recorded policy digest in every history example replays from canonical JSON.
#[test]
fn c13_policy_digest_replays() {
    for name in ["good_history", "bad_history", "reports_only", "open_obligation", "authority_changed"] {
        let doc = load(&format!("examples/{name}.json"));
        let d = canon::digest(&doc["policy"]);
        for w in doc["witnesses"].as_array().unwrap() {
            assert_eq!(w["policy_sha256"].as_str().unwrap(), d, "{name}");
        }
    }
}

// LGGR-C09 (example form): report_collision collides; refined_reports decodes.
#[test]
fn c09_report_examples_collision_and_refinement() {
    let rc = descent::rows_from_json(&load("examples/report_collision.json")).unwrap();
    assert!(matches!(descent::analyze(&rc), descent::Descent::Collision(_, _)));
    let rr = descent::rows_from_json(&load("examples/refined_reports.json")).unwrap();
    match descent::analyze(&rr) {
        descent::Descent::Decoder(d) => assert!(descent::decoder_valid(&rr, &d)),
        _ => panic!("refined reports should decode"),
    }
}

// LGGR-C15: triangle l1 instance: dual (1,1,-1) and potential (0,1,2) certify optimum 1; repair impossible.
#[test]
fn c15_triangle_l1_optimality_example() {
    let d = load("examples/triangle_l1.json");
    let c = linear::verify_l1(&mat(&d["D"]), &vecq(&d["h"]), &vecq(&d["weights"]), &vecq(&d["potential"]), &vecq(&d["dual"])).unwrap();
    assert_eq!(c.status, linear::L1Status::OptimalityVerified);
    assert_eq!(c.upper, q(1));
    assert!(c.repair_impossible);
}

// LGGR-C16: filled triangle: D1 D0 = 0, (1,1,1) fails closure, (1,1,2) is exact.
#[test]
fn c16_filled_triangle_closure_vs_exactness_examples() {
    let f = load("examples/triangle_filled.json");
    let (st, _) = linear::classify_cochain(&mat(&f["D0"]), &vecq(&f["h"]), &mat(&f["D1"]));
    assert_eq!(st, linear::CochainStatus::ClosureFailure);
    assert!(linear::is_zero(&linear::matmul(&mat(&f["D1"]), &mat(&f["D0"]))));
    let e = load("examples/budget_exact_cochain.json");
    let (st, pot) = linear::classify_cochain(&mat(&e["D0"]), &vecq(&e["h"]), &mat(&e["D1"]));
    assert_eq!(st, linear::CochainStatus::Exact);
    assert_eq!(linear::matvec(&mat(&e["D0"]), &pot.unwrap()), vecq(&e["h"]));
}

// LGGR-C17 (example form): unfilled triangle: (1,1,1) is closed and nonexact, a nonzero H^1 class.
#[test]
fn c17_unfilled_triangle_nonzero_h1_example() {
    let u = load("examples/triangle_unfilled.json");
    let (st, pot) = linear::classify_cochain(&mat(&u["D0"]), &vecq(&u["h"]), &mat(&u["D1"]));
    assert_eq!(st, linear::CochainStatus::ClosedNonexact);
    assert!(pot.is_none());
}

// LGGR-C19: faithful transport verifies a retraction; lossy transport commutes but admits no left inverse.
#[test]
fn c19_transport_examples() {
    let f = load("examples/faithful_transport.json");
    let st = transport::verify_transport(&mat(&f["D_source"]), &mat(&f["D_target"]), &mat(&f["F0"]), &mat(&f["F1"]), Some((&mat(&f["G0"]), &mat(&f["G1"]))));
    assert_eq!(st, transport::TransportStatus::RetractionVerified);
    let l = load("examples/lossy_transport.json");
    let st = transport::verify_transport(&mat(&l["D_source"]), &mat(&l["D_target"]), &mat(&l["F0"]), &mat(&l["F1"]), None);
    assert_eq!(st, transport::TransportStatus::CommutingTransportVerified);
    assert!(!transport::zero_map_admits_left_inverse(&mat(&l["F1"])));
}

// LGGR-C35: every recorded example receipt's status is re-derived by the Rust kernels.
#[test]
fn c35_receipts_rederived() {
    let map = |s: &str| match s {
        "Exact" => "EXACT",
        "ClosureFailure" => "CLOSURE_FAILURE",
        "ClosedNonexact" => "CLOSED_NONEXACT",
        other => other,
    }
    .to_string();
    for name in ["good_history", "bad_history", "reports_only", "report_collision", "refined_reports", "triangle_filled", "triangle_unfilled", "budget_exact_cochain", "triangle_l1", "faithful_transport", "lossy_transport"] {
        let rec = load(&format!("receipts/{name}.json"));
        let doc = load(&format!("examples/{name}.json"));
        let got = if doc.get("rows").is_some() {
            match descent::analyze(&descent::rows_from_json(&doc).unwrap()) {
                descent::Descent::Decoder(_) => "DECODER_VERIFIED".to_string(),
                descent::Descent::Collision(_, _) => "REPORT_INSUFFICIENT".to_string(),
            }
        } else if doc.get("policy").is_some() {
            history::audit(&doc).status.to_string()
        } else if doc.get("D0").is_some() {
            map(&format!("{:?}", linear::classify_cochain(&mat(&doc["D0"]), &vecq(&doc["h"]), &mat(&doc["D1"])).0))
        } else if doc.get("dual").is_some() {
            let c = linear::verify_l1(&mat(&doc["D"]), &vecq(&doc["h"]), &vecq(&doc["weights"]), &vecq(&doc["potential"]), &vecq(&doc["dual"])).unwrap();
            if c.status == linear::L1Status::OptimalityVerified { "OPTIMALITY_VERIFIED".into() } else { format!("{:?}", c.status) }
        } else {
            let g = match (doc.get("G0"), doc.get("G1")) {
                (Some(a), Some(b)) => Some((mat(a), mat(b))),
                _ => None,
            };
            let st = transport::verify_transport(&mat(&doc["D_source"]), &mat(&doc["D_target"]), &mat(&doc["F0"]), &mat(&doc["F1"]), g.as_ref().map(|(a, b)| (a, b)));
            match st {
                transport::TransportStatus::RetractionVerified => "RETRACTION_VERIFIED".into(),
                transport::TransportStatus::CommutingTransportVerified => "COMMUTING_TRANSPORT_VERIFIED".into(),
                other => format!("{other:?}"),
            }
        };
        let recorded = rec["status"].as_str().map(String::from).unwrap_or_else(|| rec["result"]["status"].as_str().unwrap_or("?").to_string());
        assert_eq!(got, recorded, "{name}");
    }
}

// Cookbook 01 (LGGR-C11 instance): same boundary report, divergent downstream requirements -> collision.
#[test]
fn cookbook01_online_fiber_collision() {
    let mut m = streaming::FiberMonitor::default();
    let r = json!({"workload_type": "distributed_etl", "target_environment": "production", "data_classification": "confidential"});
    m.observe("task_batch_001", &r, &json!({"requires_isolated_vpc": true, "encryption_at_rest": "customer_managed_kms", "approval_tier": "Tier-3"}));
    assert!(m.observe("task_batch_002", &r, &json!({"requires_isolated_vpc": false, "encryption_at_rest": "default_cloud_kms", "approval_tier": "Tier-1"})));
}

// Cookbook 02 (LGGR-C10 instance): history 0,1,3,1 under every_prefix bound 2 alerts at step 2.
#[test]
fn cookbook02_prefix_excursion_alert() {
    let h = [0, 1, 3, 1];
    assert!(history::local_steps_ok(&h, 2));
    assert_eq!(history::first_prefix_violation(&h, 2), Some(2));
    assert!(history::endpoint_ok(&h, 2));
}

// Cookbook 04 (LGGR-C29 instance): enriched reports keep fibers constant; 0,1,2,3 stays within bound 3; Delta_E = 0.
#[test]
fn cookbook04_boundary_sufficient_lggg() {
    let h = [0, 1, 2, 3];
    assert!(history::local_steps_ok(&h, 1) && history::every_prefix_ok(&h, 3));
    assert_eq!(descent::evaluator_defect(true, true, true), 0);
}

// LGGR-C36: the recorded workflow event logs form intact hash chains, and a one-field edit breaks the chain.
#[test]
fn c36_workflow_event_chains_verify() {
    for rel in [
        "workflows/live_five_agent_swarm/evidence/evaluation/events.jsonl",
        "workflows/live_five_agent_swarm/evidence/development/events.jsonl",
        "workflows/concurrent_five_agent_swarm/evidence/development/events.jsonl",
    ] {
        let text = std::fs::read_to_string(root().join(rel)).unwrap();
        let mut records = chain::parse_jsonl(&text).unwrap();
        assert!(records.len() > 1, "{rel}");
        assert_eq!(chain::first_break(&records), None, "{rel}");
        let k = records.len() / 2;
        records[k]["kind"] = json!("tampered");
        assert_eq!(chain::first_break(&records), Some(k), "{rel}");
    }
}
