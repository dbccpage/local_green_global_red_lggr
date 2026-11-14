//! Commuting-square transport and chain-retraction checks on finite rational maps.
//!
//! Forward commutation F1 Ds = Dt F0 carries repairs from source to target. A left
//! inverse chain map G (G1 Dt = Ds G0, G0 F0 = I, G1 F1 = I) also reflects
//! nonrepairability back to the source. Forward commutation alone does not.

use crate::linear::{identity, is_zero, matmul, sub, Matrix};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TransportStatus {
    InvalidTransport,
    CommutingTransportVerified,
    RetractionVerified,
    RetractionRejected,
}

pub fn verify_transport(ds: &Matrix, dt: &Matrix, f0: &Matrix, f1: &Matrix, g: Option<(&Matrix, &Matrix)>) -> TransportStatus {
    let forward = is_zero(&sub(&matmul(f1, ds), &matmul(dt, f0)));
    if !forward {
        return TransportStatus::InvalidTransport;
    }
    match g {
        None => TransportStatus::CommutingTransportVerified,
        Some((g0, g1)) => {
            let ns = f0.first().map(|r| r.len()).unwrap_or(0);
            let ms = f1.first().map(|r| r.len()).unwrap_or(0);
            let ok = is_zero(&sub(&matmul(g1, dt), &matmul(ds, g0)))
                && is_zero(&sub(&matmul(g0, f0), &identity(ns)))
                && is_zero(&sub(&matmul(g1, f1), &identity(ms)));
            if ok {
                TransportStatus::RetractionVerified
            } else {
                TransportStatus::RetractionRejected
            }
        }
    }
}

/// A left inverse G with G F = I can exist only if F is injective. The zero map
/// out of a nonzero space is not, so no retraction exists (lossy transport).
pub fn zero_map_admits_left_inverse(f: &Matrix) -> bool {
    // G F = I with F = 0 forces I = 0, which fails whenever the source is nonzero.
    let n = f.first().map(|r| r.len()).unwrap_or(0);
    n == 0 || !is_zero(f)
}
