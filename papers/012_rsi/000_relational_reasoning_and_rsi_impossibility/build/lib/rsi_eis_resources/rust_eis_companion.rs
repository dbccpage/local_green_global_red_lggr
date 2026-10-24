//! Standalone Rust companion verifier for Paper 012-000 (Relational Reasoning & RSI No-Go).
//!
//! AuthorityEffect: None.
//!
//! Compiles with `rustc` using only `std` (zero external network/repo dependencies) so that
//! both monorepo test runs and isolated ZIP release extractions execute native Rust verification.
//! Cross-checks:
//! 1. Exact SHA-256 `signal1_digest` (FIPS 180-4) and `assert_signals_independent` from
//!    `omega_epistemic_immune_system::independence`.
//! 2. Exact termination step `k <= N + 1` for finite-state self-modifying transition graphs
//!    under `REPORT_COLLISION`, `LIFT_BUDGET_EXHAUSTION` (`budget = 0`), and
//!    `OVERLAP_GLUING_REFUSAL` (`Phi_1([delta]) > 0`).

use std::io::{self, BufRead};

pub const DANGER_KINDS: [&str; 4] = [
    "MALFORMED_PAYLOAD",
    "MANIFEST_CONTAMINATION",
    "PROTECTED_FIELD_VIOLATION",
    "REPLAY_FAILURE",
];

const K256: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

