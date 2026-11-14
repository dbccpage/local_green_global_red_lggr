//! Commuting-square transport and chain-retraction checks on finite rational maps.
//!
//! Source C0_S --Ds--> C1_S, target C0_T --Dt--> C1_T. Forward maps F0 : C0_S -> C0_T,
//! F1 : C1_S -> C1_T with F1 Ds = Dt F0 carry repairs from source to target. A left
//! inverse chain map G (G1 Dt = Ds G0, G0 F0 = I, G1 F1 = I) also reflects
//! nonrepairability back to the source. Forward commutation alone does not.
//!
//! Every shape is checked first; ill-typed input is `InvalidTransport`, never evidence.

use crate::linear::{expect_shape, identity, is_zero, matmul, rank, shape, sub, Matrix};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TransportStatus {
    InvalidTransport,
    CommutingTransportVerified,
    RetractionVerified,
    RetractionRejected,
}

fn shapes_ok(ds: &Matrix, dt: &Matrix, f0: &Matrix, f1: &Matrix, g: Option<(&Matrix, &Matrix)>) -> Result<(), String> {
    let (ms, ns) = shape(ds)?;
    let (mt, nt) = shape(dt)?;
    expect_shape(f0, nt, ns, "F0")?;
    expect_shape(f1, mt, ms, "F1")?;
    if let Some((g0, g1)) = g {
        expect_shape(g0, ns, nt, "G0")?;
        expect_shape(g1, ms, mt, "G1")?;
    }
    Ok(())
}

pub fn verify_transport(ds: &Matrix, dt: &Matrix, f0: &Matrix, f1: &Matrix, g: Option<(&Matrix, &Matrix)>) -> TransportStatus {
    match check(ds, dt, f0, f1, g) {
        Ok(s) => s,
        Err(_) => TransportStatus::InvalidTransport,
    }
}

fn check(ds: &Matrix, dt: &Matrix, f0: &Matrix, f1: &Matrix, g: Option<(&Matrix, &Matrix)>) -> Result<TransportStatus, String> {
    shapes_ok(ds, dt, f0, f1, g)?;
    if !is_zero(&sub(&matmul(f1, ds)?, &matmul(dt, f0)?)?) {
        return Ok(TransportStatus::InvalidTransport);
    }
    let Some((g0, g1)) = g else { return Ok(TransportStatus::CommutingTransportVerified) };
    let (ns, ms) = (f0[0].len(), f1[0].len());
    let ok = is_zero(&sub(&matmul(g1, dt)?, &matmul(ds, g0)?)?)
        && is_zero(&sub(&matmul(g0, f0)?, &identity(ns))?)
        && is_zero(&sub(&matmul(g1, f1)?, &identity(ms))?);
    Ok(if ok { TransportStatus::RetractionVerified } else { TransportStatus::RetractionRejected })
}

/// A rational left inverse G with G F = I exists iff F is injective, i.e. rank F = cols F.
pub fn admits_left_inverse(f: &Matrix) -> Result<bool, String> {
    Ok(rank(f)? == shape(f)?.1)
}
