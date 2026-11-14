//! One test per ledger claim that Rust checks. Test names are cited verbatim in
//! `dag/derivations/derivation_dag.json` (`rust_tests`) and in the claim ledger.

use lggr_derivations::{bell, descent, history, linear, minimax, q, selectors, streaming, transport, Q};
use num_traits::Zero;
use serde_json::{json, Value};
use std::collections::BTreeMap;

fn rows(report: &[u8], query: &[u8]) -> Vec<descent::Row> {
    report
        .iter()
        .zip(query)
        .enumerate()
        .map(|(i, (r, qv))| descent::Row { state_id: format!("x{i}"), report: json!(r), query: json!(qv) })
        .collect()
}

/// All maps {0,1,2} -> {0,..,k-1} as value vectors.
fn maps(k: u8) -> Vec<Vec<u8>> {
    let mut out = Vec::new();
    for a in 0..k {
        for b in 0..k {
            for c in 0..k {
                out.push(vec![a, b, c]);
            }
        }
    }
    out
}

// LGGR-C01: an explicit collision refutes every decoder.
#[test]
fn c01_collision_refutes_every_decoder() {
    // Exhaustive: 3 states, reports in {0,1,2}, queries in {0,1}; every decoder A -> B.
    for p in maps(3) {
        for qv in maps(2).into_iter().filter(|v| v.iter().all(|x| *x < 2)) {
            let collision = (0..3).any(|i| (0..3).any(|j| p[i] == p[j] && qv[i] != qv[j]));
            let any_decoder = (0..8u8).any(|d| (0..3).all(|i| (d >> p[i]) & 1 == qv[i]));
            assert!(!(collision && any_decoder));
        }
    }
}

// LGGR-C02: decoder-or-collision is an exact dichotomy on a finite table, and the decoder replays.
#[test]
fn c02_decoder_or_collision_exhaustive_census() {
    let mut count = 0;
    for p in maps(3) {
        for qv in maps(2).into_iter().filter(|v| v.iter().all(|x| *x < 2)) {
            let rs = rows(&p, &qv);
            let constant = (0..3).all(|i| (0..3).all(|j| p[i] != p[j] || qv[i] == qv[j]));
            match descent::analyze(&rs) {
                descent::Descent::Decoder(d) => {
                    assert!(constant);
                    assert!(descent::decoder_valid(&rs, &d));
                }
                descent::Descent::Collision(a, b) => {
                    assert!(!constant);
                    let ra = rs.iter().find(|r| r.state_id == a).unwrap();
                    let rb = rs.iter().find(|r| r.state_id == b).unwrap();
                    assert_eq!(ra.report, rb.report);
                    assert_ne!(ra.query, rb.query);
                }
            }
            count += 1;
        }
    }
    assert_eq!(count, 216);
}

// LGGR-C03: deterministic postprocessing of the report preserves every collision.
#[test]
fn c03_postprocessing_preserves_collision() {
    for p in maps(3) {
        for f in maps(3) {
            for i in 0..3 {
                for j in 0..3 {
                    if p[i] == p[j] {
                        assert_eq!(f[p[i] as usize], f[p[j] as usize]);
                    }
                }
            }
        }
    }
}

// LGGR-C04: any report-only evaluator errs on at least one member of a colliding pair.
#[test]
fn c04_verdict_ceiling_on_collision() {
    let a = descent::Row { state_id: "good".into(), report: json!([1, 1]), query: json!(true) };
    let b = descent::Row { state_id: "bad".into(), report: json!([1, 1]), query: json!(false) };
    for out in [json!(true), json!(false)] {
        assert!(descent::report_only_errors_on_collision(|_| out.clone(), &a, &b) >= 1);
    }
}

// LGGR-C05: Delta_E = Eg - E1*E2 lies in {-1,0,1}, and Delta_E = -1 exactly at (1,1,0).
#[test]
fn c05_evaluator_defect_partition() {
    for m in 0..8u8 {
        let (e1, e2, eg) = (m & 1 == 1, m & 2 == 2, m & 4 == 4);
        let d = descent::evaluator_defect(e1, e2, eg);
        assert!((-1..=1).contains(&d));
        assert_eq!(d == -1, e1 && e2 && !eg);
        assert_eq!(descent::defect_kind(d) == "NGD", d == -1);
    }
}

