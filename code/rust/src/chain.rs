//! Hash-chained event logs: verify the append-only chain recorded by the workflows.
//!
//! Record i is {index, previous, kind, data, sha256} where sha256 is the digest of the
//! canonical body {index, previous, kind, data} and previous is record i-1's sha256.
//! Numbers keep their recorded text (serde_json `arbitrary_precision`), so the
//! canonical form matches the writer's byte for byte.

use crate::canon::digest;
use serde_json::{json, Value};

/// Index of the first broken record, or None if the whole chain verifies.
pub fn first_break(records: &[Value]) -> Option<usize> {
    let mut previous = Value::Null;
    for (i, r) in records.iter().enumerate() {
        let body = json!({"index": r["index"], "previous": r["previous"], "kind": r["kind"], "data": r["data"]});
        let ok = r["index"].as_u64() == Some(i as u64)
            && r["previous"] == previous
            && r["sha256"].as_str() == Some(digest(&body).as_str());
        if !ok {
            return Some(i);
        }
        previous = r["sha256"].clone();
    }
    None
}

pub fn parse_jsonl(text: &str) -> Result<Vec<Value>, String> {
    text.lines().filter(|l| !l.trim().is_empty()).map(|l| serde_json::from_str(l).map_err(|e| e.to_string())).collect()
}