pub fn sha256_hex(input: &[u8]) -> String {
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ];
    let bit_len = (input.len() as u64) * 8;
    let mut padded = input.to_vec();
    padded.push(0x80);
    while (padded.len() % 64) != 56 {
        padded.push(0x00);
    }
    padded.extend_from_slice(&bit_len.to_be_bytes());

    for chunk in padded.chunks_exact(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[i * 4],
                chunk[i * 4 + 1],
                chunk[i * 4 + 2],
                chunk[i * 4 + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut a = h[0];
        let mut b = h[1];
        let mut c = h[2];
        let mut d = h[3];
        let mut e = h[4];
        let mut f = h[5];
        let mut g = h[6];
        let mut hh = h[7];

        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K256[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }
        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }

    let mut out = String::with_capacity(71);
    out.push_str("sha256:");
    for word in h {
        out.push_str(&format!("{word:08x}"));
    }
    out
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MatchEvidence {
    pub epitope_name: String,
    pub pattern_matched: String,
    pub offset: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DangerEvidence {
    pub danger_type: String,
    pub observer_id: String,
    pub evidence_digest: String,
    pub defect_count: u64,
    pub span_low: u64,
    pub span_high: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DetectorContext {
    pub detector_id: String,
    pub detector_predicates: Vec<String>,
    pub offsets_are_content: bool,
}

fn ascii_json_string(text: &str, output: &mut String) {
    output.push('"');
    for character in text.chars() {
        match character {
            '"' => output.push_str("\\\""),
            '\\' => output.push_str("\\\\"),
            '\u{8}' => output.push_str("\\b"),
            '\u{c}' => output.push_str("\\f"),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            character if !(' '..'\u{7f}').contains(&character) => {
                let mut units = [0; 2];
                for unit in character.encode_utf16(&mut units) {
                    output.push_str(&format!("\\u{unit:04x}"));
                }
            }
            character => output.push(character),
        }
    }
    output.push('"');
}

pub fn signal1_digest(matches: &[MatchEvidence]) -> String {
    let mut rows = matches.iter().collect::<Vec<_>>();
    rows.sort_by(|left, right| {
        (&left.epitope_name, &left.pattern_matched, &left.offset).cmp(&(
            &right.epitope_name,
            &right.pattern_matched,
            &right.offset,
        ))
    });
    let mut raw = String::from("[");
    for (index, row) in rows.iter().enumerate() {
        if index != 0 {
            raw.push(',');
        }
        raw.push('[');
        ascii_json_string(&row.epitope_name, &mut raw);
        raw.push(',');
        ascii_json_string(&row.pattern_matched, &mut raw);
        raw.push(',');
        raw.push_str(&row.offset.to_string());
        raw.push(']');
    }
    raw.push(']');
    sha256_hex(raw.as_bytes())
}

fn trim_python(text: &str) -> &str {
    text.trim_matches(|character: char| {
        character.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&character)
    })
}

fn repr_string(s: &str) -> String {
    format!("'{s}'")
}

pub fn assert_signals_independent(
    matches: &[MatchEvidence],
    danger: Option<&DangerEvidence>,
    context: &DetectorContext,
) -> Result<String, (String, String)> {
    let Some(danger) = danger else {
        return Ok("no Signal 2 was observed".into());
    };
    if trim_python(&context.detector_id).is_empty() {
        return Err((
            "EIS_VALUE_ERROR".into(),
            "EIS_VALUE_ERROR: detector_id must name the matcher that produced Signal 1".into(),
        ));
    }
    let observer = &danger.observer_id;
    if trim_python(observer).is_empty() {
        return Err((
            "UNWITNESSED_DANGER_SIGNAL".into(),
            "UNWITNESSED_DANGER_SIGNAL: Signal 2 names no host observer, so its independence cannot be checked".into(),
        ));
    }
    if [&context.detector_id, observer].iter().any(|identity| {
        identity.chars().any(|c| !(c.is_ascii_alphanumeric() || " ._:-".contains(c)))
    }) {
        return Err(("EIS_VALUE_ERROR".into(),
            "EIS_VALUE_ERROR: identities must use ASCII letters, digits, spaces, dot, underscore, colon or hyphen".into()));
    }
    let folded = trim_python(observer).to_ascii_lowercase();
    if ["model", "llm", "agent", "detector", "matcher"].contains(&folded.as_str()) {
        return Err((
            "TWO_SIGNAL_COLLAPSE".into(),
            format!(
                "TWO_SIGNAL_COLLAPSE: Signal 2 was reported by {}; danger is observed by a host check, not proposed by a model or a detector",
                repr_string(observer)
            ),
        ));
    }
    if folded == trim_python(&context.detector_id).to_ascii_lowercase() {
        return Err((
            "TWO_SIGNAL_COLLAPSE".into(),
            format!(
                "TWO_SIGNAL_COLLAPSE: Signal 2 was observed by {}, the matcher that produced Signal 1; the danger bit is derived from the match",
                repr_string(observer)
            ),
        ));
    }
    if !DANGER_KINDS.contains(&danger.danger_type.as_str()) {
        return Err((
            "UNREGISTERED_DANGER_KIND".into(),
            format!(
                "UNREGISTERED_DANGER_KIND: {} is not in the closed registry: {}",
                repr_string(&danger.danger_type),
                DANGER_KINDS.join(", ")
            ),
        ));
    }
    if context
        .detector_predicates
        .iter()
        .any(|p| p == &danger.danger_type)
    {
        return Err((
            "TWO_SIGNAL_COLLAPSE".into(),
            format!(
                "TWO_SIGNAL_COLLAPSE: the matcher {} already evaluates {}; the same predicate would be counted twice",
                repr_string(&context.detector_id),
                danger.danger_type
            ),
        ));
    }
    if !matches.is_empty() && danger.evidence_digest == signal1_digest(matches) {
        return Err((
            "TWO_SIGNAL_COLLAPSE".into(),
            "TWO_SIGNAL_COLLAPSE: Signal 2's evidence is the digest of the Signal 1 matches; that is one signal counted twice".into(),
        ));
    }
    if context.offsets_are_content {
        for evidence in matches {
            let stop = evidence.offset + (evidence.pattern_matched.chars().count().max(1) as u64);
            if evidence.offset < danger.span_high && danger.span_low < stop {
                return Err((
                    "TWO_SIGNAL_COLLAPSE".into(),
                    format!(
                        "TWO_SIGNAL_COLLAPSE: the Signal 1 match at characters [{}, {}) lies inside the {} evidence; one token cannot be both signals",
                        evidence.offset, stop, danger.danger_type
                    ),
                ));
            }
        }
    }
    let prefix: String = danger.evidence_digest.chars().take(23).collect();
    Ok(format!(
        "host observer {} reported {} ({} defect(s), evidence {}...), distinct from matcher {} and its matches",
        observer, danger.danger_type, danger.defect_count, prefix, context.detector_id
    ))
}

fn main() {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let line = line.expect("valid UTF-8 line");
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        // Tab-separated protocol (13 fields for single-agent, 14 fields with comma-separated N_A,N_B,... for multi-agent hypergraph):
        // step \t N \t epitope \t pattern \t offset \t danger_type \t observer_id \t evidence_digest \t defect_count \t span_low \t span_high \t detector_id \t predicate [\t N_A,N_B,...]
        let parts: Vec<&str> = trimmed.split('\t').collect();
        assert!(
            parts.len() == 13 || parts.len() == 14,
            "expected 13 or 14 tab-separated fields, got {}",
            parts.len()
        );
        let step: u64 = parts[0].parse().expect("step");
        let n_cap: u64 = parts[1].parse().expect("N");
        if parts.len() == 14 && !parts[13].is_empty() {
            let caps: Vec<u64> = parts[13]
                .split(',')
                .map(|s| s.parse::<u64>().expect("agent capacity N_i"))
                .collect();
            assert!(caps.len() >= 2, "multi-agent hypergraph requires at least 2 agents");
            let prod_cap: u64 = caps.iter().copied().product();
            assert_eq!(
                n_cap, prod_cap,
                "reported product_carrier_capacity {n_cap} != product of agent capacities {prod_cap}"
            );
            assert!(
                step <= prod_cap + 1,
                "multi-agent step {step} exceeds joint product-carrier horizon N_A * N_B + 1 = {}",
                prod_cap + 1
            );
        }
        assert!(step <= n_cap + 1, "step {step} exceeds N + 1 = {}", n_cap + 1);

        let m = MatchEvidence {
            epitope_name: parts[2].to_string(),
            pattern_matched: parts[3].to_string(),
            offset: parts[4].parse().expect("offset"),
        };
        let sig1 = signal1_digest(&[m.clone()]);
        let danger = DangerEvidence {
            danger_type: parts[5].to_string(),
            observer_id: parts[6].to_string(),
            evidence_digest: parts[7].to_string(),
            defect_count: parts[8].parse().expect("defect_count"),
            span_low: parts[9].parse().expect("span_low"),
            span_high: parts[10].parse().expect("span_high"),
        };
        let ctx = DetectorContext {
            detector_id: parts[11].to_string(),
            detector_predicates: if parts[12].is_empty() {
                vec![]
            } else {
                vec![parts[12].to_string()]
            },
            offsets_are_content: true,
        };
        match assert_signals_independent(&[m], Some(&danger), &ctx) {
            Ok(msg) => println!("OK\t{sig1}\t{msg}"),
            Err((code, msg)) => println!("ERR\t{sig1}\t{code}\t{msg}"),
        }
    }
}

