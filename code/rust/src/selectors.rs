//! Host elimination rule over a finite hypothesis space.
//!
//! Each hypothesis predicts an outcome for every check and has a contract verdict.
//! Observations eliminate hypotheses whose prediction disagrees. The host accepts
//! only if every surviving hypothesis passes, rejects only if every one fails, defers
//! on a mix, and reports a model mismatch if none survives.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    Accept,
    Reject,
    Defer,
    ModelMismatch,
}

pub struct Space {
    /// predicted[h][c]: outcome of check c under hypothesis h.
    pub predicted: Vec<Vec<u8>>,
    /// verdict[h]: does the system meet its contract under hypothesis h.
    pub verdict: Vec<bool>,
}

impl Space {
    pub fn alive(&self, obs: &[(usize, u8)]) -> Vec<usize> {
        (0..self.verdict.len()).filter(|h| obs.iter().all(|(c, r)| self.predicted[*h][*c] == *r)).collect()
    }

    pub fn host_rule(&self, obs: &[(usize, u8)]) -> Decision {
        let alive = self.alive(obs);
        if alive.is_empty() {
            return Decision::ModelMismatch;
        }
        let pass = alive.iter().filter(|h| self.verdict[**h]).count();
        if pass == alive.len() {
            Decision::Accept
        } else if pass == 0 {
            Decision::Reject
        } else {
            Decision::Defer
        }
    }

    /// Accept/reject pairs still alive: the LGGR selector's quantity to drive to zero.
    pub fn verdict_pairs(&self, alive: &[usize]) -> usize {
        let p = alive.iter().filter(|h| self.verdict[**h]).count();
        p * (alive.len() - p)
    }
}
