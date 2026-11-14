//! Verification-boundary regressions from the joint review of PR #157 (2026-11-14).
//! Malformed or ill-typed input must be rejected, never truncated into evidence.

use lggr_derivations::{linear, q, transport, Q};

fn m(rows: &[&[i64]]) -> linear::Matrix {
    rows.iter().map(|r| r.iter().map(|v| q(*v)).collect()).collect()
}

// Review finding 1: ill-typed commuting square must not certify a retraction.
#[test]
fn boundary_transport_rejects_incompatible_dimensions() {
    let (ds, dt) = (m(&[&[0]]), m(&[&[0], &[1]]));
    let (f0, f1, g0, g1) = (m(&[&[1]]), m(&[&[1]]), m(&[&[1]]), m(&[&[1]]));
    assert_eq!(transport::verify_transport(&ds, &dt, &f0, &f1, Some((&g0, &g1))), transport::TransportStatus::InvalidTransport);
    assert_eq!(transport::verify_transport(&ds, &dt, &f0, &f1, None), transport::TransportStatus::InvalidTransport);
    // Ragged and empty matrices are rejected too.
    let ragged = vec![vec![q(1)], vec![q(1), q(0)]];
    assert_eq!(transport::verify_transport(&ragged, &dt, &f0, &f1, None), transport::TransportStatus::InvalidTransport);
    assert_eq!(transport::verify_transport(&vec![], &dt, &f0, &f1, None), transport::TransportStatus::InvalidTransport);
}

// Review finding 2: a right-hand side longer than C^1 must not be classified exact.
#[test]
fn boundary_cochain_rejects_length_mismatch() {
    let d0 = m(&[&[1]]);
    assert!(linear::classify_cochain(&d0, &[q(1), q(2)], &vec![]).is_err());
    assert!(linear::classify_cochain(&d0, &[], &vec![]).is_err());
    // D1 must act on C^1.
    let d0 = m(&[&[-1, 1, 0], &[0, -1, 1], &[-1, 0, 1]]);
    assert!(linear::classify_cochain(&d0, &[q(1), q(1), q(1)], &m(&[&[1, 1]])).is_err());
    assert!(linear::solve_exact(&m(&[&[1]]), &[q(1), q(2)]).is_err());
    assert!(linear::matvec(&m(&[&[1, 2]]), &[q(1)]).is_err());
    assert!(linear::matmul(&m(&[&[1, 2]]), &m(&[&[1, 2]])).is_err());
    assert!(linear::sub(&m(&[&[1]]), &m(&[&[1, 2]])).is_err());
    let z: Vec<Q> = vec![q(1), q(1)];
    assert!(linear::verify_l1(&m(&[&[1]]), &z, &z, &[q(0)], &z).is_err());
}

// Review finding 2 (related): a left inverse exists iff the map is injective, not iff it is nonzero.
#[test]
fn boundary_left_inverse_requires_injectivity() {
    assert!(!transport::admits_left_inverse(&m(&[&[1, 0]])).unwrap());
    assert!(!transport::admits_left_inverse(&m(&[&[0, 0, 0]])).unwrap());
    assert!(!transport::admits_left_inverse(&m(&[&[1, 1], &[2, 2]])).unwrap());
    assert!(transport::admits_left_inverse(&m(&[&[1], &[0]])).unwrap());
    assert!(transport::admits_left_inverse(&m(&[&[0, 1, 0], &[1, 0, 0], &[0, 0, 1]])).unwrap());
    assert_eq!(linear::rank(&m(&[&[1, 2, 3], &[2, 4, 6], &[1, 0, 1]])).unwrap(), 2);
}

// Review finding 3: integer predictors on a two-point fiber attain ceil((b-a)/2), not (b-a)/2.
#[test]
fn boundary_integer_two_point_optimum_is_ceiling() {
    for a in -5i64..=5 {
        for b in a..=5 {
            let best = (a - 3..=b + 3).map(|z| (a - z).abs().max((b - z).abs())).min().unwrap();
            assert_eq!(best, (b - a + 1) / 2, "a={a} b={b}");
        }
    }
    // The reviewer's case: a = 0, b = 1 gives 1 over the integers, 1/2 only over the rationals.
    assert_eq!((0..=1).map(|z: i64| (0 - z).abs().max((1 - z).abs())).min().unwrap(), 1);
}
