//! Observer-fiber minimax floor.
//!
//! For a presentation O : H -> Y and a target f : H -> Z, any predictor g that sees
//! only O(h) has worst-case error at least W_f(y)/2 on the fiber O^{-1}(y), where
//! W_f(y) is the spread max f - min f on that fiber. The midpoint attains it.
//! Errors are compared doubled (2|f - g|) so everything stays in the integers.

use std::collections::BTreeMap;

/// Fiber spreads W_f(y) for a finite table of (observation, target) pairs.
pub fn fiber_spreads(table: &[(i64, i64)]) -> BTreeMap<i64, i64> {
    let mut lo: BTreeMap<i64, (i64, i64)> = BTreeMap::new();
    for (y, f) in table {
        let e = lo.entry(*y).or_insert((*f, *f));
        e.0 = e.0.min(*f);
        e.1 = e.1.max(*f);
    }
    lo.into_iter().map(|(y, (a, b))| (y, b - a)).collect()
}

/// Worst doubled error of a predictor g(y) over the table: max 2|f(h) - g(O(h))|.
pub fn worst_doubled_error<G: Fn(i64) -> i64>(table: &[(i64, i64)], g: G) -> i64 {
    table.iter().map(|(y, f)| 2 * (f - g(*y)).abs()).max().unwrap_or(0)
}

/// The doubled minimax value: max over fibers of W_f(y).
pub fn doubled_floor(table: &[(i64, i64)]) -> i64 {
    fiber_spreads(table).values().copied().max().unwrap_or(0)
}

/// Doubled midpoint predictor: 2 g(y) = min + max on the fiber. Returns the doubled
/// worst error of that predictor, which equals the doubled floor.
pub fn midpoint_doubled_error(table: &[(i64, i64)]) -> i64 {
    let mut ext: BTreeMap<i64, (i64, i64)> = BTreeMap::new();
    for (y, f) in table {
        let e = ext.entry(*y).or_insert((*f, *f));
        e.0 = e.0.min(*f);
        e.1 = e.1.max(*f);
    }
    table
        .iter()
        .map(|(y, f)| {
            let (a, b) = ext[y];
            (2 * f - (a + b)).abs()
        })
        .max()
        .unwrap_or(0)
}
