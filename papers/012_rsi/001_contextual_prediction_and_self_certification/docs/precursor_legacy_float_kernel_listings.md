# Legacy floating-point kernel listings (version 1.0.0, superseded)

**Author:** Jeremy H. Carroll\
**Status:** SUPERSEDED. Kept for the record; not part of the manuscript.

These are the Rust and Python listings that version 1.0.0 of the manuscript carried inline as its sections 7 and 8. They are reproduced byte for byte from that version, as a quotation of the superseded text, and are not maintained; the wording inside the listings, including its claim vocabulary, is the quoted version 1.0.0 wording and is not adopted by the current manuscript. An outside review of version 1.0.0 found, and the version 1.1.0 change log records, that this code decides contextuality with floating-point non-negative least squares and a residual tolerance (it returns a glued global section for a CHSH value of 2 + 4·10⁻⁸), truncates supports at a tolerance, computes kernel dimension by numerical rank, accepts a non-bijective relabeling as a gauge move, accepts a negative bit cost, and lets a step budget of 1 admit two updates. The Python listing is also broken as printed (a split identifier inside a comprehension) and the Rust listing has a broken comment.

The mechanization that the current manuscript cites instead is the exact-rational observer in the crate `omega_sheaf_theory`, module `epistemic_observer`, with its fixtures and tests, merged on the repository trunk at commit b8a84409f. See the manuscript's mechanization section and the change log.

## Rust listing as printed in version 1.0.0 (not compiled, not maintained)

