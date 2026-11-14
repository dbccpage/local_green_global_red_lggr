//! Lean axiom census against the derivation DAG.
//!
//! `lean_census emit`  prints a Lean file that runs `#print axioms` on every theorem the DAG
//!                     cites from LggrVII, LggrVIII and WorldLGGRWitness.
//! `lean_census check` reads Lean's output on stdin and fails unless every cited theorem was
//!                     reported, no axiom outside {propext, Quot.sound, Classical.choice} appears
//!                     (in particular no sorryAx), and the set of theorems using Classical.choice
//!                     equals `lean_inventory[*].uses_classical_choice` in the DAG.
//!
//! Run from the repository root:
//!   cargo run -q --manifest-path code/rust/Cargo.toml --bin lean_census -- emit > lean4/Census.lean
//!   (cd lean4 && lake env lean Census.lean) | cargo run -q --manifest-path code/rust/Cargo.toml --bin lean_census -- check

use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;

const MODULES: [&str; 3] = ["LggrVII", "LggrVIII", "WorldLGGRWitness"];
const ALLOWED: [&str; 3] = ["propext", "Quot.sound", "Classical.choice"];

fn dag() -> Value {
    let root = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    serde_json::from_str(&std::fs::read_to_string(root.join("dag/derivations/derivation_dag.json")).unwrap()).unwrap()
}

fn cited(d: &Value) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    for n in d["nodes"].as_array().unwrap() {
        for t in n["lean_theorems"].as_array().unwrap() {
            let t = t.as_str().unwrap();
            if t.starts_with("LggrVII.") || t.starts_with("LggrVIII.") || t.starts_with("OmegaWorld.") {
                out.insert(t.to_string());
            }
        }
    }
    out
}

/// Parse `#print axioms` output into theorem -> axioms.
fn parse(text: &str) -> BTreeMap<String, BTreeSet<String>> {
    let mut out = BTreeMap::new();
    let mut rest = text;
    while let Some(i) = rest.find('\'') {
        let after = &rest[i + 1..];
        let Some(j) = after.find('\'') else { break };
        let name = after[..j].to_string();
        let tail = &after[j + 1..];
        let t = tail.trim_start();
        if t.starts_with("does not depend on any axioms") {
            out.insert(name, BTreeSet::new());
            rest = tail;
        } else if t.starts_with("depends on axioms:") {
            let open = tail.find('[').unwrap();
            let close = tail.find(']').unwrap();
            let ax = tail[open + 1..close].split(',').map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
            out.insert(name, ax);
            rest = &tail[close + 1..];
        } else {
            rest = tail;
        }
    }
    out
}

fn main() {
    let d = dag();
    let names = cited(&d);
    match std::env::args().nth(1).as_deref() {
        Some("emit") => {
            for m in MODULES {
                println!("import {m}");
            }
            for n in &names {
                println!("#print axioms {n}");
            }
        }
        Some("check") => {
            let mut text = String::new();
            std::io::stdin().read_to_string(&mut text).unwrap();
            let got = parse(&text);
            let mut errors = Vec::new();
            for n in &names {
                match got.get(n) {
                    None => errors.push(format!("no axiom report for {n}")),
                    Some(ax) => {
                        for a in ax {
                            if !ALLOWED.contains(&a.as_str()) {
                                errors.push(format!("{n} depends on disallowed axiom {a}"));
                            }
                        }
                    }
                }
            }
            let classical: BTreeSet<String> = got.iter().filter(|(k, v)| names.contains(*k) && v.contains("Classical.choice")).map(|(k, _)| k.clone()).collect();
            let recorded: BTreeSet<String> = d["lean_inventory"]
                .as_array()
                .unwrap()
                .iter()
                .flat_map(|m| m["uses_classical_choice"].as_array().unwrap().iter().map(|v| v.as_str().unwrap().to_string()))
                .filter(|t| names.contains(t))
                .collect();
            for t in classical.difference(&recorded) {
                errors.push(format!("{t} now uses Classical.choice but the DAG does not record it"));
            }
            for t in recorded.difference(&classical) {
                errors.push(format!("{t} is recorded as using Classical.choice but no longer does"));
            }
            println!("lean census: {} theorems reported, {} use Classical.choice, {} errors", got.len(), classical.len(), errors.len());
            if !errors.is_empty() {
                for e in &errors {
                    eprintln!("{e}");
                }
                std::process::exit(1);
            }
        }
        _ => {
            eprintln!("usage: lean_census emit|check");
            std::process::exit(2);
        }
    }
}
