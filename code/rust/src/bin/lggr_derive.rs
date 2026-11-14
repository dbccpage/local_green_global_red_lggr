//! Re-derive the verdict for every file in `examples/` with the Rust kernels only.
//!
//! Usage: `cargo run --release --bin lggr_derive -- [EXAMPLES_DIR]` (default `../../examples`).
//! Prints one JSON object keyed by example name. AuthorityEffect: None.

use lggr_derivations::{descent, history, linear, transport};
use serde_json::{json, Value};
use std::path::PathBuf;

fn mat(v: &Value) -> linear::Matrix {
    linear::matrix_from_json(v).expect("matrix")
}

pub fn derive(name: &str, doc: &Value) -> Value {
    if doc.get("rows").is_some() {
        let rows = descent::rows_from_json(doc).expect("rows");
        return match descent::analyze(&rows) {
            descent::Descent::Decoder(d) => json!({"kind": "descent", "status": "DECODER_VERIFIED", "fibers": d.len()}),
            descent::Descent::Collision(a, b) => json!({"kind": "descent", "status": "REPORT_INSUFFICIENT", "collision": [a, b]}),
        };
    }
    if doc.get("policy").is_some() {
        let a = history::audit(doc);
        return json!({"kind": "audit", "result": history::audit_json(&a)});
    }
    if doc.get("D0").is_some() {
        let h = linear::vector_from_json(&doc["h"]).unwrap();
        let (st, pot) = linear::classify_cochain(&mat(&doc["D0"]), &h, &mat(&doc["D1"]));
        return json!({"kind": "cochain", "status": format!("{st:?}"),
                      "potential": pot.map(|p| p.iter().map(|x| x.to_string()).collect::<Vec<_>>())});
    }
    if doc.get("dual").is_some() {
        let v = |k: &str| linear::vector_from_json(&doc[k]).unwrap();
        let c = linear::verify_l1(&mat(&doc["D"]), &v("h"), &v("weights"), &v("potential"), &v("dual")).unwrap();
        return json!({"kind": "l1", "status": format!("{:?}", c.status), "lower": c.lower.map(|x| x.to_string()),
                      "upper": c.upper.to_string(), "repair_impossible": c.repair_impossible});
    }
    if doc.get("D_source").is_some() {
        let g0 = doc.get("G0").map(mat);
        let g1 = doc.get("G1").map(mat);
        let g = match (&g0, &g1) {
            (Some(a), Some(b)) => Some((a, b)),
            _ => None,
        };
        let st = transport::verify_transport(&mat(&doc["D_source"]), &mat(&doc["D_target"]), &mat(&doc["F0"]), &mat(&doc["F1"]), g);
        let reflection_possible = transport::zero_map_admits_left_inverse(&mat(&doc["F0"]));
        return json!({"kind": "transport", "status": format!("{st:?}"), "left_inverse_possible": reflection_possible});
    }
    json!({"kind": "unknown", "name": name})
}

fn main() {
    let dir = std::env::args().nth(1).map(PathBuf::from).unwrap_or_else(|| PathBuf::from("../../examples"));
    let mut names: Vec<_> = std::fs::read_dir(&dir).expect("examples dir").filter_map(|e| e.ok()).map(|e| e.path())
        .filter(|p| p.extension().map(|x| x == "json").unwrap_or(false)).collect();
    names.sort();
    let mut out = serde_json::Map::new();
    for p in names {
        let doc: Value = serde_json::from_str(&std::fs::read_to_string(&p).unwrap()).unwrap();
        let name = p.file_stem().unwrap().to_string_lossy().to_string();
        out.insert(name.clone(), derive(&name, &doc));
    }
    println!("{}", serde_json::to_string_pretty(&Value::Object(out)).unwrap());
}