// LGGR-C06: signed increments telescope to endpoint minus baseline.
#[test]
fn c06_telescoping_all_short_histories() {
    let vals = [-2i64, -1, 0, 1, 2];
    for a in vals {
        for b in vals {
            for c in vals {
                for d in vals {
                    let (s, e) = history::telescope(&[a, b, c, d]);
                    assert_eq!(s, e);
                }
            }
        }
    }
}

// LGGR-C07: local step bounds do not imply the endpoint bound; witness (0,1,2), B = 1.
#[test]
fn c07_local_steps_do_not_imply_endpoint_bound() {
    let h = [0, 1, 2];
    assert!(history::local_steps_ok(&h, 1));
    assert!(!history::endpoint_ok(&h, 1));
}

// LGGR-C08: every-prefix boundedness implies endpoint boundedness, not conversely; witness (0,1,2,1).
#[test]
fn c08_every_prefix_strictly_stronger_than_endpoint() {
    let vals = [-2i64, -1, 0, 1, 2];
    for a in vals {
        for b in vals {
            for c in vals {
                let h = [0, a, b, c];
                if history::every_prefix_ok(&h, 1) {
                    assert!(history::endpoint_ok(&h, 1));
                }
            }
        }
    }
    let w = [0, 1, 2, 1];
    assert!(history::endpoint_ok(&w, 1) && !history::every_prefix_ok(&w, 1));
}

// LGGR-C09: unsigned step reports collide on (0,1,0) and (0,1,2); signed reports separate them.
#[test]
fn c09_unsigned_reports_collide_signed_reports_separate() {
    let (good, bad) = ([0, 1, 0], [0, 1, 2]);
    assert_eq!(history::unsigned_report(&good), history::unsigned_report(&bad));
    assert_ne!(history::endpoint_ok(&good, 1), history::endpoint_ok(&bad, 1));
    assert_ne!(history::signed_report(&good), history::signed_report(&bad));
}

// LGGR-C10: an online prefix alert latches at the first excursion and is never cleared.
#[test]
fn c10_prefix_violation_latches() {
    let mut m = streaming::PrefixMonitor::new(2);
    let deltas = [1, 2, -3, 0, 1];
    let alerts: Vec<bool> = deltas.iter().map(|d| m.step(*d)).collect();
    assert_eq!(m.first_alert, Some(2));
    assert_eq!(alerts, vec![false, true, true, true, true]);
    // The endpoint is back inside the bound, yet the prefix query stays false.
    assert!(m.cumulative.abs() <= 2);
}

// LGGR-C11: an online fiber collision persists under every trace extension.
#[test]
fn c11_online_collision_monotonicity() {
    let mut m = streaming::FiberMonitor::default();
    let r = json!({"workload_type": "distributed_etl", "target_environment": "production"});
    assert!(!m.observe("task_batch_001", &r, &json!({"approval_tier": "Tier-3"})));
    assert!(m.observe("task_batch_002", &r, &json!({"approval_tier": "Tier-1"})));
    for i in 0..10 {
        assert!(m.observe(&format!("later_{i}"), &json!(i), &json!(i)));
    }
    assert_eq!(m.collision, Some(("task_batch_001".into(), "task_batch_002".into())));
}

// LGGR-C14: weak duality: a bounded annihilating dual lower-bounds every primal residual.
#[test]
fn c14_l1_weak_duality_on_triangle() {
    let d: linear::Matrix = vec![vec![q(-1), q(1), q(0)], vec![q(0), q(-1), q(1)], vec![q(-1), q(0), q(1)]];
    let h = vec![q(1), q(1), q(1)];
    let w = vec![q(1), q(1), q(1)];
    let z = vec![q(1), q(1), q(-1)];
    for a in -3..=3 {
        for b in -3..=3 {
            let x = vec![q(0), q(a), q(b)];
            let c = linear::verify_l1(&d, &h, &w, &x, &z).unwrap();
            assert!(c.lower.clone().unwrap() <= c.upper);
        }
    }
}

