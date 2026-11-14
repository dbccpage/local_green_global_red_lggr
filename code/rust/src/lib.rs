//! Exact derivation kernels for the LGGR claim ledger.
//!
//! AuthorityEffect: None. Every function checks supplied finite data with exact
//! integer or rational arithmetic. No floats, no solver, no tolerance. A result
//! describes the supplied instance only.
//!
//! The modules are independent re-derivations of the finite mechanisms that the
//! ledger cites. They do not call, wrap or import the Python `lggr` app.

pub mod bell;
pub mod canon;
pub mod chain;
pub mod descent;
pub mod history;
pub mod linear;
pub mod minimax;
pub mod selectors;
pub mod streaming;
pub mod transport;

pub use num_rational::BigRational as Q;

/// Parse an exact rational from a JSON integer or a rational string such as `"3/4"`.
/// Floats and Booleans are rejected, matching the claim hygiene of the examples.
pub fn q_from_json(v: &serde_json::Value) -> Result<Q, String> {
    use num_bigint::BigInt;
    use std::str::FromStr;
    match v {
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(Q::from_integer(BigInt::from(i)))
            } else if let Some(u) = n.as_u64() {
                Ok(Q::from_integer(BigInt::from(u)))
            } else {
                Err(format!("non-integer JSON number {n}; use a rational string"))
            }
        }
        serde_json::Value::String(s) => {
            let s = s.trim();
            if let Some((a, b)) = s.split_once('/') {
                let a = BigInt::from_str(a.trim()).map_err(|e| e.to_string())?;
                let b = BigInt::from_str(b.trim()).map_err(|e| e.to_string())?;
                if b == BigInt::from(0) {
                    return Err("zero denominator".into());
                }
                Ok(Q::new(a, b))
            } else {
                Ok(Q::from_integer(BigInt::from_str(s).map_err(|e| e.to_string())?))
            }
        }
        _ => Err(format!("not an exact rational: {v}")),
    }
}

/// Integer shorthand for tests and kernels.
pub fn q(i: i64) -> Q {
    Q::from_integer(num_bigint::BigInt::from(i))
}
