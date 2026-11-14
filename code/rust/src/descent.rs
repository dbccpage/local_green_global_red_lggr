//! Decoder-or-collision on a supplied finite table, and the Boolean evaluator defect.
//!
//! For a report map p : X -> A and query q : X -> B on a finite carrier, exactly one
//! holds: q is constant on every realized fiber p^{-1}(a) (a decoder exists on p(X)),
//! or two states share a report and differ on the query (a collision).

use crate::canon::canonical;
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Row {
    pub state_id: String,
    pub report: Value,
    pub query: Value,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Descent {
    /// Realized report (canonical text) -> query (canonical text).
    Decoder(BTreeMap<String, String>),
    /// (left, right) state ids: equal reports, different queries.
    Collision(String, String),
}

/// Rows from `{"rows": [{"state_id", "report", "query"}]}`.
pub fn rows_from_json(v: &Value) -> Result<Vec<Row>, String> {
    let rows = v["rows"].as_array().ok_or("rows must be an array")?;
    let mut out = Vec::new();
    let mut seen = std::collections::BTreeSet::new();
    for r in rows {
        let id = r["state_id"].as_str().ok_or("state_id must be a string")?.to_string();
        if !seen.insert(id.clone()) {
            return Err(format!("duplicate state_id {id}"));
        }
        out.push(Row { state_id: id, report: r["report"].clone(), query: r["query"].clone() });
    }
    Ok(out)
}

/// Decide decoder or collision. Rows are processed in state-id order, so the
/// reported collision is deterministic. Equality is canonical JSON equality
/// (type-sensitive: `true` and `1` are different observations).
pub fn analyze(rows: &[Row]) -> Descent {
    let mut sorted: Vec<&Row> = rows.iter().collect();
    sorted.sort_by(|a, b| a.state_id.cmp(&b.state_id));
    let mut rep: BTreeMap<String, (&str, String)> = BTreeMap::new();
    for r in sorted {
        let k = canonical(&r.report);
        let qv = canonical(&r.query);
        match rep.get(&k) {
            Some((left, q0)) if *q0 != qv => {
                return Descent::Collision(left.to_string(), r.state_id.clone());
            }
            Some(_) => {}
            None => {
                rep.insert(k, (&r.state_id, qv));
            }
        }
    }
    Descent::Decoder(rep.into_iter().map(|(k, (_, q))| (k, q)).collect())
}

/// Replay a decoder: it must cover exactly the realized reports and agree on every row.
pub fn decoder_valid(rows: &[Row], dec: &BTreeMap<String, String>) -> bool {
    let realized: std::collections::BTreeSet<String> = rows.iter().map(|r| canonical(&r.report)).collect();
    realized.len() == dec.len()
        && realized.iter().all(|k| dec.contains_key(k))
        && rows.iter().all(|r| dec[&canonical(&r.report)] == canonical(&r.query))
}

/// Boolean evaluator defect Delta_E = E_g - E_1 * E_2.
pub fn evaluator_defect(e1: bool, e2: bool, eg: bool) -> i8 {
    (eg as i8) - (e1 as i8) * (e2 as i8)
}

/// NGD (-1, local green / global red), ZDR (0), PGD (+1).
pub fn defect_kind(d: i8) -> &'static str {
    match d {
        -1 => "NGD",
        0 => "ZDR",
        1 => "PGD",
        _ => unreachable!("defect is in {{-1,0,1}}"),
    }
}

/// Verdict ceiling: any evaluator that factors through the report gives the same
/// verdict on both members of a colliding pair, so it is wrong on at least one.
pub fn report_only_errors_on_collision<F: Fn(&Value) -> Value>(evaluator: F, a: &Row, b: &Row) -> usize {
    [a, b].iter().filter(|r| canonical(&evaluator(&r.report)) != canonical(&r.query)).count()
}
