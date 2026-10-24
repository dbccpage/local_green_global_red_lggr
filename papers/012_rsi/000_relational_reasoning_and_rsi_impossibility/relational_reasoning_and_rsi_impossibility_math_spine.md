# Canonical math spine

Relational Reasoning, Memory, and Embedded Knowledge

Each entry is an expression, not a standalone truth assertion. Domains, assumptions, and quantified statements belong to its linked manuscript context and claim ledger. The build requires every occurrence to agree with this spine before conversion. Equation IDs persist when an entry is edited; content hashes and edition bindings change.

Formalization status: not inferred from LaTeX. Existing Lean results cover only the statements identified in the manuscript and claim ledger. No generated proof is asserted.

## E0001 {#7b565a20-ee2e-50a9-a7ed-dd767c7d472e}

$$
r:X\to O,\qquad f:X\to Y.
$$

## E0002 {#83bca2c6-659a-548e-afbd-3a3f54749941}

$$
C_r(x)=\{y:r(y)=r(x)\},\qquad
K_r p(x)\ \Longleftrightarrow\ \forall y\in C_r(x),\ p(y).
$$

## E0003 {#e9e26d68-d548-5e1c-adad-f9278376aa1e}

$$
K_r p(x)\Rightarrow p(x),\qquad
K_r p(x)\Rightarrow K_r(K_r p)(x),\qquad
K_r(r=r(x))(x).
$$

## E0004 {#cbb7ff9a-fd48-5f63-9b67-f2957706e523}

$$
\exists d:O\to Y\;\forall x,\ d(r(x))=f(x)
\quad\Longleftrightarrow\quad
\forall x,y,\ r(x)=r(y)\Rightarrow f(x)=f(y).
$$

## E0005 {#5ec0e1c6-7e1b-517c-a28c-044090595ba9}

$$
x\sim_F y\quad\Longleftrightarrow\quad
\forall w\in A^*,\ q(F_w(x))=q(F_w(y)).
$$

## E0006 {#d11f2f28-9d9a-53a4-95ab-84d48123e2c0}

$$
d(m(x))=q(x),\qquad m(F_a(x))=U_a(m(x)).
$$

