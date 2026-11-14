//! Integrity of `dag/derivations/derivation_dag.json` and its agreement with the ledger,
//! the Lean sources and the Rust tests.

use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn dag() -> Value {
    serde_json::from_str(&std::fs::read_to_string(root().join("dag/derivations/derivation_dag.json")).unwrap()).unwrap()
}

fn nodes(d: &Value) -> &Vec<Value> {
    d["nodes"].as_array().unwrap()
}

#[test]
fn dag_ids_unique_and_edges_resolve() {
    let d = dag();
    let ids: Vec<&str> = nodes(&d).iter().map(|n| n["id"].as_str().unwrap()).collect();
    let set: BTreeSet<&str> = ids.iter().copied().collect();
    assert_eq!(ids.len(), set.len(), "duplicate node id");
    for e in d["edges"].as_array().unwrap() {
        assert!(set.contains(e["from"].as_str().unwrap()), "{e}");
        assert!(set.contains(e["to"].as_str().unwrap()), "{e}");
    }
    for n in nodes(&d) {
        for dep in n["depends_on"].as_array().unwrap() {
            assert!(set.contains(dep.as_str().unwrap()), "{} -> {dep}", n["id"]);
        }
    }
}

#[test]
fn dag_is_acyclic() {
    let d = dag();
    let mut indeg: BTreeMap<String, usize> = nodes(&d).iter().map(|n| (n["id"].as_str().unwrap().to_string(), 0)).collect();
    let mut out: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for e in d["edges"].as_array().unwrap() {
        let (f, t) = (e["from"].as_str().unwrap().to_string(), e["to"].as_str().unwrap().to_string());
        *indeg.get_mut(&t).unwrap() += 1;
        out.entry(f).or_default().push(t);
    }
    let mut ready: Vec<String> = indeg.iter().filter(|(_, v)| **v == 0).map(|(k, _)| k.clone()).collect();
    let mut seen = 0;
    while let Some(n) = ready.pop() {
        seen += 1;
        for t in out.get(&n).cloned().unwrap_or_default() {
            let v = indeg.get_mut(&t).unwrap();
            *v -= 1;
            if *v == 0 {
                ready.push(t);
            }
        }
    }
    assert_eq!(seen, indeg.len(), "cycle in derivation DAG");
}

#[test]
fn dag_statuses_are_backed_by_evidence() {
    let d = dag();
    let allowed: BTreeSet<&str> = d["statuses"].as_object().unwrap().keys().map(|k| k.as_str()).collect();
    let mut counts: BTreeMap<String, u64> = BTreeMap::new();
    for n in nodes(&d) {
        let s = n["status"].as_str().unwrap();
        assert!(allowed.contains(s), "{}: {s}", n["id"]);
        *counts.entry(s.to_string()).or_default() += 1;
        let lean = n["lean_theorems"].as_array().unwrap().len();
        let rust = n["rust_tests"].as_array().unwrap().len();
        match s {
            "PROVED_LEAN" => assert!(lean > 0, "{} PROVED_LEAN without a Lean theorem", n["id"]),
            "TESTED_RUST" => assert!(rust > 0, "{} TESTED_RUST without a Rust test", n["id"]),
            "OPEN" | "PROSE_ONLY" => assert!(rust == 0 && lean == 0, "{} cites evidence but is {s}", n["id"]),
            _ => {}
        }
    }
    let recorded: BTreeMap<String, u64> = d["counts"].as_object().unwrap().iter().map(|(k, v)| (k.clone(), v.as_u64().unwrap())).collect();
    assert_eq!(recorded, counts);
}

#[test]
fn dag_lean_theorems_exist_in_sources() {
    let d = dag();
    let mut src = BTreeMap::new();
    for m in ["LggrVII", "LggrVIII", "WorldLGGRWitness", "PrimitiveDifference"] {
        src.insert(m, std::fs::read_to_string(root().join(format!("lean4/{m}.lean"))).unwrap().replace('\r', ""));
    }
    let all: String = src.values().cloned().collect::<Vec<_>>().join("\n");
    for n in nodes(&d) {
        for t in n["lean_theorems"].as_array().unwrap() {
            let short = t.as_str().unwrap().rsplit('.').next().unwrap();
            let found = all.lines().any(|l| {
                let l = l.trim_start();
                (l.starts_with("theorem ") || l.starts_with("lemma ")) && l.split_whitespace().nth(1) == Some(short)
            });
            assert!(found, "{}: Lean theorem {short} not found", n["id"]);
        }
    }
    for m in ["LggrVII", "LggrVIII", "WorldLGGRWitness", "PrimitiveDifference"] {
        assert!(!src[m].contains("sorry"), "{m} contains sorry");
    }
}

#[test]
fn dag_rust_tests_exist() {
    let d = dag();
    let dir = root().join("code/rust/tests");
    let all: String = std::fs::read_dir(&dir).unwrap().filter_map(|e| e.ok()).map(|e| std::fs::read_to_string(e.path()).unwrap()).collect();
    for n in nodes(&d) {
        for t in n["rust_tests"].as_array().unwrap() {
            let name = t.as_str().unwrap();
            assert!(all.contains(&format!("fn {name}()")), "{}: Rust test {name} not found", n["id"]);
        }
    }
}

#[test]
fn ledger_lists_every_node_with_its_status() {
    let d = dag();
    let ledger = std::fs::read_to_string(root().join("atlas/atlas_claim_ledger.md")).unwrap();
    for n in nodes(&d) {
        let id = n["id"].as_str().unwrap();
        let row = ledger.lines().find(|l| l.starts_with(&format!("| {id} |")));
        let row = row.unwrap_or_else(|| panic!("{id} missing from ledger"));
        if !id.starts_with("LGGR-L-") {
            assert!(row.contains(&format!("`{}`", n["status"].as_str().unwrap())), "{id}: ledger status differs");
        }
    }
}

/// Every cited LggrVII/LggrVIII/World theorem has a pinned statement; CI compares the pins with
/// `#check` output, so a changed statement fails until it is re-reviewed against its claim.
#[test]
fn dag_cited_theorems_have_pinned_statements() {
    let d = dag();
    let sigs: Value = serde_json::from_str(&std::fs::read_to_string(root().join("dag/derivations/lean_signatures.json")).unwrap()).unwrap();
    let sigs = sigs.as_object().unwrap();
    for n in nodes(&d) {
        for t in n["lean_theorems"].as_array().unwrap() {
            let t = t.as_str().unwrap();
            if t.starts_with("LggrVII.") || t.starts_with("LggrVIII.") || t.starts_with("OmegaWorld.") {
                let ty = sigs.get(t).and_then(|v| v.as_str()).unwrap_or_else(|| panic!("{t} has no pinned statement"));
                assert!(!ty.is_empty() && !ty.contains("sorry"), "{t}: bad pinned statement");
            }
        }
    }
}