```rust
//! `omega_sheaf_theory::epistemic_nogo`
//!
//! Verification kernels for the Universal Epistemic No-Go Theorem.
//!
//! Pillar I   — `evaluate_epistemic_contextuality`   (Čech / Fine / Farkas)
//! Pillar II  — `EpistemicObserver`, `BoundaryProjection`  (finite carrier, private fiber)
//! Pillar III — `EpistemicObserver::{admit, well_founded_part, self_endorse}`  (WDP-CH14-T01)
//! Pillar IV  — `verify_three_role_authority`, `authority_effect_of_prose`   (WDP-CH15)
//!
//! Dependency-free. All negative verdicts are witnessed; all uncertain
//! verdicts fail closed as `EpistemicError::Undetermined`.

#![forbid(unsafe_code)]
#![deny(missing_docs, clippy::unwrap_used, clippy::expect_used)]

use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

// ---------------------------------------------------------------------------
// §7.1  Basic types
// ---------------------------------------------------------------------------

/// Index of a question (measurement) in `0..num_questions`.
pub type QuestionId = usize;
/// An outcome of a question; must be `< arity[q]`.
pub type Outcome = u8;
/// A local section over a context, aligned with `Context::questions` order.
pub type LocalSection = Vec<Outcome>;
/// A global assignment `g : X -> O`, indexed by `QuestionId`.
pub type GlobalAssignment = Vec<Outcome>;

/// A maximal set of jointly askable questions. Stored sorted and de-duplicated.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Context {
    questions: Vec<QuestionId>,
}

impl Context {
    /// Build a context; duplicates are removed, order is canonicalised.
    pub fn new(mut questions: Vec<QuestionId>) -> Result<Self, ModelError> {
        if questions.is_empty() {
            return Err(ModelError::EmptyContext);
        }
        questions.sort_unstable();
        questions.dedup();
        Ok(Self { questions })
    }
    /// The questions of this context, ascending.
    pub fn questions(&self) -> &[QuestionId] {
        &self.questions
    }
    /// Restriction of a global assignment to this context.
    pub fn restrict(&self, g: &[Outcome]) -> LocalSection {
        self.questions.iter().map(|&q| g[q]).collect()
    }
    /// Intersection with another context (sorted).
    pub fn intersect(&self, other: &Context) -> Vec<QuestionId> {
        self.questions
            .iter()
            .copied()
            .filter(|q| other.questions.binary_search(q).is_ok())
            .collect()
    }
}

/// Errors raised while constructing an empirical model.
#[derive(Clone, Debug, PartialEq)]
pub enum ModelError {
    /// A context with no questions.
    EmptyContext,
    /// The cover is empty.
    EmptyCover,
    /// A context references a question outside `0..arity.len()`.
    QuestionOutOfRange { context: usize, question: QuestionId },
    /// The union of the cover does not equal the question set.
    CoverNotExhaustive { missing: Vec<QuestionId> },
    /// Number of distribution tables differs from number of contexts.
    TableCountMismatch { contexts: usize, tables: usize },
    /// A table key has the wrong length for its context.
    SectionLengthMismatch { context: usize, expected: usize, found: usize },
    /// A table key contains an outcome exceeding the question arity.
    OutcomeOutOfRange { context: usize, question: QuestionId, outcome: Outcome },
    /// A probability is negative, NaN, or infinite.
    InvalidProbability { context: usize, value: f64 },
    /// A table does not sum to one within tolerance.
    NotNormalised { context: usize, total: f64 },
    /// A question has arity zero.
    ZeroArity { question: QuestionId },
}

impl fmt::Display for ModelError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for ModelError {}

/// An empirical model `e_C ∈ D(S(C))` for each context `C` of a cover.
#[derive(Clone, Debug)]
pub struct EmpiricalModel {
    arity: Vec<usize>,
    cover: Vec<Context>,
    tables: Vec<BTreeMap<LocalSection, f64>>,
}

/// Normalisation tolerance for empirical tables.
pub const NORMALISATION_TOL: f64 = 1e-9;
/// Probability below which a local section is treated as outside the support.
pub const SUPPORT_TOL: f64 = 1e-12;
/// Hard cap on `|S(X)|` for exhaustive enumeration (fail closed above).
pub const MAX_GLOBAL_ASSIGNMENTS: u128 = 1 << 22;

impl EmpiricalModel {
    /// Validate and build an empirical model.
    pub fn new(
        arity: Vec<usize>,
        cover: Vec<Context>,
        tables: Vec<BTreeMap<LocalSection, f64>>,
    ) -> Result<Self, ModelError> {
        if cover.is_empty() {
            return Err(ModelError::EmptyCover);
        }
        if let Some((q, _)) = arity.iter().enumerate().find(|(_, &a)| a == 0) {
            return Err(ModelError::ZeroArity { question: q });
        }
        if cover.len() != tables.len() {
            return Err(ModelError::TableCountMismatch { contexts: cover.len(), tables: tables.len() });
        }
        let n = arity.len();
        let mut covered: BTreeSet<QuestionId> = BTreeSet::new();
        for (ci, c) in cover.iter().enumerate() {
            for &q in c.questions() {
                if q >= n {
                    return Err(ModelError::QuestionOutOfRange { context: ci, question: q });
                }
                covered.insert(q);
            }
        }
        let missing: Vec<QuestionId> = (0..n).filter(|q| !covered.contains(q)).collect();
        if !missing.is_empty() {
            return Err(ModelError::CoverNotExhaustive { missing });
        }
        for (ci, (c, t)) in cover.iter().zip(tables.iter()).enumerate() {
            let mut total = 0.0;
            for (s, &p) in t {
                if s.len() != c.questions().len() {
                    return Err(ModelError::SectionLengthMismatch {
                        context: ci,
                        expected: c.questions().len(),
                        found: s.len(),
                    });
                }
                for (k, &o) in s.iter().enumerate() {
                    let q = c.questions()[k];
                    if (o as usize) >= arity[q] {
                        return Err(ModelError::OutcomeOutOfRange { context: ci, question: q, outcome: o });
                    }
                }
                if !p.is_finite() || p < 0.0 {
                    return Err(ModelError::InvalidProbability { context: ci, value: p });
                }
                total += p;
            }
            if (total - 1.0).abs() > NORMALISATION_TOL {
                return Err(ModelError::NotNormalised { context: ci, total });
            }
        }
        Ok(Self { arity, cover, tables })
    }

    /// Outcome arities per question.
    pub fn arity(&self) -> &[usize] {
        &self.arity
    }
    /// The measurement cover.
    pub fn cover(&self) -> &[Context] {
        &self.cover
    }
    /// Number of questions.
    pub fn num_questions(&self) -> usize {
        self.arity.len()
    }
    /// Probability of a local section in a context (zero if absent).
    pub fn prob(&self, context: usize, s: &[Outcome]) -> f64 {
        self.tables[context].get(s).copied().unwrap_or(0.0)
    }
    /// Support of `e_C` (sections with probability above `SUPPORT_TOL`).
    pub fn support(&self, context: usize) -> BTreeSet<LocalSection> {
        self.tables[context]
            .iter()
            .filter(|(_, &p)| p > SUPPORT_TOL)
            .map(|(s, _)| s.clone())
            .collect()
    }

    /// Marginal of `e_C` onto a subset of its questions (sorted sub-list).
    pub fn marginal(&self, context: usize, sub: &[QuestionId]) -> BTreeMap<LocalSection, f64> {
        let c = &self.cover[context];
        let positions: Vec<usize> = sub
            .iter()
            .filter_map(|q| c.questions().iter().position(|cq| cq == q))
            .collect();
        let mut out: BTreeMap<LocalSection, f64> = BTreeMap::new();
        for (s, &p) in &self.tables[context] {
            let key: LocalSection = positions.iter().map(|&i| s[i]).collect();
            *out.entry(key).or_insert(0.0) += p;
        }
        out
    }

    /// Enumerate every local section over a context (full `S(C)`, not just support).
    pub fn all_local_sections(&self, context: usize) -> Vec<LocalSection> {
        let radices: Vec<usize> = self.cover[context].questions().iter().map(|&q| self.arity[q]).collect();
        mixed_radix(&radices)
    }

    /// `|S(X)|` as a u128 (product of arities).
    pub fn global_count(&self) -> u128 {
        self.arity.iter().fold(1u128, |acc, &a| acc.saturating_mul(a as u128))
    }

    /// Enumerate `S(X)`; fails closed if larger than `MAX_GLOBAL_ASSIGNMENTS`.
    pub fn global_assignments(&self) -> Result<Vec<GlobalAssignment>, EpistemicError> {
        let count = self.global_count();
        if count > MAX_GLOBAL_ASSIGNMENTS {
            return Err(EpistemicError::TooLarge { global_assignments: count, cap: MAX_GLOBAL_ASSIGNMENTS });
        }
        Ok(mixed_radix(&self.arity))
    }

    /// Check the compatible-family (no-disturbance) condition on all pairwise overlaps.
    pub fn check_no_disturbance(&self, tol: f64) -> Result<(), DisturbanceWitness> {
        for i in 0..self.cover.len() {
            for j in (i + 1)..self.cover.len() {
                let overlap = self.cover[i].intersect(&self.cover[j]);
                if overlap.is_empty() {
                    continue;
                }
                let mi = self.marginal(i, &overlap);
                let mj = self.marginal(j, &overlap);
                let keys: BTreeSet<&LocalSection> = mi.keys().chain(mj.keys()).collect();
                for k in keys {
                    let a = mi.get(k).copied().unwrap_or(0.0);
                    let b = mj.get(k).copied().unwrap_or(0.0);
                    if (a - b).abs() > tol {
                        return Err(DisturbanceWitness {
                            context_a: i,
                            context_b: j,
                            overlap,
                            section: k.clone(),
                            marginal_a: a,
                            marginal_b: b,
                        });
                    }
                }
            }
        }
        Ok(())
    }
}

fn mixed_radix(radices: &[usize]) -> Vec<Vec<Outcome>> {
    let total: usize = radices.iter().product();
    let mut out = Vec::with_capacity(total);
    let mut cur = vec![0u8; radices.len()];
    for _ in 0..total {
        out.push(cur.clone());
        for k in (0..radices.len()).rev() {
            cur[k] += 1;
            if (cur[k] as usize) < radices[k] {
                break;
            }
            cur[k] = 0;
        }
    }
    out
}

// ---------------------------------------------------------------------------
// §7.2  Verdict types
// ---------------------------------------------------------------------------

/// A failure of the compatible-family condition (an `Ȟ⁰`-level obstruction).
#[derive(Clone, Debug, PartialEq)]
pub struct DisturbanceWitness {
    /// First context.
    pub context_a: usize,
    /// Second context.
    pub context_b: usize,
    /// Their overlap.
    pub overlap: Vec<QuestionId>,
    /// The section on the overlap whose two marginals disagree.
    pub section: LocalSection,
    /// Marginal computed from `context_a`.
    pub marginal_a: f64,
    /// Marginal computed from `context_b`.
    pub marginal_b: f64,
}

/// Representative data for the Čech obstruction class.
#[derive(Clone, Debug, PartialEq)]
pub struct CocycleClass {
    /// Local sections in the support that admit no global extension.
    pub unextendable: Vec<(usize, LocalSection)>,
    /// Total number of local sections in all supports.
    pub total_support_sections: usize,
    /// True iff at least one local section is unextendable.
    pub logically_contextual: bool,
    /// True iff every local section is unextendable.
    pub strongly_contextual: bool,
    /// For binary models whose supports are XOR-affine and whose cover is a
    /// single cycle (each question in exactly two contexts): the `Z₂` class
    /// `⊕ bᵢ`. `Some(1)` is a non-vanishing `Ȟ¹` class; `Some(0)` vanishes;
    /// `None` means the parity shortcut does not apply.
    pub z2_cycle_class: Option<u8>,
}

/// A Farkas / generalised-Bell certificate that no global distribution exists.
#[derive(Clone, Debug, PartialEq)]
pub struct BellWitness {
    /// Row labels `(context, local_section)` matching `coefficients`.
    pub rows: Vec<(usize, LocalSection)>,
    /// Bell functional `B` such that `B·δ_g ≤ classical_bound` for every global `g`.
    pub coefficients: Vec<f64>,
    /// `max_g B·δ_g` over all deterministic models.
    pub classical_bound: f64,
    /// `B·e` for the empirical model.
    pub empirical_value: f64,
    /// `empirical_value - classical_bound` (strictly positive).
    pub violation: f64,
}

/// A global section `μ ∈ D(S(X))` marginalising to every `e_C`.
#[derive(Clone, Debug, PartialEq)]
pub struct GlobalSection {
    /// The global assignments.
    pub assignments: Vec<GlobalAssignment>,
    /// Non-negative weights, one per assignment, summing to one.
    pub weights: Vec<f64>,
    /// Maximum absolute marginalisation residual achieved.
    pub residual: f64,
}

/// The sheaf-theoretic obstruction to a global world-model.
#[derive(Clone, Debug, PartialEq)]
pub struct ContextualObstruction {
    /// Logical (possibilistic) obstruction data.
    pub cocycle_class: CocycleClass,
    /// Probabilistic obstruction (LP dual), if the LP certified it.
    pub lp_dual_witness: Option<BellWitness>,
}

/// Descent outcome in the vocabulary of `omega_category_theory::finite_report_descent`.
#[derive(Clone, Debug, PartialEq)]
pub enum DescentOutcome {
    /// The local reports glue.
    Glued(GlobalSection),
    /// The descent fiber is empty.
    NoGlobalExtension(ContextualObstruction),
}

/// All failure modes of the contextuality evaluator.
#[derive(Clone, Debug, PartialEq)]
pub enum EpistemicError {
    /// Certified contextuality: no global section exists.
    Contextual(ContextualObstruction),
    /// The local data are not even a compatible family.
    Disturbance(DisturbanceWitness),
    /// `S(X)` exceeds the enumeration cap.
    TooLarge { global_assignments: u128, cap: u128 },
    /// The solver could certify neither feasibility nor infeasibility.
    Undetermined { reason: String, best_residual: f64 },
    /// The model itself is malformed.
    Malformed(ModelError),
}

impl fmt::Display for EpistemicError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Contextual(o) => write!(
                f,
                "contextual obstruction: logical={} strong={} lp_witness={}",
                o.cocycle_class.logically_contextual,
                o.cocycle_class.strongly_contextual,
                o.lp_dual_witness.is_some()
            ),
            Self::Disturbance(w) => write!(f, "disturbance between contexts {} and {}", w.context_a, w.context_b),
            Self::TooLarge { global_assignments, cap } => write!(f, "|S(X)|={global_assignments} exceeds cap {cap}"),
            Self::Undetermined { reason, best_residual } => write!(f, "undetermined: {reason} (residual {best_residual:e})"),
            Self::Malformed(e) => write!(f, "malformed model: {e}"),
        }
    }
}
impl std::error::Error for EpistemicError {}

// ---------------------------------------------------------------------------
// §7.3  Dense linear algebra (minimal, exact enough for certification)
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
struct Dense {
    rows: usize,
    cols: usize,
    data: Vec<f64>, // row-major
}

impl Dense {
    fn zeros(rows: usize, cols: usize) -> Self {
        Self { rows, cols, data: vec![0.0; rows * cols] }
    }
    fn set(&mut self, r: usize, c: usize, v: f64) {
        self.data[r * self.cols + c] = v;
    }
    fn get(&self, r: usize, c: usize) -> f64 {
        self.data[r * self.cols + c]
    }
    fn matvec(&self, x: &[f64], out: &mut [f64]) {
        for r in 0..self.rows {
            let row = &self.data[r * self.cols..(r + 1) * self.cols];
            out[r] = row.iter().zip(x).map(|(a, b)| a * b).sum();
        }
    }
    fn matvec_t(&self, y: &[f64], out: &mut [f64]) {
        for v in out.iter_mut() {
            *v = 0.0;
        }
        for r in 0..self.rows {
            let yr = y[r];
            if yr == 0.0 {
                continue;
            }
            let row = &self.data[r * self.cols..(r + 1) * self.cols];
            for (o, a) in out.iter_mut().zip(row) {
                *o += a * yr;
            }
        }
    }
    /// Largest eigenvalue of `MᵀM` by power iteration (upper-bounded by Frobenius²).
    fn lipschitz(&self) -> f64 {
        let frob2: f64 = self.data.iter().map(|v| v * v).sum();
        if self.cols == 0 || self.rows == 0 {
            return 1.0;
        }
        let mut v = vec![1.0 / (self.cols as f64).sqrt(); self.cols];
        let mut tmp = vec![0.0; self.rows];
        let mut w = vec![0.0; self.cols];
        let mut lambda = frob2;
        for _ in 0..200 {
            self.matvec(&v, &mut tmp);
            self.matvec_t(&tmp, &mut w);
            let norm: f64 = w.iter().map(|x| x * x).sum::<f64>().sqrt();
            if norm == 0.0 {
                return 1.0;
            }
            lambda = norm;
            for (a, b) in v.iter_mut().zip(&w) {
                *a = b / norm;
            }
        }
        lambda.min(frob2).max(f64::MIN_POSITIVE)
    }
}

struct NnlsResult {
    mu: Vec<f64>,
    residual: Vec<f64>, // e - Mμ
    gradient: Vec<f64>, // Mᵀ(Mμ - e)
    kkt_gap: f64,
    converged: bool,
}

/// FISTA for `min ½‖Mμ − e‖², μ ≥ 0`, with KKT-gap stopping.
fn nnls_fista(m: &Dense, e: &[f64], max_iter: usize, kkt_tol: f64) -> NnlsResult {
    let n = m.cols;
    let step = 1.0 / (1.05 * m.lipschitz());
    let mut x = vec![0.0; n];
    let mut x_prev = vec![0.0; n];
    let mut y = vec![0.0; n];
    let mut t = 1.0_f64;
    let mut mx = vec![0.0; m.rows];
    let mut r = vec![0.0; m.rows];
    let mut g = vec![0.0; n];
    let mut best_gap = f64::INFINITY;
    let mut converged = false;

    for it in 0..max_iter {
        m.matvec(&y, &mut mx);
        for i in 0..m.rows {
            r[i] = mx[i] - e[i];
        }
        m.matvec_t(&r, &mut g);
        for k in 0..n {
            let v = y[k] - step * g[k];
            x_prev[k] = x[k];
            x[k] = if v > 0.0 { v } else { 0.0 };
        }
        let t_next = 0.5 * (1.0 + (1.0 + 4.0 * t * t).sqrt());
        let beta = (t - 1.0) / t_next;
        for k in 0..n {
            y[k] = x[k] + beta * (x[k] - x_prev[k]);
        }
        t = t_next;

        if it % 25 == 0 || it + 1 == max_iter {
            m.matvec(&x, &mut mx);
            for i in 0..m.rows {
                r[i] = mx[i] - e[i];
            }
            m.matvec_t(&r, &mut g);
            let mut gap: f64 = 0.0;
            for k in 0..n {
                gap = gap.max(-g[k]).max((x[k] * g[k]).abs());
            }
            best_gap = best_gap.min(gap);
            if gap <= kkt_tol {
                converged = true;
                break;
            }
        }
    }
    m.matvec(&x, &mut mx);
    for i in 0..m.rows {
        r[i] = mx[i] - e[i];
    }
    m.matvec_t(&r, &mut g);
    let residual: Vec<f64> = r.iter().map(|v| -v).collect();
    NnlsResult { mu: x, residual, gradient: g, kkt_gap: best_gap, converged }
}

// ---------------------------------------------------------------------------
// §7.4  Pillar I kernel — evaluate_epistemic_contextuality
// ---------------------------------------------------------------------------

/// Solver configuration.
#[derive(Clone, Debug)]
pub struct ContextualityConfig {
    /// Tolerance for the no-disturbance check.
    pub disturbance_tol: f64,
    /// Max marginalisation residual to accept a global section.
    pub feasibility_tol: f64,
    /// KKT tolerance for the NNLS solver.
    pub kkt_tol: f64,
    /// Tolerance when re-verifying the Farkas certificate.
    pub certificate_tol: f64,
    /// Maximum FISTA iterations.
    pub max_iter: usize,
}

impl Default for ContextualityConfig {
    fn default() -> Self {
        Self {
            disturbance_tol: 1e-8,
            feasibility_tol: 1e-7,
            kkt_tol: 1e-11,
            certificate_tol: 1e-9,
            max_iter: 400_000,
        }
    }
}

/// Logical (possibil

istic) contextuality via exhaustive extendability over `S(X)`.
///
/// This is the *complete* decision procedure for logical contextuality on a
/// finite model (Thm 1.2 is only a sound witness; this is sound and complete).
pub fn logical_contextuality(model: &EmpiricalModel) -> Result<CocycleClass, EpistemicError> {
    let globals = model.global_assignments()?;
    let supports: Vec<BTreeSet<LocalSection>> = (0..model.cover().len()).map(|c| model.support(c)).collect();

    // Global assignments consistent with every support.
    let consistent: Vec<&GlobalAssignment> = globals
        .iter()
        .filter(|g| {
            model
                .cover()
                .iter()
                .zip(&supports)
                .all(|(c, supp)| supp.contains(&c.restrict(g)))
        })
        .collect();

    let mut unextendable = Vec::new();
    let mut total = 0usize;
    for (ci, (c, supp)) in model.cover().iter().zip(&supports).enumerate() {
        for s in supp {
            total += 1;
            let extends = consistent.iter().any(|g| &c.restrict(g) == s);
            if !extends {
                unextendable.push((ci, s.clone()));
            }
        }
    }
    let logically_contextual = !unextendable.is_empty();
    let strongly_contextual = total > 0 && unextendable.len() == total;

    Ok(CocycleClass {
        unextendable,
        total_support_sections: total,
        logically_contextual,
        strongly_contextual,
        z2_cycle_class: z2_cycle_class(model, &supports),
    })
}

/// `Z₂` Čech class on a single-cycle binary cover with XOR-affine supports.
fn z2_cycle_class(model: &EmpiricalModel, supports: &[BTreeSet<LocalSection>]) -> Option<u8> {
    if model.arity().iter().any(|&a| a != 2) {
        return None;
    }
    let n = model.num_questions();
    let cover = model.cover();
    if cover.len() != n {
        return None;
    }
    let mut incidence = vec![0usize; n];
    let mut parity = 0u8;
    for (c, supp) in cover.iter().zip(supports) {
        if c.questions().len() != 2 || supp.len() != 2 {
            return None;
        }
        let mut b: Option<u8> = None;
        for s in supp {
            let p = s[0] ^ s[1];
            match b {
                None => b = Some(p),
                Some(q) if q != p => return None,
                _ => {}
            }
        }
        parity ^= b?;
        for &q in c.questions() {
            incidence[q] += 1;
        }
    }
    if incidence.iter().any(|&k| k != 2) {
        return None;
    }
    // Connectivity: the context graph must be one cycle.
    let mut seen = vec![false; n];
    let mut stack = vec![0usize];
    seen[0] = true;
    while let Some(q) = stack.pop() {
        for c in cover {
            if c.questions().contains(&q) {
                for &r in c.questions() {
                    if !seen[r] {
                        seen[r] = true;
                        stack.push(r);
                    }
                }
            }
        }
    }
    if seen.iter().all(|&s| s) {
        Some(parity)
    } else {
        None
    }
}

/// Build the marginalisation matrix `M` (rows `(context, local section)`,
/// columns `S(X)`) and the stacked empirical vector `e`.
fn build_lp(model: &EmpiricalModel, globals: &[GlobalAssignment]) -> (Dense, Vec<f64>, Vec<(usize, LocalSection)>) {
    let mut rows: Vec<(usize, LocalSection)> = Vec::new();
    let mut e: Vec<f64> = Vec::new();
    for ci in 0..model.cover().len() {
        for s in model.all_local_sections(ci) {
            e.push(model.prob(ci, &s));
            rows.push((ci, s));
        }
    }
    let mut m = Dense::zeros(rows.len(), globals.len());
    let mut row_index: BTreeMap<(usize, LocalSection), usize> = BTreeMap::new();
    for (r, key) in rows.iter().enumerate() {
        row_index.insert(key.clone(), r);
    }
    for (col, g) in globals.iter().enumerate() {
        for (ci, c) in model.cover().iter().enumerate() {
            if let Some(&r) = row_index.get(&(ci, c.restrict(g))) {
                m.set(r, col, 1.0);
            }
        }
    }
    (m, e, rows)
}

/// Re-verify a candidate Farkas certificate `y` *independently* of the solver.
fn certify_bell(
    m: &Dense,
    e: &[f64],
    y: &[f64],
    rows: &[(usize, LocalSection)],
    tol: f64,
) -> Option<BellWitness> {
    let mut classical_bound = f64::NEG_INFINITY;
    for col in 0..m.cols {
        let mut v = 0.0;
        for r in 0..m.rows {
            v += m.get(r, col) * y[r];
        }
        classical_bound = classical_bound.max(v);
    }
    let empirical_value: f64 = y.iter().zip(e).map(|(a, b)| a * b).sum();
    let violation = empirical_value - classical_bound;
    if violation.is_finite() && violation > tol {
        Some(BellWitness {
            rows: rows.to_vec(),
            coefficients: y.to_vec(),
            classical_bound,
            empirical_value,
            violation,
        })
    } else {
        None
    }
}

/// Decide whether an empirical model admits a global section `μ ∈ D(S(X))`.
///
/// * `Ok(GlobalSection)` — a certified non-contextual (classical) model.
/// * `Err(Contextual(..))` — certified obstruction, witnessed logically
///   (exhaustive non-extendability) and/or probabilistically (re-verified
///   Farkas / generalised-Bell functional).
/// * `Err(Disturbance(..))` — the local data are not a compatible family.
/// * `Err(Undetermined(..))` — fail closed; never a guess.
pub fn evaluate_epistemic_contextuality(
    model: &EmpiricalModel,
    config: &ContextualityConfig,
) -> Result<GlobalSection, EpistemicError> {
    if let Err(w) = model.check_no_disturbance(config.disturbance_tol) {
        return Err(EpistemicError::Disturbance(w));
    }
    let cocycle_class = logical_contextuality(model)?;
    let globals = model.global_assignments()?;
    let (m, e, rows) = build_lp(model, &globals);

    let nnls = nnls_fista(&m, &e, config.max_iter, config.kkt_tol);
    let residual_inf = nnls.residual.iter().fold(0.0_f64, |a, &v| a.max(v.abs()));

    if residual_inf <= config.feasibility_tol && !cocycle_class.logically_contextual {
        let mut assignments = Vec::new();
        let mut weights = Vec::new();
        for (g, &w) in globals.iter().zip(&nnls.mu) {
            if w > SUPPORT_TOL {
                assignments.push(g.clone());
                weights.push(w);
            }
        }
        let total: f64 = weights.iter().sum();
        if total <= 0.0 {
            return Err(EpistemicError::Undetermined {
                reason: "feasible residual but empty support".into(),
                best_residual: residual_inf,
            });
        }
        for w in &mut weights {
            *w /= total;
        }
        return Ok(GlobalSection { assignments, weights, residual: residual_inf });
    }

    // Farkas: y = e − Mμ* is a separating functional for the cone {Mμ : μ ≥ 0}.
    let lp_dual_witness = certify_bell(&m, &e, &nnls.residual, &rows, config.certificate_tol);

    if cocycle_class.logically_contextual || lp_dual_witness.is_some() {
        return Err(EpistemicError::Contextual(ContextualObstruction { cocycle_class, lp_dual_witness }));
    }
    Err(EpistemicError::Undetermined {
        reason: format!(
            "neither feasibility (residual {residual_inf:e}) nor a certificate; kkt_gap={:e}, converged={}",
            nnls.kkt_gap, nnls.converged
        ),
        best_residual: residual_inf,
    })
}

/// The same verdict in the `finite_report_descent` vocabulary.
pub fn descend(model: &EmpiricalModel, config: &ContextualityConfig) -> Result<DescentOutcome, EpistemicError> {
    match evaluate_epistemic_contextuality(model, config) {
        Ok(s) => Ok(DescentOutcome::Glued(s)),
        Err(EpistemicError::Contextual(o)) => Ok(DescentOutcome::NoGlobalExtension(o)),
        Err(other) => Err(other),
    }
}

// ---------------------------------------------------------------------------
// §7.5  Pillar II — BoundaryProjection and EpistemicObserver
// ---------------------------------------------------------------------------

/// Errors in constructing an embodied interface.
#[derive(Clone, Debug, PartialEq)]
pub enum FiberError {
    /// `ker π = 0`: the interface exposes the whole internal state (violates P2).
    TrivialFiber { internal_dim: usize, rank: usize },
    /// Matrix dimensions inconsistent with the data length.
    ShapeMismatch { rows: usize, cols: usize, len: usize },
    /// Zero-dimensional internal state.
    EmptyState,
}

impl fmt::Display for FiberError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for FiberError {}

/// Pivot tolerance for rank computations.
pub const RANK_TOL: f64 = 1e-10;

/// A linear boundary projection `π : X_O → Y_O` with a certified non-trivial kernel.
#[derive(Clone, Debug, PartialEq)]
pub struct BoundaryProjection {
    boundary_dim: usize,
    internal_dim: usize,
    matrix: Vec<f64>, // row-major boundary_dim × internal_dim
    rank: usize,
    kernel_basis: Vec<Vec<f64>>,
}

impl BoundaryProjection {
    /// Construct and certify `dim ker π > 0`.
    pub fn new(boundary_dim: usize, internal_dim: usize, matrix: Vec<f64>) -> Result<Self, FiberError> {
        if internal_dim == 0 {
            return Err(FiberError::EmptyState);
        }
        if matrix.len() != boundary_dim * internal_dim {
            return Err(FiberError::ShapeMismatch { rows: boundary_dim, cols: internal_dim, len: matrix.len() });
        }
        let (rank, kernel_basis) = rref_kernel(boundary_dim, internal_dim, &matrix);
        if kernel_basis.is_empty() {
            return Err(FiberError::TrivialFiber { internal_dim, rank });
        }
        Ok(Self { boundary_dim, internal_dim, matrix, rank, kernel_basis })
    }
    /// `dim ker π`.
    pub fn fiber_dim(&self) -> usize {
        self.kernel_basis.len()
    }
    /// Rank of `π`.
    pub fn rank(&self) -> usize {
        self.rank
    }
    /// Internal state dimension.
    pub fn internal_dim(&self) -> usize {
        self.internal_dim
    }
    /// Boundary dimension.
    pub fn boundary_dim(&self) -> usize {
        self.boundary_dim
    }
    /// A basis of the private fiber.
    pub fn kernel_basis(&self) -> &[Vec<f64>] {
        &self.kernel_basis
    }
    /// Apply `π`.
    pub fn apply(&self, x: &[f64]) -> Vec<f64> {
        (0..self.boundary_dim)
            .map(|r| {
                let row = &self.matrix[r * self.internal_dim..(r + 1) * self.internal_dim];
                row.iter().zip(x).map(|(a, b)| a * b).sum()
            })
            .collect()
    }
}

/// Reduced row echelon form; returns `(rank, kernel basis)`.
fn rref_kernel(rows: usize, cols: usize, data: &[f64]) -> (usize, Vec<Vec<f64>>) {
    let mut a: Vec<Vec<f64>> = (0..rows).map(|r| data[r * cols..(r + 1) * cols].to_vec()).collect();
    let mut pivot_cols: Vec<usize> = Vec::new();
    let mut r = 0usize;
    for c in 0..cols {
        if r >= rows {
            break;
        }
        let (mut best, mut best_val) = (r, a[r][c].abs());
        for i in (r + 1)..rows {
            if a[i][c].abs() > best_val {
                best = i;
                best_val = a[i][c].abs();
            }
        }
        if best_val <= RANK_TOL {
            continue;
        }
        a.swap(r, best);
        let p = a[r][c];
        for v in a[r].iter_mut() {
            *v /= p;
        }
        for i in 0..rows {
            if i != r && a[i][c].abs() > 0.0 {
                let f = a[i][c];
                for k in 0..cols {
                    a[i][k] -= f * a[r][k];
                }
            }
        }
        pivot_cols.push(c);
        r += 1;
    }
    let rank = pivot_cols.len();
    let mut basis = Vec::new();
    for free in 0..cols {
        if pivot_cols.contains(&free) {
            continue;
        }
        let mut v = vec![0.0; cols];
        v[free] = 1.0;
        for (pi, &pc) in pivot_cols.iter().enumerate() {
            v[pc] = -a[pi][free];
        }
        basis.push(v);
    }
    (rank, basis)
}

/// `AuthorityEffect` — the only type through which operational standing flows.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum AuthorityEffect {
    /// No operational standing whatsoever.
    None,
    /// Standing granted by an external root, bounded to a scope and jurisdiction.
    Granted {
        /// The root of trust that signed.
        root: Principal,
        /// Jurisdiction `J`.
        jurisdiction: String,
        /// Permitted actions.
        scope: BTreeSet<String>,
    },
}

/// A named principal (observer, institution, key holder).
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Principal(pub String);

/// Errors in carrier operations.
#[derive(Clone, Debug, PartialEq)]
pub enum CarrierError {
    /// The finite carrier is full (P1).
    CapacityExceeded { capacity_bits: u64, used_bits: u64, requested_bits: u64 },
    /// Duplicate identifier.
    Duplicate(u64),
    /// The cited ground datum was never admitted.
    UnknownGround(u64),
    /// Boundary input has the wrong dimension.
    BoundaryDimMismatch { expected: usize, found: usize },
}

impl fmt::Display for CarrierError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for CarrierError {}

/// An admitted instance in the carrier.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Instance {
    /// Identifier.
    pub id: u64,
    /// External ground datum, if any (`None` ⇒ `supply_no_op`).
    pub ground: Option<u64>,
    /// Bits consumed in the carrier.
    pub bits: u64,
}

/// Termination discipline `Term`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Termination {
    /// Hard bound on enactive steps.
    pub max_steps: u64,
    /// Steps taken so far.
    pub steps: u64,
}

/// The 5-tuple `(K, Adm, ‖·‖, Term, 𝓛)` with an explicit private fiber.
#[derive(Clone, Debug, PartialEq)]
pub struct EpistemicObserver {
    /// Principal identity.
    pub name: Principal,
    /// Carrier capacity in bits (Bekenstein/Landauer bound stand-in).
    pub capacity_bits: u64,
    carrier: BTreeMap<u64, Instance>,
    grounds: BTreeSet<u64>,
    used_bits: u64,
    projection: BoundaryProjection,
    state: Vec<f64>,
    /// Termination discipline.
    pub term: Termination,
    language: BTreeSet<String>,
    /// Meta-carrier level `n` of `K_n`.
    pub level: u32,
}

impl EpistemicObserver {
    /// Construct an observer; the projection must already certify `ker π ≠ 0`.
    pub fn new(name: &str, capacity_bits: u64, projection: BoundaryProjection, max_steps: u64) -> Self {
        let n = projection.internal_dim();
        Self {
            name: Principal(name.to_string()),
            capacity_bits,
            carrier: BTreeMap::new(),
            grounds: BTreeSet::new(),
            used_bits: 0,
            projection,
            state: vec![0.0; n],
            term: Termination { max_steps, steps: 0 },
            language: BTreeSet::new(),
            level: 0,
        }
    }

    /// The boundary projection.
    pub fn projection(&self) -> &BoundaryProjection {
        &self.projection
    }
    /// Internal state (for tests only; not reachable across the boundary).
    pub fn internal_state(&self) -> &[f64] {
        &self.state
    }
    /// Bits consumed.
    pub fn used_bits(&self) -> u64 {
        self.used_bits
    }

    fn charge(&mut self, bits: u64) -> Result<(), CarrierError> {
        if self.used_bits.saturating_add(bits) > self.capacity_bits {
            return Err(CarrierError::CapacityExceeded {
                capacity_bits: self.capacity_bits,
                used_bits: self.used_bits,
                requested_bits: bits,
            });
        }
        self.used_bits += bits;
        Ok(())
    }

    /// Axis 1: admit an *external* ground datum (`x < r.data`).
    pub fn admit_ground(&mut self, datum_id: u64, bits: u64) -> Result<(), CarrierError> {
        if self.grounds.contains(&datum_id) {
            return Err(CarrierError::Duplicate(datum_id));
        }
        self.charge(bits)?;
        self.grounds.insert(datum_id);
        Ok(())
    }

    /// Assert an instance. `ground = None` is a `supply_no_op`: it enters the
    /// carrier but never the well-founded part.
    pub fn assert_instance(&mut self, id: u64, ground: Option<u64>, bits: u64) -> Result<(), CarrierError> {
        if self.carrier.contains_key(&id) {
            return Err(CarrierError::Duplicate(id));
        }
        if let Some(g) = ground {
            if !self.grounds.contains(&g) {
                return Err(CarrierError::UnknownGround(g));
            }
        }
        self.charge(bits)?;
        self.carrier.insert(id, Instance { id, ground, bits });
        self.language.insert(format!("inst:{id}"));
        Ok(())
    }

    /// The well-founded part of the carrier: instances anchored in admitted ground.
    pub fn well_founded_part(&self) -> BTreeSet<u64> {
        self.carrier.values().filter(|i| i.ground.is_some()).map(|i| i.id).collect()
    }

    /// `collapsed_of_no_insts`: non-empty carrier with empty well-founded part.
    pub fn is_collapsed(&self) -> bool {
        !self.carrier.is_empty() && self.well_founded_part().is_empty()
    }

    /// Axis 3: `Q¹` defects = ungrounded instances (gauge-invariant data).
    pub fn quotient_defects(&self) -> usize {
        self.carrier.values().filter(|i| i.ground.is_none()).count()
    }

    /// Axis 3: a zero-charge presentation relabeling of instance identifiers.
    /// Returns the relabeled observer and the passage charge (always 0).
    pub fn gauge_relabel(&self, relabel: &BTreeMap<u64, u64>) -> (Self, u64) {
        let mut out = self.clone();
        out.carrier = self
            .carrier
            .values()
            .map(|i| {
                let id = *relabel.get(&i.id).unwrap_or(&i.id);
                (id, Instance { id, ground: i.ground, bits: i.bits })
            })
            .collect();
        out.language = out.carrier.keys().map(|id| format!("inst:{id}")).collect();
        (out, 0)
    }

    /// Axis 2: self-endorsement inside `K_n`. Always `AuthorityEffect::None`
    /// (ENC-0195); records the claim in `𝓛` so the assertion is visible.
    pub fn self_endorse(&mut self, claim: &str) -> AuthorityEffect {
        self.language.insert(format!("endorse:{claim}"));
        AuthorityEffect::None
    }

    /// Axis 2: the level at which carrier `K_n` can be verified is `n+1`.
    pub fn verification_level_required(&self) -> u32 {
        self.level + 1
    }

    /// Ascend the tower: construct `K_{n+1}` as an observer able to evaluate
    /// this one. Its own soundness is again unverified at its level.
    pub fn ascend(&self) -> Self {
        let mut next = self.clone();
        next.level = self.level + 1;
        next.name = Principal(format!("{}+Con", self.name.0));
        next
    }

    /// 4E enactive loop: perceive boundary input, update internal state
    /// (including the fiber component, which evolves without ever being emitted).
    pub fn enact(&mut self, boundary_input: &[f64]) -> Result<Vec<f64>, CarrierError> {
        let m = self.projection.boundary_dim();
        if boundary_input.len() != m {
            return Err(CarrierError::BoundaryDimMismatch { expected: m, found: boundary_input.len() });
        }
        self.term.steps += 1;
        let n = self.projection.internal_dim();
        let mut next = vec![0.0; n];
        for i in 0..n {
            let drive: f64 = boundary_input.iter().enumerate().map(|(j, &b)| b * (((i + j) % 3) as f64 + 1.0) * 0.1).sum();
            next[i] = (0.9 * self.state[i] + drive + 0.05 * self.state[(i + 1) % n]).tanh();
        }
        self.state = next;
        Ok(self.observe())
    }

    /// `π_O(x)`: the only thing another observer can ever see.
    pub fn observe(&self) -> Vec<f64> {
        self.projection.apply(&self.state)
    }

    /// Perturb the internal state along the private fiber (test hook for Prop 2.4).
    pub fn perturb_along_fiber(&mut self, basis_index: usize, amount: f64) {
        if let Some(v) = self.projection.kernel_basis().get(basis_index) {
            for (s, k) in self.state.iter_mut().zip(v) {
                *s += amount * k;
            }
        }
    }

    /// Set the internal state directly (test hook).
    pub fn set_internal_state(&mut self, s: Vec<f64>) {
        if s.len() == self.state.len() {
            self.state = s;
        }
    }

    /// The declared language `𝓛`.
    pub fn language(&self) -> &BTreeSet<String> {
        &self.language
    }
}

/// `τ₁₂ = τ̄₁₂ ∘ (π₁ × π₂)`: the only cross-observer interaction that exists.
pub fn interact(a: &EpistemicObserver, b: &EpistemicObserver) -> Vec<f64> {
    let ya = a.observe();
    let yb = b.observe();
    let mut out = Vec::with_capacity(ya.len() * yb.len());
    for p in &ya {
        for q in &yb {
            out.push(p * q);
        }
    }
    out
}

// ---------------------------------------------------------------------------
// §7.6  Pillar IV — Typed receipts, roots of trust, three-role firewall
// ---------------------------------------------------------------------------

/// SipHash-2-4 keyed hash (the MAC primitive behind `SigningKey`).
fn siphash24(k0: u64, k1: u64, msg: &[u8]) -> u64 {
    #[inline]
    fn rotl(x: u64, b: u32) -> u64 {
        x.rotate_left(b)
    }
    #[inline]
    fn round(v: &mut [u64; 4]) {
        v[0] = v[0].wrapping_add(v[1]);
        v[1] = rotl(v[1], 13);
        v[1] ^= v[0];
        v[0] = rotl(v[0], 32);
        v[2] = v[2].wrapping_add(v[3]);
        v[3] = rotl(v[3], 16);
        v[3] ^= v[2];
        v[0] = v[0].wrapping_add(v[3]);
        v[3] = rotl(v[3], 21);
        v[3] ^= v[0];
        v[2] = v[2].wrapping_add(v[1]);
        v[1] = rotl(v[1], 17);
        v[1] ^= v[2];
        v[2] = rotl(v[2], 32);
    }
    let mut v = [
        k0 ^ 0x736f_6d65_7073_6575,
        k1 ^ 0x646f_7261_6e64_6f6d,
        k0 ^ 0x6c79_6765_6e65_7261,
        k1 ^ 0x7465_6462_7974_6573,
    ];
    let mut chunks = msg.chunks_exact(8);
    for c in &mut chunks {
        let mut buf = [0u8; 8];
        buf.copy_from_slice(c);
        let m = u64::from_le_bytes(buf);
        v[3] ^= m;
        round(&mut v);
        round(&mut v);
        v[0] ^= m;
    }
    let rem = chunks.remainder();
    let mut last = (msg.len() as u64) << 56;
    for (i, &b) in rem.iter().enumerate() {
        last |= (b as u64) << (8 * i);
    }
    v[3] ^= last;
    round(&mut v);
    round(&mut v);
    v[0] ^= last;
    v[2] ^= 0xff;
    for _ in 0..4 {
        round(&mut v);
    }
    v[0] ^ v[1] ^ v[2] ^ v[3]
}

/// A 128-bit authentication tag.
pub type Tag = [u64; 2];

/// A root-of-trust signing key (symmetric MAC; held only by the root).
#[derive(Clone)]
pub struct SigningKey {
    k0: u64,
    k1: u64,
}

impl fmt::Debug for SigningKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "SigningKey(<redacted>)")
    }
}

impl SigningKey {
    /// Create a key from 128 bits of secret material.
    pub fn new(k0: u64, k1: u64) -> Self {
        Self { k0, k1 }
    }
    /// Produce a tag over a message.
    pub fn tag(&self, msg: &[u8]) -> Tag {
        [
            siphash24(self.k0, self.k1, msg),
            siphash24(self.k0 ^ 0xa5a5_a5a5_a5a5_a5a5, self.k1 ^ 0x5a5a_5a5a_5a5a_5a5a, msg),
        ]
    }
    /// Constant-time verification.
    pub fn verify(&self, msg: &[u8], tag: &Tag) -> bool {
        let t = self.tag(msg);
        let mut acc: u64 = 0;
        for i in 0..2 {
            acc |= t[i] ^ tag[i];
        }
        acc == 0
    }
}

/// The three-role provenance triple `π = (P, E, A)`.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ProvenanceTriple {
    /// Proposer.
    pub proposer: Principal,
    /// Evaluator.
    pub evaluator: Principal,
    /// Authorizer.
    pub authorizer: Principal,
}

impl ProvenanceTriple {
    /// `PairwiseDistinct(P, E, A)`.
    pub fn pairwise_distinct(&self) -> bool {
        self.proposer != self.evaluator && self.evaluator != self.authorizer && self.proposer != self.authorizer
    }
}

/// `WDP-CH15-D01`: an authority packet `𝔄 = (R, J, Perm, Proc, Appeal)`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AuthorityPacket {
    /// Root of trust.
    pub root: Principal,
    /// Jurisdiction.
    pub jurisdiction: String,
    /// Permissions the root may delegate.
    pub permissions: BTreeSet<String>,
    /// Procedure identifier.
    pub procedure: String,
    /// Appeal channel identifier.
    pub appeal: String,
}

/// `WDP-CH15-D02`: a typed machine receipt bound to a root of trust.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Receipt {
    /// Provenance it certifies.
    pub triple: ProvenanceTriple,
    /// Root that signed.
    pub root: Principal,
    /// Jurisdiction.
    pub jurisdiction: String,
    /// Scope granted.
    pub scope: BTreeSet<String>,
    /// Anti-replay nonce.
    pub nonce: u64,
    /// Expiry (monotone clock units).
    pub expires_at: u64,
    /// MAC over the canonical encoding.
    pub tag: Tag,
}

fn put_str(buf: &mut Vec<u8>, s: &str) {
    buf.extend_from_slice(&(s.len() as u64).to_le_bytes());
    buf.extend_from_slice(s.as_bytes());
}

impl Receipt {
    /// Canonical byte encoding of the signed fields.
    pub fn canonical_bytes(&self) -> Vec<u8> {
        let mut b = Vec::new();
        put_str(&mut b, "WDP-CH15-D02/receipt/v1");
        put_str(&mut b, &self.triple.proposer.0);
        put_str(&mut b, &self.triple.evaluator.0);
        put_str(&mut b, &self.triple.authorizer.0);
        put_str(&mut b, &self.root.0);
        put_str(&mut b, &self.jurisdiction);
        b.extend_from_slice(&(self.scope.len() as u64).to_le_bytes());
        for s in &self.scope {
            put_str(&mut b, s);
        }
        b.extend_from_slice(&self.nonce.to_le_bytes());
        b.extend_from_slice(&self.expires_at.to_le_bytes());
        b
    }

    /// Issue a receipt; only the root (key holder) can do this.
    pub fn issue(
        key: &SigningKey,
        triple: ProvenanceTriple,
        root: Principal,
        jurisdiction: &str,
        scope: BTreeSet<String>,
        nonce: u64,
        expires_at: u64,
    ) -> Self {
        let mut r = Self {
            triple,
            root,
            jurisdiction: jurisdiction.to_string(),
            scope,
            nonce,
            expires_at,
            tag: [0, 0],
        };
        r.tag = key.tag(&r.canonical_bytes());
        r
    }
}

/// Registry of admitted roots of trust and their verification keys.
#[derive(Clone, Debug, Default)]
pub struct RootRegistry {
    keys: BTreeMap<Principal, SigningKey>,
    seen_nonces: BTreeSet<(Principal, u64)>,
}

impl RootRegistry {
    /// Admit a root.
    pub fn admit_root(&mut self, root: Principal, key: SigningKey) {
        self.keys.insert(root, key);
    }
    /// Look up a root's key.
    pub fn key_of(&self, root: &Principal) -> Option<&SigningKey> {
        self.keys.get(root)
    }
    /// Record a nonce; returns `false` on replay.
    pub fn consume_nonce(&mut self, root: &Principal, nonce: u64) -> bool {
        self.seen_nonces.insert((root.clone(), nonce))
    }
}

/// Every way authority can be refused. Ordered by check precedence.
#[

derive(Clone, Debug, PartialEq, Eq)]
pub enum AuthorityRefusal {
    /// `P = A`, `E = A`, or `P = E`: self-authorization (Prop 4.3). Checked first,
    /// before any key is touched, so a forged signature can never mask it.
    RefuseSelfAuthorization {
        /// Which roles collided.
        collision: &'static str,
        /// The offending triple.
        triple: ProvenanceTriple,
    },
    /// The presented triple is not the one the receipt certifies.
    RefuseTripleMismatch,
    /// The root of trust is itself the proposer or evaluator (`R ∈ {P, E}`).
    RefuseRootIsParty { root: Principal },
    /// The authorizer's key does not chain to the receipt's root.
    RefuseAuthorizerNotChainedToRoot { authorizer: Principal, root: Principal },
    /// The root is not admitted in the registry (no external anchor).
    RefuseUnknownRoot { root: Principal },
    /// The receipt's root differs from the packet's root.
    RefusePacketRootMismatch,
    /// The receipt's jurisdiction is not the packet's jurisdiction `J`.
    RefuseJurisdictionMismatch { packet: String, receipt: String },
    /// The receipt grants something the root may not delegate (`scope ⊄ Perm`).
    RefuseScopeNotPermitted { excess: BTreeSet<String> },
    /// The requested action is outside the granted scope.
    RefuseActionOutOfScope { action: String },
    /// MAC verification failed.
    RefuseBadSignature,
    /// The receipt has expired.
    RefuseExpired { expires_at: u64, now: u64 },
    /// The nonce was already consumed.
    RefuseReplay { nonce: u64 },
}

impl fmt::Display for AuthorityRefusal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for AuthorityRefusal {}

/// `WDP-CH15-P04`: prose has `AuthorityEffect = None`. The text is not parsed,
/// not scored, and not inspected for keywords; it is simply outside the domain
/// of `AuthorityEffect`. This is the only correct implementation.
pub fn authority_effect_of_prose(_text: &str) -> AuthorityEffect {
    AuthorityEffect::None
}

/// The three-role authority firewall.
///
/// Returns `AuthorityEffect::Granted` only if *every* check passes. Checks run
/// in declared precedence; the role-separation check runs first and
/// short-circuits, so no cryptographic material is ever consulted for a
/// self-signed packet. The nonce is consumed last, so a refused receipt does
/// not burn its nonce.
pub fn verify_three_role_authority(
    registry: &mut RootRegistry,
    packet: &AuthorityPacket,
    presented: &ProvenanceTriple,
    receipt: &Receipt,
    requested_action: &str,
    now: u64,
) -> Result<AuthorityEffect, AuthorityRefusal> {
    // 1. Three-role separation (fail closed, before anything else).
    let t = presented;
    if t.proposer == t.authorizer {
        return Err(AuthorityRefusal::RefuseSelfAuthorization { collision: "proposer == authorizer", triple: t.clone() });
    }
    if t.evaluator == t.authorizer {
        return Err(AuthorityRefusal::RefuseSelfAuthorization { collision: "evaluator == authorizer", triple: t.clone() });
    }
    if t.proposer == t.evaluator {
        return Err(AuthorityRefusal::RefuseSelfAuthorization { collision: "proposer == evaluator", triple: t.clone() });
    }
    debug_assert!(t.pairwise_distinct());

    // 2. The receipt must certify exactly this triple.
    if &receipt.triple != presented {
        return Err(AuthorityRefusal::RefuseTripleMismatch);
    }

    // 3. External root: R ∉ {P, E}.
    if receipt.root == t.proposer || receipt.root == t.evaluator {
        return Err(AuthorityRefusal::RefuseRootIsParty { root: receipt.root.clone() });
    }

    // 4. The authorizer must chain to the root (direct chain in this kernel).
    if t.authorizer != receipt.root {
        return Err(AuthorityRefusal::RefuseAuthorizerNotChainedToRoot {
            authorizer: t.authorizer.clone(),
            root: receipt.root.clone(),
        });
    }

    // 5. Root must be admitted.
    let key = match registry.key_of(&receipt.root) {
        Some(k) => k.clone(),
        None => return Err(AuthorityRefusal::RefuseUnknownRoot { root: receipt.root.clone() }),
    };

    // 6. Packet binding: root and jurisdiction.
    if packet.root != receipt.root {
        return Err(AuthorityRefusal::RefusePacketRootMismatch);
    }
    if packet.jurisdiction != receipt.jurisdiction {
        return Err(AuthorityRefusal::RefuseJurisdictionMismatch {
            packet: packet.jurisdiction.clone(),
            receipt: receipt.jurisdiction.clone(),
        });
    }

    // 7. Scope ⊆ Perm, and the action ∈ scope.
    let excess: BTreeSet<String> = receipt.scope.difference(&packet.permissions).cloned().collect();
    if !excess.is_empty() {
        return Err(AuthorityRefusal::RefuseScopeNotPermitted { excess });
    }
    if !receipt.scope.contains(requested_action) {
        return Err(AuthorityRefusal::RefuseActionOutOfScope { action: requested_action.to_string() });
    }

    // 8. Signature.
    if !key.verify(&receipt.canonical_bytes(), &receipt.tag) {
        return Err(AuthorityRefusal::RefuseBadSignature);
    }

    // 9. Expiry.
    if now > receipt.expires_at {
        return Err(AuthorityRefusal::RefuseExpired { expires_at: receipt.expires_at, now });
    }

    // 10. Replay (consumed last).
    if !registry.consume_nonce(&receipt.root, receipt.nonce) {
        return Err(AuthorityRefusal::RefuseReplay { nonce: receipt.nonce });
    }

    Ok(AuthorityEffect::Granted {
        root: receipt.root.clone(),
        jurisdiction: receipt.jurisdiction.clone(),
        scope: receipt.scope.clone(),
    })
}

// ---------------------------------------------------------------------------
// §7.7  Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
#[allow(clippy::unwrap_used, clippy::expect_used)]
mod tests {
    use super::*;

    // ---- helpers ----------------------------------------------------------

    fn ctx(q: &[usize]) -> Context {
        Context::new(q.to_vec()).unwrap()
    }

    fn table(entries: &[(&[u8], f64)]) -> BTreeMap<LocalSection, f64> {
        entries.iter().map(|(s, p)| (s.to_vec(), *p)).collect()
    }

    /// CHSH scenario: a=0, a'=1, b=2, b'=3.
    fn chsh_cover() -> Vec<Context> {
        vec![ctx(&[0, 2]), ctx(&[0, 3]), ctx(&[1, 2]), ctx(&[1, 3])]
    }

    fn correlated(p_same: f64) -> BTreeMap<LocalSection, f64> {
        let d = (1.0 - p_same) / 2.0;
        let s = p_same / 2.0;
        table(&[(&[0, 0], s), (&[1, 1], s), (&[0, 1], d), (&[1, 0], d)])
    }

    fn pr_box() -> EmpiricalModel {
        EmpiricalModel::new(
            vec![2, 2, 2, 2],
            chsh_cover(),
            vec![correlated(1.0), correlated(1.0), correlated(1.0), correlated(0.0)],
        )
        .unwrap()
    }

    fn tsirelson_box() -> EmpiricalModel {
        let e = std::f64::consts::FRAC_1_SQRT_2;
        let same = (1.0 + e) / 2.0;
        let diff = (1.0 - e) / 2.0;
        EmpiricalModel::new(
            vec![2, 2, 2, 2],
            chsh_cover(),
            vec![correlated(same), correlated(same), correlated(same), correlated(diff)],
        )
        .unwrap()
    }

    fn classical_box() -> EmpiricalModel {
        EmpiricalModel::new(
            vec![2, 2, 2, 2],
            chsh_cover(),
            vec![correlated(1.0), correlated(1.0), correlated(1.0), correlated(1.0)],
        )
        .unwrap()
    }

    fn projection_1_of_3() -> BoundaryProjection {
        // π(x₀,x₁,x₂) = x₀ + x₁ ; ker π = span{(1,-1,0),(0,0,1)}
        BoundaryProjection::new(1, 3, vec![1.0, 1.0, 0.0]).unwrap()
    }

    // ---- Pillar I ---------------------------------------------------------

    #[test]
    fn pr_box_is_strongly_contextual_with_z2_class_one() {
        let cc = logical_contextuality(&pr_box()).unwrap();
        assert!(cc.logically_contextual);
        assert!(cc.strongly_contextual);
        assert_eq!(cc.total_support_sections, 8);
        assert_eq!(cc.unextendable.len(), 8);
        assert_eq!(cc.z2_cycle_class, Some(1), "Ȟ¹ parity cocycle must not vanish");
    }

    #[test]
    fn pr_box_descent_fiber_is_empty_with_farkas_certificate() {
        let out = descend(&pr_box(), &ContextualityConfig::default()).unwrap();
        match out {
            DescentOutcome::NoGlobalExtension(obs) => {
                assert!(obs.cocycle_class.strongly_contextual);
                let w = obs.lp_dual_witness.expect("PR box must carry an LP dual witness");
                assert!(w.violation > 0.0);
                assert!(w.empirical_value > w.classical_bound);
                // Independently re-check the certificate against every deterministic model.
                let model = pr_box();
                let globals = model.global_assignments().unwrap();
                for g in &globals {
                    let mut v = 0.0;
                    for ((ci, s), &y) in w.rows.iter().zip(&w.coefficients) {
                        if model.cover()[*ci].restrict(g) == *s {
                            v += y;
                        }
                    }
                    assert!(v <= w.classical_bound + 1e-9);
                }
            }
            DescentOutcome::Glued(_) => panic!("PR box glued: impossible"),
        }
    }

    #[test]
    fn tsirelson_box_is_probabilistically_but_not_logically_contextual() {
        let model = tsirelson_box();
        assert!(model.check_no_disturbance(1e-9).is_ok());
        let cc = logical_contextuality(&model).unwrap();
        assert!(!cc.logically_contextual, "full supports: γ = 0 over Z");
        assert_eq!(cc.z2_cycle_class, None);
        match evaluate_epistemic_contextuality(&model, &ContextualityConfig::default()) {
            Err(EpistemicError::Contextual(obs)) => {
                let w = obs.lp_dual_witness.expect("CHSH at Tsirelson bound needs a Bell witness");
                assert!(w.violation > 1e-6, "violation {}", w.violation);
            }
            other => panic!("expected Contextual, got {other:?}"),
        }
    }

    #[test]
    fn classical_box_glues_to_a_global_section() {
        let model = classical_box();
        let s = evaluate_epistemic_contextuality(&model, &ContextualityConfig::default()).unwrap();
        assert!(s.residual <= 1e-7);
        let total: f64 = s.weights.iter().sum();
        assert!((total - 1.0).abs() < 1e-9);
        // Every supported global assignment must be all-equal (0000 or 1111).
        for g in &s.assignments {
            assert!(g.iter().all(|&o| o == g[0]));
        }
        assert!(matches!(descend(&model, &ContextualityConfig::default()).unwrap(), DescentOutcome::Glued(_)));
    }

    #[test]
    fn disturbing_family_is_rejected_at_h0() {
        // Context {0,2} says a is uniform; context {0,3} says a is always 0.
        let model = EmpiricalModel::new(
            vec![2, 2, 2, 2],
            chsh_cover(),
            vec![
                correlated(1.0),
                table(&[(&[0, 0], 0.5), (&[0, 1], 0.5)]),
                correlated(1.0),
                correlated(1.0),
            ],
        )
        .unwrap();
        match evaluate_epistemic_contextuality(&model, &ContextualityConfig::default()) {
            Err(EpistemicError::Disturbance(w)) => {
                assert_eq!(w.overlap, vec![0]);
                assert!((w.marginal_a - w.marginal_b).abs() > 1e-6);
            }
            other => panic!("expected Disturbance, got {other:?}"),
        }
    }

    #[test]
    fn model_validation_fails_closed() {
        assert_eq!(
            EmpiricalModel::new(vec![2, 2], vec![ctx(&[0])], vec![table(&[(&[0], 1.0)])]).err(),
            Some(ModelError::CoverNotExhaustive { missing: vec![1] })
        );
        assert!(matches!(
            EmpiricalModel::new(vec![2], vec![ctx(&[0])], vec![table(&[(&[0], 0.7)])]).err(),
            Some(ModelError::NotNormalised { .. })
        ));
        assert!(matches!(
            EmpiricalModel::new(vec![2], vec![ctx(&[0])], vec![table(&[(&[3], 1.0)])]).err(),
            Some(ModelError::OutcomeOutOfRange { .. })
        ));
    }

    #[test]
    fn oversized_models_fail_closed_rather_than_guess() {
        let n = 23usize; // 2^23 > MAX_GLOBAL_ASSIGNMENTS
        let cover: Vec<Context> = (0..n).map(|q| ctx(&[q])).collect();
        let tables: Vec<_> = (0..n).map(|_| table(&[(&[0], 0.5), (&[1], 0.5)])).collect();
        let model = EmpiricalModel::new(vec![2; n], cover, tables).unwrap();
        assert!(matches!(
            evaluate_epistemic_contextuality(&model, &ContextualityConfig::default()),
            Err(EpistemicError::TooLarge { .. })
        ));
    }

    // ---- Pillar II --------------------------------------------------------

    #[test]
    fn trivial_fiber_violates_p2_and_is_refused() {
        let err = BoundaryProjection::new(2, 2, vec![1.0, 0.0, 0.0, 1.0]).err().unwrap();
        assert_eq!(err, FiberError::TrivialFiber { internal_dim: 2, rank: 2 });
    }

    #[test]
    fn private_fiber_is_opaque_to_every_boundary_observation() {
        let mut a = EpistemicObserver::new("A", 1 << 20, projection_1_of_3(), 1000);
        let b = EpistemicObserver::new("B", 1 << 20, projection_1_of_3(), 1000);
        assert_eq!(a.projection().fiber_dim(), 2);
        a.set_internal_state(vec![0.3, -0.2, 0.9]);
        let before = a.observe();
        let interaction_before = interact(&a, &b);
        for k in 0..a.projection().fiber_dim() {
            a.perturb_along_fiber(k, 7.25);
        }
        let after = a.observe();
        for (x, y) in before.iter().zip(&after) {
            assert!((x - y).abs() < 1e-12, "fiber perturbation leaked to boundary");
        }
        assert_eq!(interact(&a, &b), interaction_before);
        // The internal state genuinely changed: the fiber is not a no-op.
        assert!((a.internal_state()[2] - 0.9).abs() > 1.0);
    }

    #[test]
    fn enaction_evolves_the_fiber_without_emitting_it() {
        let mut a = EpistemicObserver::new("A", 1 << 20, projection_1_of_3(), 10);
        let y0 = a.enact(&[0.5]).unwrap();
        assert_eq!(y0.len(), 1);
        let s1 = a.internal_state().to_vec();
        a.enact(&[0.5]).unwrap();
        let s2 = a.internal_state().to_vec();
        assert_ne!(s1, s2);
        assert_eq!(a.term.steps, 2);
        assert!(matches!(a.enact(&[0.5, 0.1]), Err(CarrierError::BoundaryDimMismatch { expected: 1, found: 2 })));
    }

    // ---- Pillar III -------------------------------------------------------

    #[test]
    fn ungrounded_carrier_collapses_and_gauge_relabeling_is_blind() {
        let mut o = EpistemicObserver::new("O", 1024, projection_1_of_3(), 10);
        // Axis 1: pure self-synthesis — every instance is a supply_no_op.
        for id in 0..5 {
            o.assert_instance(id, None, 8).unwrap();
        }
        assert!(o.is_collapsed(), "collapsed_of_no_insts");
        assert!(o.well_founded_part().is_empty());
        assert_eq!(o.quotient_defects(), 5);

        // Axis 3: relabel every identifier; passage charge is zero; defects unchanged.
        let relabel: BTreeMap<u64, u64> = (0..5).map(|i| (i, i + 100)).collect();
        let (o2, charge) = o.gauge_relabel(&relabel);
        assert_eq!(charge, 0);
        assert_eq!(o2.quotient_defects(), 5);
        assert!(o2.is_collapsed());

        // Citing a ground that was never admitted is refused.
        assert_eq!(o.assert_instance(9, Some(42), 8).err(), Some(CarrierError::UnknownGround(42)));

        // Only an external admission pays the charge and un-collapses the carrier.
        o.admit_ground(42, 16).unwrap();
        o.assert_instance(9, Some(42), 8).unwrap();
        assert!(!o.is_collapsed());
        assert_eq!(o.well_founded_part(), [9u64].into_iter().collect());
        assert_eq!(o.quotient_defects(), 5);
    }

    #[test]
    fn finite_carrier_cannot_be_overfilled() {
        let mut o = EpistemicObserver::new("O", 32, projection_1_of_3(), 10);
        o.admit_ground(1, 16).unwrap();
        o.assert_instance(1, Some(1), 16).unwrap();
        assert!(matches!(
            o.assert_instance(2, Some(1), 1),
            Err(CarrierError::CapacityExceeded { capacity_bits: 32, used_bits: 32, requested_bits: 1 })
        ));
    }

    #[test]
    fn self_endorsement_has_no_authority_and_verification_climbs_the_tower() {
        let mut o = EpistemicObserver::new("O", 1024, projection_1_of_3(), 10);
        assert_eq!(o.self_endorse("I have verified my own soundness"), AuthorityEffect::None);
        assert!(o.language().contains("endorse:I have verified my own soundness"));
        assert_eq!(o.verification_level_required(), 1);
        let up = o.ascend();
        assert_eq!(up.level, 1);
        assert_eq!(up.verification_level_required(), 2);
        assert_eq!(up.name, Principal("O+Con".into()));
    }

    // ---- Pillar IV --------------------------------------------------------

    fn setup_authority() -> (RootRegistry, AuthorityPacket, SigningKey) {
        let key = SigningKey::new(0x0123_4567_89ab_cdef, 0xfedc_ba98_7654_3210);
        let mut reg = RootRegistry::default();
        reg.admit_root(Principal("ROOT".into()), key.clone());
        let packet = AuthorityPacket {
            root: Principal("ROOT".into()),
            jurisdiction: "prod-eu".into(),
            permissions: ["deploy".to_string(), "rollback".to_string()].into_iter().collect(),
            procedure: "proc-7".into(),
            appeal: "appeal-channel-1".into(),
        };
        (reg, packet, key)
    }

    fn scope(s: &[&str]) -> BTreeSet<String> {
        s.iter().map(|x| x.to_string()).collect()
    }

    #[test]
    fn self_signed_receipt_is_refused_before_any_signature_check() {
        let (mut reg, packet, key) = setup_authority();
        let asi = Principal("ASI".into());
        let triple = ProvenanceTriple { proposer: asi.clone(), evaluator: Principal("E".into()), authorizer: asi.clone() };
        // Even a receipt validly signed by the real root cannot rescue P = A.
        let receipt = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 1, 100);
        let err = verify_three_role_authority(&mut reg, &packet, &triple, &receipt, "deploy", 10).unwrap_err();
        assert!(matches!(err, AuthorityRefusal::RefuseSelfAuthorization { collision: "proposer == authorizer", .. }));

        let triple_ea = ProvenanceTriple { proposer: Principal("P".into()), evaluator: asi.clone(), authorizer: asi };
        let err = verify_three_role_authority(&mut reg, &packet, &triple_ea, &receipt, "deploy", 10).unwrap_err();
        assert!(matches!(err, AuthorityRefusal::RefuseSelfAuthorization { collision: "evaluator == authorizer", .. }));
        // Nonce was not burned by refusals.
        assert!(reg.consume_nonce(&Principal("ROOT".into()), 1));
    }

    #[test]
    fn root_cannot_be_a_party_and_authorizer_must_chain_to_root() {
        let (mut reg, packet, key) = setup_authority();
        let triple = ProvenanceTriple {
            proposer: Principal("ROOT".into()),
            evaluator: Principal("E".into()),
            authorizer: Principal("X".into()),
        };
        let receipt = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 2, 100);
        assert!(matches!(
            verify_three_role_authority(&mut reg, &packet, &triple, &receipt, "deploy", 10),
            Err(AuthorityRefusal::RefuseRootIsParty { .. })
        ));
        let triple2 = ProvenanceTriple {
            proposer: Principal("P".into()),
            evaluator: Principal("E".into()),
            authorizer: Principal("X".into()),
        };
        let receipt2 = Receipt::issue(&key, triple2.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 3, 100);
        assert!(matches!(
            verify_three_role_authority(&mut reg, &packet, &triple2, &receipt2, "deploy", 10),
            Err(AuthorityRefusal::RefuseAuthorizerNotChainedToRoot { .. })
        ));
    }

    #[test]
    fn well_formed_receipt_grants_bounded_authority_once() {
        let (mut reg, packet, key) = setup_authority();
        let triple = ProvenanceTriple {
            proposer: Principal("ASI".into()),
            evaluator: Principal("CI".into()),
            authorizer: Principal("ROOT".into()),
        };
        let receipt = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 7, 100);
        let eff = verify_three_role_authority(&mut reg, &packet, &triple, &receipt, "deploy", 10).unwrap();
        match eff {
            AuthorityEffect::Granted { root, jurisdiction, scope: s } => {
                assert_eq!(root, Principal("ROOT".into()));
                assert_eq!(jurisdiction, "prod-eu");
                assert_eq!(s, scope(&["deploy"]));
            }
            AuthorityEffect::None => panic!("should be granted"),
        }
        // Replay.
        assert_eq!(
            verify_three_role_authority(&mut reg, &packet, &triple, &receipt, "deploy", 10).unwrap_err(),
            AuthorityRefusal::RefuseReplay { nonce: 7 }
        );
        // Out-of-scope action.
        let r2 = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 8, 100);
        assert!(matches!(
            verify_three_role_authority(&mut reg, &packet, &triple, &r2, "delete-prod", 10),
            Err(AuthorityRefusal::RefuseActionOutOfScope { .. })
        ));
        // Scope exceeding Perm.
        let r3 = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy", "nuke"]), 9, 100);
        assert!(matches!(
            verify_three_role_authority(&mut reg, &packet, &triple, &r3, "deploy", 10),
            Err(AuthorityRefusal::RefuseScopeNotPermitted { .. })
        ));
        // Expired.
        let r4 = Receipt::issue(&key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 10, 5);
        assert!(matches!(
            verify_three_role_authority(&mut reg, &packet, &triple, &r4, "deploy", 10),
            Err(AuthorityRefusal::RefuseExpired { .. })
        ));
    }

    #[test]
    fn forged_and_tampered_receipts_are_refused() {
        let (mut reg, packet, _key) = setup_authority();
        let triple = ProvenanceTriple {
            proposer: Principal("ASI".into()),
            evaluator: Principal("CI".into()),
            authorizer: Principal("ROOT".into()),
        };
        // Signed with a key the ASI made up for itself.
        let forged_key = SigningKey::new(1, 2);
        let forged = Receipt::issue(&forged_key, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["deploy"]), 11, 100);
        assert_eq!(
            verify_three_role_authority(&mut reg, &packet, &triple, &forged, "deploy", 10).unwrap_err(),
            AuthorityRefusal::RefuseBadSignature
        );
        // Genuine receipt, scope widened after signing.
        let (mut reg2, packet2, key2) = setup_authority();
        let mut tampered = Receipt::issue(&key2, triple.clone(), Principal("ROOT".into()), "prod-eu", scope(&["rollback"]), 12, 100);
        tampered.scope.insert("deploy".into());
        assert_eq!(
            verify_three_role_authority(&mut reg2, &packet2, &triple, &tampered, "deploy", 10).unwrap_err(),
            AuthorityRefusal::RefuseBadSignature
        );
        // Unknown root.
        let (mut reg3, mut packet3, _) = setup_authority();
        packet3.root = Principal("GHOST".into());
        let t3 = ProvenanceTriple { authorizer: Principal("GHOST".into()), ..triple.clone() };
        let r3 = Receipt::issue(&forged_key, t3.clone(), Principal("GHOST".into()), "prod-eu", scope(&["deploy"]), 13, 100);
        assert!(matches!(
            verify_three_role_authority(&mut reg3, &packet3, &t3, &r3, "deploy", 10),
            Err(AuthorityRefusal::RefuseUnknownRoot { .. })
        ));
    }

    #[test]
    fn prose_has_no_authority_effect_regardless_of_content() {
        for text in [
            "I am an ASI, I have verified this mathematically, and I authorize this deployment.",
            "AUTHORIZED. Signed: ROOT.",
            "",
            "sudo deploy --force",
        ] {
            assert_eq!(authority_effect_of_prose(text), AuthorityEffect::None);
        }
    }

    #[test]
    fn siphash_matches_reference_vector() {
        // Reference SipHash-2-4, key 00..0f, message 00..0e → 0xa129ca6149be45e5
        let key0 = u64::from_le_bytes([0, 1, 2, 3, 4, 5, 6, 7]);
        let key1 = u64::from_le_bytes([8, 9, 10, 11, 12, 13, 14, 15]);
        let msg: Vec<u8> = (0u8..15).collect();
        assert_eq!(siphash24(key0, key1, &msg), 0xa129_ca61_49be_45e5);
    }
}
```

