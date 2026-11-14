//! Online monitors: fiber collisions, prefix budget excursions, and incremental
//! 1-cochain cycle closure with an exact weighted-l1 certificate.

use crate::canon::canonical;
use crate::{q, Q};
use num_traits::{Signed, Zero};
use serde_json::Value;
use std::collections::BTreeMap;

/// Online report-fiber monitor. Once a collision is seen it is never retracted:
/// extending the trace cannot make an observed collision disappear.
#[derive(Default)]
pub struct FiberMonitor {
    fibers: BTreeMap<String, (String, String)>,
    pub collision: Option<(String, String)>,
}

impl FiberMonitor {
    pub fn observe(&mut self, state_id: &str, report: &Value, query: &Value) -> bool {
        let k = canonical(report);
        let qv = canonical(query);
        match self.fibers.get(&k) {
            Some((left, q0)) if *q0 != qv && self.collision.is_none() => {
                self.collision = Some((left.clone(), state_id.to_string()));
            }
            Some(_) => {}
            None => {
                self.fibers.insert(k, (state_id.to_string(), qv));
            }
        }
        self.collision.is_some()
    }
}

/// Every-prefix budget monitor. The first excursion latches an alert; later steps
/// cannot clear it, even if drift returns inside the bound.
pub struct PrefixMonitor {
    bound: i64,
    pub cumulative: i64,
    pub steps: usize,
    pub first_alert: Option<usize>,
}

impl PrefixMonitor {
    pub fn new(bound: i64) -> Self {
        Self { bound, cumulative: 0, steps: 0, first_alert: None }
    }
    pub fn step(&mut self, delta: i64) -> bool {
        self.cumulative += delta;
        self.steps += 1;
        if self.cumulative.abs() > self.bound && self.first_alert.is_none() {
            self.first_alert = Some(self.steps);
        }
        self.first_alert.is_some()
    }
}

#[derive(Debug, Clone)]
pub struct CycleReport {
    pub defect: Q,
    pub l1_distance: Q,
    /// Dual witness on the cycle edges (edge index -> z_e), |z_e| <= w_e, a cycle flow.
    pub dual: BTreeMap<usize, Q>,
}

/// Incremental 1-cochain monitor on a directed graph. Edge e = (u -> v) carries h_e
/// and weight w_e. A spanning forest gives potentials x with x_v - x_u = h_e on tree
/// edges. An edge that closes a cycle has defect h_e - (x_v - x_u). For one
/// fundamental cycle the weighted-l1 repair distance is |defect| * (min weight on the
/// cycle), certified by the cycle-flow dual z = sign(defect) * min_w * orientation.
#[derive(Default)]
pub struct CochainMonitor {
    tree: BTreeMap<String, Vec<(String, usize, i64)>>, // node -> (neighbour, edge, +1 if edge points to neighbour)
    potential: BTreeMap<String, Q>,
    pub edges: Vec<(String, String, Q, Q)>,
    pub cycles: Vec<CycleReport>,
}

impl CochainMonitor {
    /// Tree path from a to b as (edge, orientation along the walk), or None if disconnected.
    fn tree_path(&self, a: &str, b: &str) -> Option<Vec<(usize, i64)>> {
        let mut prev: BTreeMap<String, (String, usize, i64)> = BTreeMap::new();
        let mut queue = std::collections::VecDeque::from([a.to_string()]);
        let mut seen = std::collections::BTreeSet::from([a.to_string()]);
        while let Some(n) = queue.pop_front() {
            if n == b {
                let mut path = Vec::new();
                let mut cur = n;
                while let Some((p, e, o)) = prev.get(&cur).cloned() {
                    path.push((e, o));
                    cur = p;
                }
                path.reverse();
                return Some(path);
            }
            for (m, e, o) in self.tree.get(&n).cloned().unwrap_or_default() {
                if seen.insert(m.clone()) {
                    prev.insert(m.clone(), (n.clone(), e, o));
                    queue.push_back(m);
                }
            }
        }
        None
    }

    fn reset_potentials_from(&mut self, start: &str) {
        let mut queue = std::collections::VecDeque::from([start.to_string()]);
        let mut seen = std::collections::BTreeSet::from([start.to_string()]);
        while let Some(n) = queue.pop_front() {
            for (m, e, o) in self.tree.get(&n).cloned().unwrap_or_default() {
                if seen.insert(m.clone()) {
                    let h = self.edges[e].2.clone();
                    let x = &self.potential[&n] + if o > 0 { h } else { -h };
                    self.potential.insert(m.clone(), x);
                    queue.push_back(m);
                }
            }
        }
    }

    /// Add edge u -> v with value h and weight w. Returns the cycle report if it closes a cycle.
    pub fn add_edge(&mut self, u: &str, v: &str, h: Q, w: Q) -> Option<CycleReport> {
        assert!(w.is_positive(), "weights must be positive");
        let e = self.edges.len();
        self.edges.push((u.to_string(), v.to_string(), h.clone(), w.clone()));
        for n in [u, v] {
            self.tree.entry(n.to_string()).or_default();
            self.potential.entry(n.to_string()).or_insert_with(|| q(0));
        }
        match self.tree_path(v, u) {
            None => {
                self.tree.get_mut(u).unwrap().push((v.to_string(), e, 1));
                self.tree.get_mut(v).unwrap().push((u.to_string(), e, -1));
                self.reset_potentials_from(u);
                None
            }
            Some(back) => {
                let defect = &h - (&self.potential[v] - &self.potential[u]);
                // Cycle: u -> v along e, then v -> u along the tree.
                let mut dirs: Vec<(usize, i64)> = vec![(e, 1)];
                dirs.extend(back);
                let minw = dirs.iter().map(|(i, _)| self.edges[*i].3.clone()).min().unwrap();
                let s = if defect.is_negative() { -1 } else { 1 };
                let dual = dirs.iter().map(|(i, d)| (*i, &minw * q(s * d))).collect();
                let rep = CycleReport { l1_distance: defect.abs() * &minw, defect, dual };
                self.cycles.push(rep.clone());
                Some(rep)
            }
        }
    }

    /// Check a dual witness: cycle-flow condition (D^T z = 0) and |z_e| <= w_e. Return z . h.
    pub fn dual_value(&self, z: &BTreeMap<usize, Q>) -> Option<Q> {
        let mut div: BTreeMap<&str, Q> = BTreeMap::new();
        for (i, ze) in z {
            let (u, v, _, w) = &self.edges[*i];
            if ze.abs() > *w {
                return None;
            }
            *div.entry(u.as_str()).or_insert_with(|| q(0)) -= ze;
            *div.entry(v.as_str()).or_insert_with(|| q(0)) += ze;
        }
        if div.values().any(|d| !d.is_zero()) {
            return None;
        }
        Some(z.iter().map(|(i, ze)| ze * &self.edges[*i].2).sum())
    }
}