// LGGR-C17: an incremental closing edge yields defect h - (x_v - x_u); repair distance |defect| * min w,
// certified by a cycle-flow dual (cookbook 03 instance: defect 3, distance 3).
#[test]
fn c17_incremental_cycle_closure_certificate() {
    let mut m = streaming::CochainMonitor::default();
    assert!(m.add_edge("Agent_A", "Agent_B", q(1), q(1)).is_none());
    assert!(m.add_edge("Agent_B", "Agent_C", q(1), q(1)).is_none());
    let r = m.add_edge("Agent_C", "Agent_A", q(1), q(1)).unwrap();
    assert_eq!(r.defect, q(3));
    assert_eq!(r.l1_distance, q(3));
    assert_eq!(m.dual_value(&r.dual), Some(q(3)));
    // Weighted case with mixed orientations: the dual still certifies |defect| * min w.
    let mut m = streaming::CochainMonitor::default();
    m.add_edge("a", "b", q(2), q(5));
    m.add_edge("c", "b", q(1), q(2));
    let r = m.add_edge("a", "c", q(4), q(3)).unwrap();
    assert_eq!(r.defect, q(3));
    assert_eq!(r.l1_distance, q(6));
    assert_eq!(m.dual_value(&r.dual), Some(r.l1_distance.clone()));
}

// LGGR-C18: an acyclic (tree) stream of 1-cochains is always exact.
#[test]
fn c18_open_chain_exactness() {
    let mut m = streaming::CochainMonitor::default();
    for (u, v, h) in [("0", "1", 5), ("1", "2", -2), ("3", "1", 7)] {
        assert!(m.add_edge(u, v, q(h), q(1)).is_none());
    }
    assert!(m.cycles.is_empty());
}

// LGGR-C21: two-point fiber minimax: 2 max(|a-z|,|b-z|) >= b-a, attained at the midpoint.
#[test]
fn c21_two_point_fiber_minimax() {
    for a in -4i64..=4 {
        for b in a..=4 {
            for z in -6..=6 {
                assert!(2 * (a - z).abs().max((b - z).abs()) >= b - a);
            }
            if (a + b) % 2 == 0 {
                let m = (a + b) / 2;
                assert_eq!(2 * (a - m).abs().max((b - m).abs()), b - a);
            }
        }
    }
}

// LGGR-C22: on any finite table, every report-only integer predictor has doubled error >= max fiber spread,
// and the (doubled) fiber-midpoint predictor attains it.
#[test]
fn c22_general_fiber_minimax_floor() {
    // 3 histories, observations in {0,1}, targets in {-2..2}: every table and every predictor.
    let ts = [-2i64, -1, 0, 1, 2];
    for o in 0..8u8 {
        for f0 in ts {
            for f1 in ts {
                for f2 in ts {
                    let table: Vec<(i64, i64)> = [f0, f1, f2].iter().enumerate().map(|(i, f)| (((o >> i) & 1) as i64, *f)).collect();
                    let floor = minimax::doubled_floor(&table);
                    for g0 in -3..=3 {
                        for g1 in -3..=3 {
                            let e = minimax::worst_doubled_error(&table, |y| if y == 0 { g0 } else { g1 });
                            assert!(e >= floor);
                        }
                    }
                    assert_eq!(minimax::midpoint_doubled_error(&table), floor);
                }
            }
        }
    }
}

// LGGR-C23: recursion on fixed evidence cannot shrink the floor: any finite composition of updates
// that sees only the report gives one output per fiber.
#[test]
fn c23_evidence_preserving_recursion_keeps_floor() {
    let table = vec![(0i64, 0i64), (0, 4), (1, 1)];
    let floor = minimax::doubled_floor(&table);
    assert_eq!(floor, 4);
    let updates: Vec<fn(i64, i64) -> i64> = vec![|y, g| g + y, |_, g| 2 * g - 1, |y, g| (g - 3 * y).abs(), |_, g| g / 2];
    for seed in -3..=3 {
        let predictor = |y: i64| updates.iter().fold(seed, |g, u| u(y, g));
        assert!(minimax::worst_doubled_error(&table, predictor) >= floor);
    }
}

