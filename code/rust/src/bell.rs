//! Finite local-consistency obstructions: CHSH, PR box, odd parity cycles and the
//! Mermin-Peres square. All checks are exhaustive enumeration over finite assignments.

/// CHSH value S = E(0,0) + E(0,1) + E(1,0) - E(1,1) of a deterministic local strategy
/// a(x), b(y) in {-1, +1}.
pub fn chsh_deterministic(a: [i8; 2], b: [i8; 2]) -> i64 {
    let e = |x: usize, y: usize| (a[x] * b[y]) as i64;
    e(0, 0) + e(0, 1) + e(1, 0) - e(1, 1)
}

/// Maximum |S| over all 16 deterministic local strategies. Any local hidden-variable
/// behaviour is a convex mixture of these, so |S| <= this value for all of them.
pub fn chsh_local_max() -> i64 {
    let s = [-1i8, 1];
    let mut best = 0;
    for a0 in s {
        for a1 in s {
            for b0 in s {
                for b1 in s {
                    best = best.max(chsh_deterministic([a0, a1], [b0, b1]).abs());
                }
            }
        }
    }
    best
}

/// PR box correlators: E(x,y) = +1 unless x = y = 1, where E = -1. S = 4.
pub fn chsh_pr_box() -> i64 {
    let e = |x: u8, y: u8| if x == 1 && y == 1 { -1i64 } else { 1 };
    e(0, 0) + e(0, 1) + e(1, 0) - e(1, 1)
}

/// Odd cycle of n Boolean variables with constraints x_i != x_{i+1}: every edge is
/// locally satisfiable, every proper sub-path is satisfiable, the whole cycle is not.
/// Returns (all edges locally satisfiable, all paths satisfiable, global count).
pub fn odd_cycle_inequality(n: usize) -> (bool, bool, usize) {
    let edges_ok = true; // each constraint x != y has the assignment (0,1)
    let sat = |len: usize, cyclic: bool| -> usize {
        (0u32..(1 << len))
            .filter(|m| {
                let bit = |i: usize| (m >> (i % len)) & 1;
                let k = if cyclic { len } else { len - 1 };
                (0..k).all(|i| bit(i) != bit(i + 1))
            })
            .count()
    };
    let paths_ok = sat(n, false) > 0;
    (edges_ok, paths_ok, sat(n, true))
}

/// Mermin-Peres magic square, classical version: assign +/-1 to 9 cells so every row
/// multiplies to +1 and the columns multiply to +1, +1, -1. Returns the number of
/// satisfying assignments (0: no noncontextual assignment exists).
pub fn mermin_peres_assignments() -> usize {
    (0u32..512)
        .filter(|m| {
            let v = |r: usize, c: usize| if (m >> (3 * r + c)) & 1 == 1 { -1i8 } else { 1 };
            let rows = (0..3).all(|r| v(r, 0) * v(r, 1) * v(r, 2) == 1);
            let colp = [1i8, 1, -1];
            let cols = (0..3).all(|c| v(0, c) * v(1, c) * v(2, c) == colp[c]);
            rows && cols
        })
        .count()
}

/// Each row and each column of the magic square is satisfiable on its own.
pub fn mermin_peres_contexts_locally_satisfiable() -> bool {
    // A single context of three +/-1 values with a prescribed product always has a solution.
    [1i8, -1].iter().all(|p| (0u8..8).any(|m| {
        let v = |i: u8| if (m >> i) & 1 == 1 { -1i8 } else { 1 };
        v(0) * v(1) * v(2) == *p
    }))
}
