//! Lean axiom census against the derivation DAG.
//!
//! `lean_census emit`  prints a Lean file that runs `#print axioms` on every theorem the DAG
//!                     cites from LggrVII, LggrVIII and WorldLGGRWitness.
//! `lean_census check` reads Lean's output on stdin and fails unless every cited theorem was
//!                     reported, no axiom outside {propext, Quot.sound, Classical.choice} appears
//!                     (in particular no sorryAx), and the set of theorems using Classical.choice
//!                     equals `lean_inventory[*].uses_classical_choice` in the DAG.
//!
//! `lean_census emit-types`   prints a Lean file that runs `#check @T` on the same theorems.
//! `lean_census check-types`  reads that output on stdin and fails unless every cited theorem's
//!                            statement equals the one pinned in `dag/derivations/lean_signatures.json`.
//!                            A changed statement must be re-reviewed against its ledger claim
//!                            before the pin is updated (`check-types --record` rewrites it).
//!
//! Run from the repository root:
//!   cargo run -q --manifest-path code/rust/Cargo.toml --bin lean_census -- emit > lean4/Census.lean
//!   (cd lean4 && lake env lean Census.lean) | cargo run -q --manifest-path code/rust/Cargo.toml --bin lean_census -- check

use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;

const MODULES: [&str; 3] = ["LggrVII", "LggrVIII", "WorldLGGRWitness"];
const ALLOWED: [&str; 3] = ["propext", "Quot.sound", "Classical.choice"];

fn root() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

const SIGS: &str = "dag/derivations/lean_signatures.json";

/// Parse `#check @T` output. Each statement starts at column 0 with `T : ` (or `@T : `) for a
/// cited name `T`; every other line continues the current statement and is joined with a space.
fn parse_types(text: &str, names: &BTreeSet<String>) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    let mut cur: Option<(String, String)> = None;
    for line in text.lines() {
        let start = line.strip_prefix('@').unwrap_or(line).split_once(" : ");
        if let Some((name, ty)) = start.filter(|(n, _)| names.contains(*n)) {
            if let Some((n, t)) = cur.take() {
                out.insert(n, t);
            }
            cur = Some((name.to_string(), ty.trim().to_string()));
        } else if let Some((_, t)) = cur.as_mut() {
            let l = line.trim();
            if !l.is_empty() {
                t.push(' ');
                t.push_str(l);
            }
        }
    }
    if let Some((n, t)) = cur {
        out.insert(n, t);
    }
    out
}

fn dag() -> Value {
    serde_json::from_str(&std::fs::read_to_string(root().join("dag/derivations/derivation_dag.json")).unwrap()).unwrap()
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
        Some("emit-types") => {
            for m in MODULES {
                println!("import {m}");
            }
            for n in &names {
                println!("#check @{n}");
            }
        }
        Some("check-types") => {
            let mut text = String::new();
            std::io::stdin().read_to_string(&mut text).unwrap();
            let got = parse_types(&text, &names);
            let path = root().join(SIGS);
            if std::env::args().nth(2).as_deref() == Some("--record") {
                let pinned: BTreeMap<&String, &String> = got.iter().filter(|(k, _)| names.contains(*k)).collect();
                std::fs::write(&path, serde_json::to_string_pretty(&pinned).unwrap() + "\n").unwrap();
                println!("recorded {} signatures", pinned.len());
                return;
            }
            let pinned: BTreeMap<String, String> = serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
            let mut errors = Vec::new();
            for n in &names {
                match (got.get(n), pinned.get(n)) {
                    (None, _) => errors.push(format!("no #check output for {n}")),
                    (Some(_), None) => errors.push(format!("{n} has no pinned signature")),
                    (Some(a), Some(b)) if a != b => errors.push(format!("{n} statement changed:\n  pinned: {b}\n  now:    {a}")),
                    _ => {}
                }
            }
            println!("lean types: {} theorems checked, {} errors", names.len(), errors.len());
            if !errors.is_empty() {
                for e in &errors {
                    eprintln!("{e}");
                }
                std::process::exit(1);
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
            eprintln!("usage: lean_census emit|check|emit-types|check-types [--record]");
            std::process::exit(2);
        }
    }
}