// LGGR-C24: CHSH: every deterministic local strategy has |S| = 2, so local |S| <= 2; the PR box has S = 4.
#[test]
fn c24_chsh_local_bound_and_pr_box() {
    let s = [-1i8, 1];
    for a0 in s {
        for a1 in s {
            for b0 in s {
                for b1 in s {
                    assert_eq!(bell::chsh_deterministic([a0, a1], [b0, b1]).abs(), 2);
                }
            }
        }
    }
    assert_eq!(bell::chsh_local_max(), 2);
    assert_eq!(bell::chsh_pr_box(), 4);
}

// LGGR-C25: an odd cycle of pairwise "differ" constraints is locally and pathwise satisfiable but has no global section.
#[test]
fn c25_odd_cycle_local_green_global_red() {
    for n in [3usize, 5, 7] {
        let (edges, paths, global) = bell::odd_cycle_inequality(n);
        assert!(edges && paths);
        assert_eq!(global, 0);
    }
    // Even cycles glue: exactly two global sections.
    assert_eq!(bell::odd_cycle_inequality(4).2, 2);
}

// LGGR-C26: Mermin-Peres square: each context is satisfiable, no global +/-1 assignment exists.
#[test]
fn c26_mermin_peres_parity_obstruction() {
    assert!(bell::mermin_peres_contexts_locally_satisfiable());
    assert_eq!(bell::mermin_peres_assignments(), 0);
}

// LGGR-C27: scaled contextual-fraction packing identity: U - R = S - (m-1)N, so S - Gamma <= (m-1)N.
#[test]
fn c27_contextual_fraction_packing_identity() {
    for s in 1i64..=6 {
        for m in 1i64..=4 {
            for n in 0i64..=5 {
                let (u, r) = (s + n, m * n);
                assert_eq!(u - r, s - (m - 1) * n);
                for gamma in (u - r)..=(u - r + 3) {
                    assert!(s - gamma <= (m - 1) * n);
                }
            }
        }
    }
}

// LGGR-C28: GHZ rnd2 arithmetic over denominator 768: CF = 228/768 = 19/64, N_min = 75/768 = 25/256,
// CF - 2 N_min = 13/128 > 0. Arithmetic on the supplied optima only (optimality not checked here).
#[test]
fn c28_ghz_rnd2_cf_vs_neg_mass_arithmetic() {
    let qq = |a: i64, b: i64| Q::new(a.into(), b.into());
    let cf = qq(768 - 540, 768);
    let nmin = qq(75, 768);
    assert_eq!(cf, qq(19, 64));
    assert_eq!(nmin, qq(25, 256));
    assert_eq!(&cf - qq(2, 1) * &nmin, qq(13, 128));
    // Order reversal against Q_{5/8}: CF = 1/4 < CF(p*), N_min = 1/8 > N_min(p*).
    assert!(qq(1, 4) < cf && qq(1, 8) > nmin);
}

// LGGR-C29: boundary-sufficient composition (Eg = E1 && E2) with passing stages gives Delta_E = 0.
#[test]
fn c29_boundary_sufficient_gluing_zero_defect() {
    for e1 in [false, true] {
        for e2 in [false, true] {
            let d = descent::evaluator_defect(e1, e2, e1 && e2);
            assert_eq!(d, 0);
        }
    }
}

// LGGR-C30: a collision between two locally passing traces that disagree globally forces NGD on one branch.
#[test]
fn c30_boundary_insufficiency_forces_ngd() {
    for (egx, egy) in [(true, false), (false, true)] {
        let dx = descent::evaluator_defect(true, true, egx);
        let dy = descent::evaluator_defect(true, true, egy);
        assert!(dx == -1 || dy == -1);
    }
}

// LGGR-C31: enriching a report with a feature that separates the pair removes that collision.
#[test]
fn c31_metadata_refinement_eliminates_collision() {
    let p = |x: u8| x / 2; // collides 0,1 and 2,3
    let qv = |x: u8| x % 2;
    let mfeat = |x: u8| x % 2 == 1;
    let rs: Vec<descent::Row> = (0..4u8)
        .map(|x| descent::Row { state_id: x.to_string(), report: json!([p(x), mfeat(x)]), query: json!(qv(x)) })
        .collect();
    assert!(matches!(descent::analyze(&rs), descent::Descent::Decoder(_)));
}

