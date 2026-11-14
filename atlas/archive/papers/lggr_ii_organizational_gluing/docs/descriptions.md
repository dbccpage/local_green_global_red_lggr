# Repository and archive descriptions

## Primary description

An interface can pass every local check and fail its global check. This paper
models the gap using Boolean local evaluators E_i, a global evaluator E_G, and
the defect Delta_E = E_G - product_i E_i. The value -1 is exactly the
local-green/global-red configuration. A finite counterexample shows that a
boundary representation which recovers E_G does not thereby imply evaluator
factorization. A stronger carrier result shows that if the global evaluator
changes between two traces with the same retained local carrier, then no
evaluator on carrier quotient classes can reproduce it. Lean 4 checks the
Boolean and quotient theorems; Python implements the audit model, rejects
malformed states, runs break-and-recover mutations, and generates the figures.
A checked-in uv lockfile pins the tested Python environment. One notebook moves
from the truth table through interactive widgets to the quotient obstruction
and executes headlessly in the test suite. Named examples in the code are
illustrative assignments, not empirical audits or predictions.

## Secondary description

A finite Boolean account of why passing local evaluators need not compose into
a passing global evaluator, with Lean proofs, tested Python, deterministic
figures, and a clean-kernel interactive notebook.

## Archive contents

- Markdown, TeX, and PDF forms of the paper;
- claim ledger, canonical Lean claim map, and claim-to-code map;
- Lean sources and the current axiom census;
- the byte-identical shared obstruction-paper-kit preamble;
- locked Python environment, implementation, tests, and figure generator;
- one public Jupyter notebook;
- deterministic checksum and dated-archive builders; and
- CC BY 4.0 documentation plus Apache 2.0 code licensing.