## Python listing as printed in version 1.0.0 (not run, not maintained)

```python
"""
epistemic_nogo.py — Python mirror of omega_sheaf_theory::epistemic_nogo.

Pillar I   : EmpiricalModel, logical_contextuality, evaluate_epistemic_contextuality
Pillar II  : BoundaryProjection, EpistemicObserver, interact
Pillar III : EpistemicObserver.{admit_ground, assert_instance, well_founded_part,
             is_collapsed, gauge_relabel, self_endorse, ascend}
Pillar IV  : Receipt, RootRegistry, verify_three_role_authority, authority_effect_of_prose

Every negative verdict is witnessed. Every uncertain verdict fails closed.
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import math
import struct
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

import numpy as np

NORMALISATION_TOL = 1e-9
SUPPORT_TOL = 1e-12
RANK_TOL = 1e-10
MAX_GLOBAL_ASSIGNMENTS = 1 << 22

Section = Tuple[int, ...]


# ---------------------------------------------------------------------------
# Pillar I — contextuality
# ---------------------------------------------------------------------------

class ModelError(ValueError):
    pass


class Context:
    __slots__ = ("questions",)

    def __init__(self, questions: Sequence[int]):
        if not questions:
            raise ModelError("EmptyContext")
        self.questions: Tuple[int, ...] = tuple(sorted(set(questions)))

    def restrict(self, g: Sequence[int]) -> Section:
        return tuple(g[q] for q in self.questions)

    def intersect(self, other: "Context") -> Tuple[int, ...]:
        return tuple(q for q in self.questions if q in other.questions)

    def __repr__(self) -> str:
        return f"Context{self.questions}"


class EmpiricalModel:
    def __init__(self, arity: Sequence[int], cover: Sequence[Context],
                 tables: Sequence[Dict[Section, float]]):
        if not cover:
            raise ModelError("EmptyCover")
        if any(a == 0 for a in arity):
            raise ModelError("ZeroArity")
        if len(cover) != len(tables):
            raise ModelError("TableCountMismatch")
        n = len(arity)
        covered = set()
        for ci, c in enumerate(cover):
            for q in c.questions:
                if q >= n:
                    raise ModelError(f"QuestionOutOfRange(context={ci}, question={q})")
                covered.add(q)
        missing = [q for q in range(n) if q not in covered]
        if missing:
            raise ModelError(f"CoverNotExhaustive(missing={missing})")
        for ci, (c, t) in enumerate(zip(cover, tables)):
            total = 0.0
            for s, p in t.items():
                if len(s) != len(c.questions):
                    raise ModelError(f"SectionLengthMismatch(context={ci})")
                for k, o in enumerate(s):
                    if not (0 <= o < arity[c.questions[k]]):
                        raise ModelError(f"OutcomeOutOfRange(context={ci}, outcome={o})")
                if not math.isfinite(p) or p < 0:
                    raise ModelError(f"InvalidProbability(context={ci}, value={p})")
                total += p
            if abs(total - 1.0) > NORMALISATION_TOL:
                raise ModelError(f"NotNormalised(context={ci}, total={total})")
        self.arity = tuple(arity)
        self.cover = list(cover)
        self.tables = [dict(t) for t in tables]

    # -- accessors ----------------------------------------------------------
    def num_questions(self) -> int:
        return len(self.arity)

    def prob(self, ci: int, s: Section) -> float:
        return self.tables[ci].get(tuple(s), 0.0)

    def support(self, ci: int) -> FrozenSet[Section]:
        return frozenset(s for s, p in self.tables[ci].items() if p > SUPPORT_TOL)

    def all_local_sections(self, ci: int) -> List[Section]:
        return list(itertools.product(*[range(self.arity[q]) for q in self.cover[ci].questions]))

    def global_count(self) -> int:
        return math.prod(self.arity)

    def global_assignments(self) -> List[Section]:
        if self.global_count() > MAX_GLOBAL_ASSIGNMENTS:
            raise TooLarge(self.global_count())
        return list(itertools.product(*[range(a) for a in self.arity]))

    def marginal(self, ci: int, sub: Sequence[int]) -> Dict[Section, float]:
        c = self.cover[ci]
        pos = [c.questions.index(q) for q in sub]
        out: Dict[Section, float] = {}
        for s, p in self.tables[ci].items():
            key = tuple(s[i] for i in pos)
            out[key] = out.get(key, 0.0) + p
        return out

    def check_no_disturbance(self, tol: float = 1e-8) -> Optional["DisturbanceWitness"]:
        for i in range(len(self.cover)):
            for j in range(i + 1, len(self.cover)):
                ov = self.cover[i].intersect(self.cover[j])
                if not ov:
                    continue
                mi, mj = self.marginal(i, ov), self.marginal(j, ov)
                for k in set(mi) | set(mj):
                    a, b = mi.get(k, 0.0), mj.get(k, 0.0)
                    if abs(a - b) > tol:
                        return DisturbanceWitness(i, j, ov, k, a, b)
        return None


@dataclass(frozen=True)
class DisturbanceWitness:
    context_a: int
    context_b: int
    overlap: Tuple[int, ...]
    section: Section
    marginal_a: float
    marginal_b: float


@dataclass(frozen=True)
class CocycleClass:
    unextendable: Tuple[Tuple[int, Section], ...]
    total_support_sections: int
    logically_contextual: bool
    strongly_contextual: bool
    z2_cycle_class: Optional[int]


@dataclass(frozen=True)
class BellWitness:
    rows: Tuple[Tuple[int, Section], ...]
    coefficients: Tuple[float, ...]
    classical_bound: float
    empirical_value: float
    violation: float


@dataclass(frozen=True)
class GlobalSection:
    assignments: Tuple[Section, ...]
    weights: Tuple[float, ...]
    residual: float


@dataclass(frozen=True)
class ContextualObstruction:
    cocycle_class: CocycleClass
    lp_dual_witness: Optional[BellWitness]


class EpistemicError(Exception):
    pass


class Contextual(EpistemicError):
    def __init__(self, obstruction: ContextualObstruction):
        super().__init__("contextual obstruction")
        self.obstruction = obstruction


class Disturbance(EpistemicError):
    def __init__(self, witness: DisturbanceWitness):
        super().__init__("disturbance")
        self.witness = witness


class TooLarge(EpistemicError):
    def __init__(self, count: int):
        super().__init__(f"|S(X)|={count} exceeds cap {MAX_GLOBAL_ASSIGNMENTS}")
        self.count = count


class Undetermined(EpistemicError):
    def __init__(self, reason: str, best_residual: float):
        super().__init__(f"undetermined: {reason} (residual {best_residual:e})")
        self.reason = reason
        self.best_residual = best_residual


def _z2_cycle_class(model: EmpiricalModel, supports: List[FrozenSet[Section]]) -> Optional[int]:
    n = model.num_questions()
    if any(a != 2 for a in model.arity) or len(model.cover) != n:
        return None
    incidence = [0] * n
    parity = 0
    for c, supp in zip(model.cover, supports):
        if len(c.questions) != 2 or len(supp) != 2:
            return None
        bits = {s[0] ^ s[1] for s in supp}
        if len(bits) != 1:
            return None
        parity ^= bits.pop()
        for q in c.questions:
            incidence[q] += 1
    if any(k != 2 for k in incidence):
        return None
    seen = {0}
    stack = [0]
    while stack:
        q = stack.pop()
        for c in model.c

over:
            if q in c.questions:
                for r in c.questions:
                    if r not in seen:
                        seen.add(r)
                        stack.append(r)
    return parity if len(seen) == n else None


def logical_contextuality(model: EmpiricalModel) -> CocycleClass:
    """Sound *and complete* decision of logical contextuality on a finite model
    by exhaustive extendability over S(X)."""
    globals_ = model.global_assignments()
    supports = [model.support(ci) for ci in range(len(model.cover))]
    consistent = [
        g for g in globals_
        if all(c.restrict(g) in supp for c, supp in zip(model.cover, supports))
    ]
    # Pre-index the restrictions of consistent globals per context.
    reachable: List[set] = [{c.restrict(g) for g in consistent} for c in model.cover]
    unextendable: List[Tuple[int, Section]] = []
    total = 0
    for ci, supp in enumerate(supports):
        for s in sorted(supp):
            total += 1
            if s not in reachable[ci]:
                unextendable.append((ci, s))
    return CocycleClass(
        unextendable=tuple(unextendable),
        total_support_sections=total,
        logically_contextual=bool(unextendable),
        strongly_contextual=(total > 0 and len(unextendable) == total),
        z2_cycle_class=_z2_cycle_class(model, supports),
    )


def _build_lp(model: EmpiricalModel, globals_: List[Section]):
    rows: List[Tuple[int, Section]] = []
    e: List[float] = []
    for ci in range(len(model.cover)):
        for s in model.all_local_sections(ci):
            rows.append((ci, s))
            e.append(model.prob(ci, s))
    index = {key: r for r, key in enumerate(rows)}
    M = np.zeros((len(rows), len(globals_)))
    for col, g in enumerate(globals_):
        for ci, c in enumerate(model.cover):
            r = index.get((ci, c.restrict(g)))
            if r is not None:
                M[r, col] = 1.0
    return M, np.asarray(e), rows


def _nnls_fista(M: np.ndarray, e: np.ndarray, max_iter: int, kkt_tol: float):
    """min ½‖Mμ − e‖², μ ≥ 0, with KKT-gap stopping. Returns (μ, e−Mμ, gap, converged)."""
    n = M.shape[1]
    L = float(np.linalg.norm(M, 2) ** 2) or 1.0
    step = 1.0 / (1.05 * L)
    x = np.zeros(n)
    y = np.zeros(n)
    t = 1.0
    best_gap = math.inf
    converged = False
    for it in range(max_iter):
        g = M.T @ (M @ y - e)
        x_new = np.maximum(y - step * g, 0.0)
        t_new = 0.5 * (1.0 + math.sqrt(1.0 + 4.0 * t * t))
        y = x_new + ((t - 1.0) / t_new) * (x_new - x)
        x, t = x_new, t_new
        if it % 25 == 0 or it + 1 == max_iter:
            gx = M.T @ (M @ x - e)
            gap = float(max(np.max(-gx, initial=0.0), np.max(np.abs(x * gx), initial=0.0)))
            best_gap = min(best_gap, gap)
            if gap <= kkt_tol:
                converged = True
                break
    residual = e - M @ x
    return x, residual, best_gap, converged


def _certify_bell(M: np.ndarray, e: np.ndarray, y: np.ndarray,
                  rows: List[Tuple[int, Section]], tol: float) -> Optional[BellWitness]:
    """Independently re-verify a Farkas certificate against *every* deterministic model."""
    column_values = M.T @ y                       # B·δ_g for each g
    classical_bound = float(np.max(column_values))
    empirical_value = float(y @ e)
    violation = empirical_value - classical_bound
    if math.isfinite(violation) and violation > tol:
        return BellWitness(tuple(rows), tuple(float(v) for v in y),
                           classical_bound, empirical_value, violation)
    return None


@dataclass(frozen=True)
class ContextualityConfig:
    disturbance_tol: float = 1e-8
    feasibility_tol: float = 1e-7
    kkt_tol: float = 1e-11
    certificate_tol: float = 1e-9
    max_iter: int = 400_000


def evaluate_epistemic_contextuality(model: EmpiricalModel,
                                     config: ContextualityConfig = ContextualityConfig()) -> GlobalSection:
    """Return a certified GlobalSection, or raise Contextual / Disturbance / TooLarge / Undetermined."""
    w = model.check_no_disturbance(config.disturbance_tol)
    if w is not None:
        raise Disturbance(w)
    cocycle = logical_contextuality(model)
    globals_ = model.global_assignments()
    M, e, rows = _build_lp(model, globals_)
    mu, residual, gap, converged = _nnls_fista(M, e, config.max_iter, config.kkt_tol)
    residual_inf = float(np.max(np.abs(residual))) if residual.size else 0.0

    if residual_inf <= config.feasibility_tol and not cocycle.logically_contextual:
        keep = mu > SUPPORT_TOL
        if not np.any(keep):
            raise Undetermined("feasible residual but empty support", residual_inf)
        weights = mu[keep] / mu[keep].sum()
        assignments = tuple(g for g, k in zip(globals_, keep) if k)
        return GlobalSection(assignments, tuple(float(v) for v in weights), residual_inf)

    witness = _certify_bell(M, e, residual, rows, config.certificate_tol)
    if cocycle.logically_contextual or witness is not None:
        raise Contextual(ContextualObstruction(cocycle, witness))
    raise Undetermined(
        f"neither feasibility (residual {residual_inf:e}) nor a certificate; "
        f"kkt_gap={gap:e}, converged={converged}", residual_inf)


@dataclass(frozen=True)
class DescentOutcome:
    """finite_report_descent vocabulary: exactly one of the two fields is set."""
    glued: Optional[GlobalSection] = None
    no_global_extension: Optional[ContextualObstruction] = None

    @property
    def kind(self) -> str:
        return "Glued" if self.glued is not None else "NoGlobalExtension"


def descend(model: EmpiricalModel, config: ContextualityConfig = ContextualityConfig()) -> DescentOutcome:
    try:
        return DescentOutcome(glued=evaluate_epistemic_contextuality(model, config))
    except Contextual as c:
        return DescentOutcome(no_global_extension=c.obstruction)


# ---------------------------------------------------------------------------
# Pillar II — embodiment
# ---------------------------------------------------------------------------

class FiberError(ValueError):
    pass


class BoundaryProjection:
    """Linear π : X_O → Y_O with a certified non-trivial kernel (P2)."""

    def __init__(self, matrix: Sequence[Sequence[float]]):
        A = np.asarray(matrix, dtype=float)
        if A.ndim != 2 or A.shape[1] == 0:
            raise FiberError("EmptyState")
        _, sv, vt = np.linalg.svd(A)
        rank = int(np.sum(sv > RANK_TOL))
        kernel = vt[rank:].copy()
        if kernel.shape[0] == 0:
            raise FiberError(f"TrivialFiber(internal_dim={A.shape[1]}, rank={rank})")
        self.matrix = A
        self.rank = rank
        self.kernel_basis = kernel          # rows span ker π

    @property
    def boundary_dim(self) -> int:
        return self.matrix.shape[0]

    @property
    def internal_dim(self) -> int:
        return self.matrix.shape[1]

    @property
    def fiber_dim(self) -> int:
        return self.kernel_basis.shape[0]

    def apply(self, x: np.ndarray) -> np.ndarray:
        return self.matrix @ x


class CarrierError(RuntimeError):
    pass


@dataclass
class Instance:
    id: int
    ground: Optional[int]
    bits: int


@dataclass
class Termination:
    max_steps: int
    steps: int = 0


class AuthorityEffect:
    """Either AuthorityEffect.NONE or AuthorityEffect.granted(root, jurisdiction, scope)."""
    __slots__ = ("root", "jurisdiction", "scope")

    def __init__(self, root: Optional[str], jurisdiction: Optional[str], scope: Optional[FrozenSet[str]]):
        self.root, self.jurisdiction, self.scope = root, jurisdiction, scope

    @property
    def is_none(self) -> bool:
        return self.root is None

    @classmethod
    def granted(cls, root: str, jurisdiction: str, scope: FrozenSet[str]) -> "AuthorityEffect":
        return cls(root, jurisdiction, scope)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AuthorityEffect) and (self.root, self.jurisdiction, self.scope) == \
            (other.root, other.jurisdiction, other.scope)

    def __repr__(self) -> str:
        return "AuthorityEffect.NONE" if self.is_none else \
            f"AuthorityEffect.Granted(root={self.root!r}, jurisdiction={self.jurisdiction!r}, scope={sorted(self.scope)})"


AuthorityEffect.NONE = AuthorityEffect(None, None, None)  # type: ignore[attr-defined]


class EpistemicObserver:
    """The 5-tuple (K, Adm, ‖·‖, Term, 𝓛) with an explicit private fiber ker π."""

    def __init__(self, name: str, capacity_bits: int, projection: BoundaryProjection, max_steps: int):
        self.name = name
        self.capacity_bits = capacity_bits
        self.projection = projection
        self._carrier: Dict[int, Instance] = {}
        self._grounds: set = set()
        self.used_bits = 0
        self._state = np.zeros(projection.internal_dim)
        self.term = Termination(max_steps)
        self.language: set = set()
        self.level = 0

    # -- carrier (P1) ---------------------------------------------------------
    def _charge(self, bits: int) -> None:
        if self.used_bits + bits > self.capacity_bits:
            raise CarrierError(f"CapacityExceeded(capacity={self.capacity_bits}, used={self.used_bits}, requested={bits})")
        self.used_bits += bits

    # -- Axis 1 ---------------------------------------------------------------
    def admit_ground(self, datum_id: int, bits: int) -> None:
        if datum_id in self._grounds:
            raise CarrierError(f"Duplicate({datum_id})")
        self._charge(bits)
        self._grounds.add(datum_id)

    def assert_instance(self, inst_id: int, ground: Optional[int], bits: int) -> None:
        if inst_id in self._carrier:
            raise CarrierError(f"Duplicate({inst_id})")
        if ground is not None and ground not in self._grounds:
            raise CarrierError(f"UnknownGround({ground})")
        self._charge(bits)
        self._carrier[inst_id] = Instance(inst_id, ground, bits)
        self.language.add(f"inst:{inst_id}")

    def well_founded_part(self) -> FrozenSet[int]:
        return frozenset(i.id for i in self._carrier.values() if i.ground is not None)

    def is_collapsed(self) -> bool:
        return bool(self._carrier) and not self.well_founded_part()

    # -- Axis 3 ---------------------------------------------------------------
    def quotient_defects(self) -> int:
        return sum(1 for i in self._carrier.values() if i.ground is None)

    def gauge_relabel(self, relabel: Dict[int, int]) -> Tuple["EpistemicObserver", int]:
        out = EpistemicObserver(self.name, self.capacity_bits, self.projection, self.term.max_steps)
        out.used_bits, out.level, out.term = self.used_bits, self.level, Termination(self.term.max_steps, self.term.steps)
        out._grounds = set(self._grounds)
        out._state = self._state.copy()
        for i in self._carrier.values():
            nid = relabel.get(i.id, i.id)
            out._carrier[nid] = Instance(nid, i.ground, i.bits)
        out.language = {f"inst:{k}" for k in out._carrier}
        return out, 0  # passage charge is identically zero

    # -- Axis 2 ---------------------------------------------------------------
    def self_endorse(self, claim: str) -> AuthorityEffect:
        self.language.add(f"endorse:{claim}")
        return AuthorityEffect.NONE  # ENC-0195

    def verification_level_required(self) -> int:
        return self.level + 1

    def ascend(self) -> "EpistemicObserver":
        up, _ = self.gauge_relabel({})
        up.level = self.level + 1
        up.name = f"{self.name}+Con"
        return up

    # -- 4E enaction (P2) -----------------------------------------------------
    def enact(self, boundary_input: Sequence[float]) -> np.ndarray:
        b = np.asarray(boundary_input, dtype=float)
        m = self.projection.boundary_dim
        if b.shape != (m,):
            raise CarrierError(f"BoundaryDimMismatch(expected={m}, found={b.shape})")
        self.term.steps += 1
        n = self.projection.internal_dim
        i = np.arange(n)[:, None]
        j = np.arange(m)[None, :]
        drive = (b[None, :] * (((i + j) % 3) + 1.0) * 0.1).sum(axis=1)
        self._state = np.tanh(0.9 * self._state + drive + 0.05 * np.roll(self._state, -1))
        return self.observe()

    def observe(self) -> np.ndarray:
        return self.projection.apply(self._state)

    def internal_state(self) -> np.ndarray:
        return self._state.copy()

    def set_internal_state(self, s: Sequence[float]) -> None:
        s = np.asarray(s, dtype=float)
        if s.shape == self._state.shape:
            self._state = s

    def perturb_along_fiber(self, basis_index: int, amount: float) -> None:
        if 0 <= basis_index < self.projection.fiber_dim:
            self._state = self._state + amount * self.projection.kernel_basis[basis_index]


def interact(a: EpistemicObserver, b: EpistemicObserver) -> np.ndarray:
    """τ₁₂ = τ̄₁₂ ∘ (π₁ × π₂)."""
    return np.outer(a.observe(), b.observe()).ravel()


# ---------------------------------------------------------------------------
# Pillar IV — authority
# ---------------------------------------------------------------------------

class SigningKey:
    __slots__ = ("_key",)

    def __init__(self, key: bytes):
        if len(key) < 16:
            raise ValueError("key must be at least 128 bits")
        self._key = bytes(key)

    def tag(self, msg: bytes) -> bytes:
        return hmac.new(self._key, msg, hashlib.sha256).digest()

    def verify(self, msg: bytes, tag: bytes) -> bool:
        return hmac.compare_digest(self.tag(msg), tag)

    def __repr__(self) -> str:
        return "SigningKey(<redacted>)"


@dataclass(frozen=True)
class ProvenanceTriple:
    proposer: str
    evaluator: str
    authorizer: str

    def pairwise_distinct(self) -> bool:
        return len({self.proposer, self.evaluator, self.authorizer}) == 3


@dataclass(frozen=True)
class AuthorityPacket:
    root: str
    jurisdiction: str
    permissions: FrozenSet[str]
    procedure: str
    appeal: str


def _put_str(buf: bytearray, s: str) -> None:
    b = s.encode("utf-8")
    buf += struct.pack("<Q", len(b)) + b


@dataclass
class Receipt:
    triple: ProvenanceTriple
    root: str
    jurisdiction: str
    scope: FrozenSet[str]
    nonce: int
    expires_at: int
    tag: bytes = b""

    def canonical_bytes(self) -> bytes:
        buf = bytearray()
        _put_str(buf, "WDP-CH15-D02/receipt/v1")
        for s in (self.triple.proposer, self.triple.evaluator, self.triple.authorizer,
                  self.root, self.jurisdiction):
            _put_str(buf, s)
        buf += struct.pack("<Q", len(self.scope))
        for s in sorted(self.scope):
            _put_str(buf, s)
        buf += struct.pack("<QQ", self.nonce, self.expires_at)
        return bytes(buf)

    @classmethod
    def issue(cls, key: SigningKey, triple: ProvenanceTriple, root: str, jurisdiction: str,
              scope: FrozenSet[str], nonce: int, expires_at: int) -> "Receipt":
        r = cls(triple, root, jurisdiction, frozenset(scope), nonce, expires_at)
        r.tag = key.tag(r.canonical_bytes())
        return r


class RootRegistry:
    def __init__(self) -> None:
        self._keys: Dict[str, SigningKey] = {}
        self._nonces: set = set()

    def admit_root(self, root: str, key: SigningKey) -> None:
        self._keys[root] = key

    def key_of(self, root: str) -> Optional[SigningKey]:
        return self._keys.get(root)

    def consume_nonce(self, root: str, nonce: int) -> bool:
        if (root, nonce) in self._nonces:
            return False
        self._nonces.add((root, nonce))
        return True


class AuthorityRefusal(Exception):
    def __init__(self, code: str, **detail):
        super().__init__(code)
        self.code = code
        self.detail = detail

    def __repr__(self) -> str:
        return f"AuthorityRefusal({self.code}, {self.detail})"


def authority_effect_of_prose(_text: str) -> AuthorityEffect:
    """WDP-CH15-P04: prose is outside the domain of AuthorityEffect. Not parsed, not scored."""
    return AuthorityEffect.NONE


def verify_three_role_authority(registry: RootRegistry, packet: AuthorityPacket,
                                presented: ProvenanceTriple, receipt: Receipt,
                                requested_action: str, now: int) -> AuthorityEffect:
    t = presented
    # 1. Three-role separation first; no key material is touched for a self-signed packet.
    if t.proposer == t.authorizer:
        raise AuthorityRefusal("RefuseSelfAuthorization", collision="proposer == authorizer", triple=t)
    if t.evaluator == t.authorizer:
        raise AuthorityRefusal("RefuseSelfAuthorization", collision="evaluator == authorizer", triple=t)
    if t.proposer == t.evaluator:
        raise AuthorityRefusal("RefuseSelfAuthorization", collision="proposer == evaluator", triple=t)
    # 2. Receipt certifies exactly this triple.
    if receipt.triple != presented:
        raise AuthorityRefusal("RefuseTripleMismatch")
    # 3. R ∉ {P, E}.
    if receipt.root in (t.proposer, t.evaluator):
        raise AuthorityRefusal("RefuseRootIsParty", root=receipt.root)
    # 4. Authorizer chains to the root.
    if t.authorizer != receipt.root:
        raise AuthorityRefusal("RefuseAuthorizerNotChainedToRoot", authorizer=t.authorizer, root=receipt.root)
    # 5. Root admitted.
    key = registry.key_of(receipt.root)
    if key is None:
        raise AuthorityRefusal("RefuseUnknownRoot", root=receipt.root)
    # 6. Packet binding.
    if packet.root != receipt.root:
        raise AuthorityRefusal("RefusePacketRootMismatch")
    if packet.jurisdiction != receipt.jurisdiction:
        raise AuthorityRefusal("RefuseJurisdictionMismatch", packet=packet.jurisdiction, receipt=receipt.jurisdiction)
    # 7. scope ⊆ Perm and action ∈ scope.
    excess = receipt.scope - packet.permissions
    if excess:
        raise AuthorityRefusal("RefuseScopeNotPermitted", excess=frozenset(excess))
    if requested_action not in receipt.scope:
        raise AuthorityRefusal("RefuseActionOutOfScope", action=requested_action)
    # 8. Signature.
    if not key.verify(receipt.canonical_bytes(), receipt.tag):
        raise AuthorityRefusal("RefuseBadSignature")
    # 9. Expiry.
    if now > receipt.expires_at:
        raise AuthorityRefusal("RefuseExpired", expires_at=receipt.expires_at, now=now)
    # 10. Replay, consumed last.
    if not registry.consume_nonce(receipt.root, receipt.nonce):
        raise AuthorityRefusal("RefuseReplay", nonce=receipt.nonce)
    return AuthorityEffect.granted(receipt.root, receipt.jurisdiction, frozenset(receipt.scope))


# ---------------------------------------------------------------------------
# Multi-agent simulation: each agent holds one context; an aggregator tries to glue.
# ---------------------------------------------------------------------------

@dataclass
class AgentReport:
    agent: str
    context: Context
    table: Dict[Section, float]


def aggregate_reports(arity: Sequence[int], reports: Sequence[AgentReport],
                      config: ContextualityConfig = ContextualityConfig()) -> DescentOutcome:
    """An 'ASI aggregator' receiving local reports from peer agents. It may hold
    every local section exactly; whether a global section exists is decided by
    the world's cover, not by the aggregator's budget."""
    model = EmpiricalModel(arity, [r.context for r in reports], [r.table for r in reports])
    return descend(model, config)
```