// LGGR-C32: in-model soundness of the host elimination rule: if the true hypothesis is in the space and
// observations are faithful, the host never accepts a failing system. Exhaustive on small spaces.
#[test]
fn c32_host_rule_no_false_accept_in_model() {
    // 3 hypotheses, 2 binary checks, every prediction table and verdict vector.
    for preds in 0u32..64 {
        for verdicts in 0u8..8 {
            let space = selectors::Space {
                predicted: (0..3).map(|h| (0..2).map(|c| ((preds >> (2 * h + c)) & 1) as u8).collect()).collect(),
                verdict: (0..3).map(|h| (verdicts >> h) & 1 == 1).collect(),
            };
            for truth in 0..3 {
                for checks in 0u8..4 {
                    let obs: Vec<(usize, u8)> = (0..2).filter(|c| (checks >> c) & 1 == 1).map(|c| (c, space.predicted[truth][c])).collect();
                    let d = space.host_rule(&obs);
                    assert_ne!(d, selectors::Decision::ModelMismatch);
                    if d == selectors::Decision::Accept {
                        assert!(space.verdict[truth]);
                    }
                    if d == selectors::Decision::Reject {
                        assert!(!space.verdict[truth]);
                    }
                }
            }
        }
    }
}

// LGGR-C33: out of model, the host rule can accept a failing system: the evidence is consistent with a passing hypothesis.
#[test]
fn c33_host_rule_false_accept_out_of_model() {
    let space = selectors::Space { predicted: vec![vec![1], vec![0]], verdict: vec![true, false] };
    // True world: outside the space, fails its contract, but check 0 returns 1.
    let obs = [(0usize, 1u8)];
    assert_eq!(space.host_rule(&obs), selectors::Decision::Accept);
    let truth_passes = false;
    assert!(!truth_passes);
}

// LGGR-C34: the LGGR selector quantity (live accept/reject pairs) is zero exactly when the host rule is resolved.
#[test]
fn c34_zero_verdict_pairs_iff_resolved() {
    for verdicts in 0u8..16 {
        for alive_mask in 1u8..16 {
            let space = selectors::Space { predicted: vec![vec![]; 4], verdict: (0..4).map(|h| (verdicts >> h) & 1 == 1).collect() };
            let alive: Vec<usize> = (0..4).filter(|h| (alive_mask >> h) & 1 == 1).collect();
            let pass = alive.iter().filter(|h| space.verdict[**h]).count();
            let resolved = pass == 0 || pass == alive.len();
            assert_eq!(space.verdict_pairs(&alive) == 0, resolved);
        }
    }
}

// Sanity for the derivation of C16 (triangle cochain): solve_exact on the triangle.
#[test]
fn c16_triangle_budget_differences_exact() {
    let d0: linear::Matrix = vec![vec![q(-1), q(1), q(0)], vec![q(0), q(-1), q(1)], vec![q(-1), q(0), q(1)]];
    let x = linear::solve_exact(&d0, &[q(1), q(1), q(2)]).unwrap().unwrap();
    assert_eq!(linear::matvec(&d0, &x).unwrap(), vec![q(1), q(1), q(2)]);
    assert!(linear::solve_exact(&d0, &[q(1), q(1), q(1)]).unwrap().is_none());
    let _ = BTreeMap::<u8, u8>::new();
    let _: Value = json!(null);
    assert!(Q::zero().is_zero());
}

// LGGR-C20: a non-injective projection admits no left inverse, so it cannot reflect nonrepairability.
#[test]
fn c20_non_injective_projection_blocks_retraction() {
    // Chord drop (h01, h12, h02) -> (h01, h12) sends (1,1,2) and (1,1,1) to (1,1).
    let drop = |h: [i64; 3]| [h[0], h[1]];
    assert_eq!(drop([1, 1, 2]), drop([1, 1, 1]));
    // Exact source vs frustrated source: they differ in repairability yet share an image.
    let d0: linear::Matrix = vec![vec![q(-1), q(1), q(0)], vec![q(0), q(-1), q(1)], vec![q(-1), q(0), q(1)]];
    assert!(linear::solve_exact(&d0, &[q(1), q(1), q(2)]).unwrap().is_some());
    assert!(linear::solve_exact(&d0, &[q(1), q(1), q(1)]).unwrap().is_none());
    let zero: linear::Matrix = vec![vec![q(0), q(0), q(0)]];
    assert!(!transport::admits_left_inverse(&zero).unwrap());
}