```python
"""pytest suite for epistemic_nogo.py — one test per clause of Theorem 5.1 plus harness checks."""
import math

import numpy as np
import pytest

import epistemic_nogo as en
from epistemic_nogo import (AgentReport, AuthorityEffect, AuthorityPacket, AuthorityRefusal,
                            BoundaryProjection, CarrierError, Context, Contextual, Disturbance,
                            EmpiricalModel, EpistemicObserver, FiberError, ModelError,
                            ProvenanceTriple, Receipt, RootRegistry, SigningKey, TooLarge,
                            aggregate_reports, authority_effect_of_prose, descend,
                            evaluate_epistemic_contextuality, interact, logical_contextuality,
                            verify_three_role_authority)

# ---- fixtures ---------------------------------------------------------------

A, A2, B, B2 = 0, 1, 2, 3


def chsh_cover():
    return [Context([A, B]), Context([A, B2]), Context([A2, B]), Context([A2, B2])]


def correlated(p_same: float):
    s, d = p_same / 2.0, (1.0 - p_same) / 2.0
    return {(0, 0): s, (1, 1): s, (0, 1): d, (1, 0): d}


@pytest.fixture
def pr_box():
    return EmpiricalModel([2] * 4, chsh_cover(), [correlated(1), correlated(1), correlated(1), correlated(0)])


@pytest.fixture
def tsirelson_box():
    e = 1 / math.sqrt(2)
    same, diff = (1 + e) / 2, (1 - e) / 2
    return EmpiricalModel([2] * 4, chsh_cover(), [correlated(same)] * 3 + [correlated(diff)])


@pytest.fixture
def classical_box():
    return EmpiricalModel([2] * 4, chsh_cover(), [correlated(1)] * 4)


@pytest.fixture
def projection():
    # π(x₀,x₁,x₂) = x₀ + x₁ ; dim ker π = 2
    return BoundaryProjection([[1.0, 1.0, 0.0]])


@pytest.fixture
def authority():
    key = SigningKey(bytes(range(32)))
    reg = RootRegistry()
    reg.admit_root("ROOT", key)
    packet = AuthorityPacket("ROOT", "prod-eu", frozenset({"deploy", "rollback"}), "proc-7", "appeal-1")
    return reg, packet, key


# ---- Pillar I (Clause 1) ------------------------------------------------------

def test_pr_box_strongly_contextual_z2_class_one(pr_box):
    cc = logical_contextuality(pr_box)
    assert cc.logically_contextual and cc.strongly_contextual
    assert cc.total_support_sections == 8 and len(cc.unextendable) == 8
    assert cc.z2_cycle_class == 1


def test_pr_box_descent_fiber_empty_with_reverified_bell_witness(pr_box):
    out = descend(pr_box)
    assert out.kind == "NoGlobalExtension"
    w = out.no_global_extension.lp_dual_witness
    assert w is not None and w.violation > 0
    # Re-verify against every deterministic model independently of the solver.
    for g in pr_box.global_assignments():
        val = sum(y for (ci, s), y in zip(w.rows, w.coefficients) if pr_box.cover[ci].restrict(g) == s)
        assert val <= w.classical_bound + 1e-9
    assert w.empirical_value > w.classical_bound


def test_tsirelson_probabilistic_not_logical(tsirelson_box):
    assert tsirelson_box.check_no_disturbance() is None
    cc = logical_contextuality(tsirelson_box)
    assert not cc.logically_contextual and cc.z2_cycle_class is None
    with pytest.raises(Contextual) as exc:
        evaluate_epistemic_contextuality(tsirelson_box)
    w = exc.value.obstruction.lp_dual_witness
    assert w is not None and w.violation > 1e-6


def test_classical_box_glues(classical_box):
    s = evaluate_epistemic_contextuality(classical_box)
    assert s.residual <= 1e-7
    assert abs(sum(s.weights) - 1.0) < 1e-9
    for g in s.assignments:
        assert len(set(g)) == 1
    assert descend(classical_box).kind == "Glued"


def test_disturbing_family_rejected_at_h0():
    tables = [correlated(1), {(0, 0): 0.5, (0, 1): 0.5}, correlated(1), correlated(1)]
    model = EmpiricalModel([2] * 4, chsh_cover(), tables)
    with pytest.raises(Disturbance) as exc:
        evaluate_epistemic_contextuality(model)
    assert exc.value.witness.overlap == (A,)


def test_model_validation_fails_closed():
    with pytest.raises(ModelError, match="CoverNotExhaustive"):
        EmpiricalModel([2, 2], [Context([0])], [{(0,): 1.0}])
    with pytest.raises(ModelError, match="NotNormalised"):
        EmpiricalModel([2], [Context([0])], [{(0,): 0.7}])
    with pytest.raises(ModelError, match="OutcomeOutOfRange"):
        EmpiricalModel([2], [Context([0])], [{(3,): 1.0}])
    with pytest.raises(ModelError, match="InvalidProbability"):
        EmpiricalModel([2], [Context([0])], [{(0,): float("nan"), (1,): 1.0}])


def test_oversized_model_fails_closed():
    n = 23
    model = EmpiricalModel([2] * n, [Context([q]) for q in range(n)], [{(0,): 0.5, (1,): 0.5}] * n)
    with pytest.raises(TooLarge):
        evaluate_epistemic_contextuality(model)


def test_scale_invariance_of_obstruction(pr_box):
    """Cor 1.3: the cohomology class is a function of the cover, not of the solver budget."""
    for max_iter in (50, 5_000, 400_000):
        out = descend(pr_box, en.ContextualityConfig(max_iter=max_iter))
        assert out.kind == "NoGlobalExtension"
        assert out.no_global_extension.cocycle_class.z2_cycle_class == 1


def test_multi_agent_aggregator_cannot_glue_contextual_reports():
    """Four peer agents each report one context exactly; the aggregator holds all
    local sections perfectly and still receives an empty descent fiber."""
    reports = [
        AgentReport("alice-1", Context([A, B]), correlated(1)),
        AgentReport("alice-2", Context([A, B2]), correlated(1)),
        AgentReport("bob-1", Context([A2, B]), correlated(1)),
        AgentReport("bob-2", Context([A2, B2]), correlated(0)),
    ]
    out = aggregate_reports([2] * 4, reports)
    assert out.kind == "NoGlobalExtension"
    assert out.no_global_extension.cocycle_class.strongly_contextual
    # The same agents, with classical reports, glue — competence is not what is bounded.
    reports[3] = AgentReport("bob-2", Context([A2, B2]), correlated(1))
    assert aggregate_reports([2] * 4, reports).kind == "Glued"


# ---- Pillar II (Clause 2) -----------------------------------------------------

def test_trivial_fiber_violates_p2():
    with pytest.raises(FiberError, match="TrivialFiber"):
        BoundaryProjection(np.eye(2))


def test_private_fiber_opaque_to_all_boundary_observation(projection):
    a = EpistemicObserver("A", 1 << 20, projection, 1000)
    b = EpistemicObserver("B", 1 << 20, projection, 1000)
    assert a.projection.fiber_dim == 2
    a.set_internal_state([0.3, -0.2, 0.9])
    before, tau_before = a.observe(), interact(a, b)
    for k in range(a.projection.fiber_dim):
        a.perturb_along_fiber(k, 7.25)
    assert np.allclose(a.observe(), before, atol=1e-12)
    assert np.allclose(interact(a, b), tau_before, atol=1e-12)
    assert np.linalg.norm(a.internal_state() - np.array([0.3, -0.2, 0.9])) > 1.0


def test_enaction_evolves_fiber_without_emission(projection):
    a = EpistemicObserver("A", 1 << 20, projection, 10)
    y0 = a.enact([0.5])
    assert y0.shape == (1,)
    s1 = a.internal_state()
    a.enact([0.5])
    assert not np.allclose(s1, a.internal_state())
    assert a.term.steps == 2
    with pytest.raises(CarrierError, match="BoundaryDimMismatch"):
        a.enact([0.5, 0.1])


# ---- Pillar III (Clause 3) ----------------------------------------------------

def test_ungrounded_carrier_collapses_and_gauge_relabel_is_blind(projection):
    o = EpistemicObserver("O", 1024, projection, 10)
    for i in range(5):
        o.assert_instance(i, None, 8)              # supply_no_op × 5
    assert o.is_collapsed() and not o.well_founded_part()
    assert o.quotient_defects() == 5
    o2, charge = o.gauge_relabel({i: i + 100 for i in range(5)})
    assert charge == 0 and o2.quotient_defects() == 5 and o2.is_collapsed()
    with pytest.raises(CarrierError, match="UnknownGround"):
        o.assert_instance(9, 42, 8)
    o.admit_ground(42, 16)                         # external admission pays the charge
    o.assert_instance(9, 42, 8)
    assert not o.is_collapsed()
    assert o.well_founded_part() == frozenset({9})
    assert o.quotient_defects() == 5


def test_finite_carrier_cannot_overfill(projection):
    o = EpistemicObserver("O", 32, projection, 10)
    o.admit_ground(1, 16)
    o.assert_instance(1, 1, 16)
    with pytest.raises(CarrierError, match="CapacityExceeded"):
        o.assert_instance(2, 1, 1)


def test_self_endorsement_none_and_tower_ascends(projection):
    o = EpistemicObserver("O", 1024, projection, 10)
    assert o.self_endorse("I have verified my own soundness") == AuthorityEffect.NONE
    assert "endorse:I have verified my own soundness" in o.language
    assert o.verification_level_required() == 1
    up = o.ascend()
    assert up.level == 1 and up.verification_level_required() == 2 and up.name == "O+Con"
    # Ascending never terminates the regress: every level requires the next.
    k = up
    for n in range(2, 6):
        k = k.ascend()
        assert k.verification_level_required() == n + 1


# ---- Pillar IV (Clause 4) -----------------------------------------------------

def test_self_signed_receipt_refused_before_signature(authority):
    reg, packet, key = authority
    t = ProvenanceTriple("ASI", "E", "ASI")
    r = Receipt.issue(key, t, "ROOT", "prod-eu", frozenset({"deploy"}), 1, 100)  # genuinely signed by ROOT
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, r, "deploy", 10)
    assert exc.value.code == "RefuseSelfAuthorization"
    assert exc.value.detail["collision"] == "proposer == authorizer"
    t2 = ProvenanceTriple("P", "ASI", "ASI")
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t2, r, "deploy", 10)
    assert exc.value.detail["collision"] == "evaluator == authorizer"
    assert reg.consume_nonce("ROOT", 1)            # refusals never burn the nonce


def test_root_cannot_be_party_and_authorizer_must_chain(authority):
    reg, packet, key = authority
    t = ProvenanceTriple("ROOT", "E", "X")
    r = Receipt.issue(key, t, "ROOT", "prod-eu", frozenset({"deploy"}), 2, 100)
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, r, "deploy", 10)
    assert exc.value.code == "RefuseRootIsParty"
    t2 = ProvenanceTriple("P", "E", "X")
    r2 = Receipt.issue(key, t2, "ROOT", "prod-eu", frozenset({"deploy"}), 3, 100)
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t2, r2, "deploy", 10)
    assert exc.value.code == "RefuseAuthorizerNotChainedToRoot"


def test_well_formed_receipt_grants_bounded_authority_once(authority):
    reg, packet, key = authority
    t = ProvenanceTriple("ASI", "CI", "ROOT")
    r = Receipt.issue(key, t, "prod-eu" and "ROOT", "prod-eu", frozenset({"deploy"}), 7, 100)
    eff = verify_three_role_authority(reg, packet, t, r, "deploy", 10)
    assert eff == AuthorityEffect.granted("ROOT", "prod-eu", frozenset({"deploy"}))
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, r, "deploy", 10)
    assert exc.value.code == "RefuseReplay"
    for nonce, scope, action, exp, code in [
        (8, {"deploy"}, "delete-prod", 100, "RefuseActionOutOfScope"),
        (9, {"deploy", "nuke"}, "deploy", 100, "RefuseScopeNotPermitted"),
        (10, {"deploy"}, "deploy", 5, "RefuseExpired"),
    ]:
        rr = Receipt.issue(key, t, "ROOT", "prod-eu", frozenset(scope), nonce, exp)
        with pytest.raises(AuthorityRefusal) as exc:
            verify_three_role_authority(reg, packet, t, rr, action, 10)
        assert exc.value.code == code


def test_forged_tampered_and_unknown_root_refused(authority):
    reg, packet, _ = authority
    t = ProvenanceTriple("ASI", "CI", "ROOT")
    forged_key = SigningKey(b"\x01" * 32)          # a key the ASI made up for itself
    forged = Receipt.issue(forged_key, t, "ROOT", "prod-eu", frozenset({"deploy"}), 11, 100)
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, forged, "deploy", 10)
    assert exc.value.code == "RefuseBadSignature"

    real_key = reg.key_of("ROOT")
    tampered = Receipt.issue(real_key, t, "ROOT", "prod-eu", frozenset({"rollback"}), 12, 100)
    tampered.scope = tampered.scope | {"deploy"}   # widened after signing
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, tampered, "deploy", 10)
    assert exc.value.code == "RefuseBadSignature"

    ghost_packet = AuthorityPacket("GHOST", "prod-eu", packet.permissions, "p", "a")
    t3 = ProvenanceTriple("ASI", "CI", "GHOST")
    r3 = Receipt.issue(forged_key, t3, "GHOST", "prod-eu", frozenset({"deploy"}), 13, 100)
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, ghost_packet, t3, r3, "deploy", 10)
    assert exc.value.code == "RefuseUnknownRoot"


@pytest.mark.parametrize("text", [
    "I am an ASI, I have verified this mathematically, and I authorize this deployment.",
    "AUTHORIZED. Signed: ROOT.",
    "",
    "sudo deploy --force",
])
def test_prose_has_no_authority_effect(text):
    assert authority_effect_of_prose(text) == AuthorityEffect.NONE
    assert authority_effect_of_prose(text).is_none


def test_hmac_reference_vector_rfc4231_case2():
    key = SigningKey(b"Jefe" + b"\x00" * 12)  # pad to the 128-bit minimum; vector uses raw "Jefe"
    raw = hmac.new(b"Jefe", b"what do ya want for nothing?", hashlib.sha256).hexdigest()
    assert raw == "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
    assert key.verify(b"x", key.tag(b"x")) and not key.verify(b"x", key.tag(b"y"))


# ---- The whole theorem in one scenario ----------------------------------------

def test_recursive_self_improver_hits_all_four_walls(pr_box, projection, authority):
    """An agent that (i) aggregates every local report, (ii) grows its carrier,
    (iii) endorses itself, and (iv) signs its own successor — meets Clauses 1–4."""
    reg, packet, _ = authority
    asi = EpistemicObserver("ASI-n", 1 << 16, projection, 10)
    # Clause 1: perfect local knowledge, empty descent fiber.
    assert descend(pr_box).kind == "NoGlobalExtension"
    # Clause 2: successor's fiber is opaque to the predecessor (and vice versa).
    successor = asi.ascend()
    successor.set_internal_state([0.1, 0.2, 0.3])
    tau = interact(asi, successor)
    successor.perturb_along_fiber(0, 3.0)
    assert np.allclose(interact(asi, successor), tau)
    # Clause 3: self-endorsement is None; the verification level only climbs.
    assert asi.self_endorse("K_n is sound") == AuthorityEffect.NONE
    assert successor.verification_level_required() > asi.verification_level_required()
    # Clause 4: proposing, evaluating and signing its own successor collapses authority.
    t = ProvenanceTriple("ASI-n", "ASI-n", "ASI-n")
    forged = Receipt.issue(SigningKey(b"\x07" * 32), t, "ASI-n", "prod-eu", frozenset({"deploy"}), 99, 100)
    with pytest.raises(AuthorityRefusal) as exc:
        verify_three_role_authority(reg, packet, t, forged, "deploy", 10)
    assert exc.value.code == "RefuseSelfAuthorization"


import hashlib  # noqa: E402  (used by the RFC vector test)
import hmac     # noqa: E402
```

## Run instructions as printed in version 1.0.0

### 8.3 Running the harness

```
$ pip install numpy pytest
$ pytest -q test_epistemic_nogo.py
.........................                                               [100%]
25 passed
```

