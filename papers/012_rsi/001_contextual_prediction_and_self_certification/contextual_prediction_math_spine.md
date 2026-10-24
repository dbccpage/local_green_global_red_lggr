# Canonical math spine

Contextual Prediction and Self-Certification

Each entry is an expression, not a standalone truth assertion. Domains, assumptions, and quantified statements belong to its linked manuscript context and claim ledger. The build requires every occurrence to agree with this spine before conversion. Equation IDs persist when an entry is edited; content hashes and edition bindings change.

Formalization status: not inferred from LaTeX. Existing Lean results cover only the statements identified in the manuscript and claim ledger. No generated proof is asserted.

## E0001 {#870fa302-c731-57b3-83ef-f2eb70ad0950}

$$
X
$$

## E0002 {#ecfd41a3-696d-51e5-ad68-25cdf17204a8}

$$
C
$$

## E0003 {#41b424ab-0740-5167-9c1e-c13909f37dda}

$$
e_C
$$

## E0004 {#a9e4aca5-2ebb-5cd0-9399-74e9fe6daf90}

$$
G
$$

## E0005 {#1f6a712c-9e8f-5240-bc41-b971cb52a4ce}

$$
p
$$

## E0006 {#7d55d94e-9d6a-548c-b871-78342445a1b4}

$$
A
$$

## E0007 {#00c3d3c6-6e29-5f55-8472-bf0ef2f1b8b4}

$$
Ap=e,\qquad p_g\geq 0,\qquad \sum_{g\in G}p_g=1.
$$

## E0008 {#b636a29a-c614-5ad7-9670-e0519e2c9b66}

$$
e
$$

## E0009 {#6bf3f98c-7884-5b65-95fb-f73f770b4e2f}

$$
d(e)=\min_{p\in\Delta(G)}\lVert Ap-e\rVert_1>0.
$$

## E0010 {#1e96d7d0-d375-53a3-a9ad-8dbc8691ac42}

$$
\lVert y\rVert_\infty\leq 1,\qquad
\langle y,e\rangle-\max_{g\in G}\langle y,A\delta_g\rangle=d(e).
$$

## E0011 {#72e012cf-bd16-5ab3-976a-b61a827ab9f5}

$$
a_x\mathbin{\mathrm{xor}} b_y=x\mathbin{\mathrm{and}} y.
$$

## E0012 {#2ac5908d-11dd-5df9-b03f-cfcad0a8325c}

$$
\pi:S\to B
$$

## E0013 {#d2d5195c-5166-56b4-9fc7-76cd56ba82f7}

$$
q:S\to Q
$$

## E0014 {#30b8f4aa-e285-51a0-8a03-1b1b6c78d629}

$$
\pi(s)=\pi(t),\quad q(s)\ne q(t)
\quad\Longrightarrow\quad
\neg\exists f\;\forall z,\ f(\pi(z))=q(z).
$$

## E0015 {#1e1ce7b0-32f3-545f-80c7-e9e8191fe6dc}

$$
U
$$

## E0016 {#7458b5e0-08bf-5e6d-a599-7b6fd777d68b}

$$
F_u:S\to S
$$

## E0017 {#e0700670-5adb-58ca-b444-1943f3cd5e9f}

$$
u
$$

## E0018 {#73778d09-0c68-5605-82a4-7062bffeee2e}

$$
\forall u,s,t,\quad \pi(s)=\pi(t)\Longrightarrow
\pi(F_u(s))=\pi(F_u(t)).
$$

## E0019 {#0fc56a78-2730-50d7-9b47-cd7a16b9cda9}

$$
\pi\circ F_u=\overline F_u\circ\pi.
$$


## E0020 {#1bb98993-9058-5440-9eee-383f4fc6c318}

$$
\langle y,A\delta_g\rangle+z\leq0\quad(g\in G),\qquad
\langle y,e\rangle+z=d(e).
$$


## E0021 {#052afb44-9418-579a-b8b2-c83c431614fc}

$$
Ap-u+v=e,\qquad p,u,v\geq0,\qquad \sum_g p_g=1,
\qquad\min\sum_i(u_i+v_i).
$$


## E0022 {#b092bf50-72b4-5418-8c33-34fd1d010a8c}

$$
\ell^1
$$


## E0023 {#7954c186-1650-5260-8cd5-7d17386166f8}

$$
E_{k+1}\le L E_k+r_k,
\qquad
E_n\le L^n E_0+\sum_{k=0}^{n-1}L^{n-1-k}r_k.
$$


## E0024 {#0d03c1b0-f71b-5e95-9c56-ca1bcc56ad90}

$$
E_n\le E_0+n\eta,\qquad
n\le\frac{\varepsilon-E_0}{\eta}\Longrightarrow E_n\le\varepsilon.
$$


## E0025 {#b6c42c00-b56a-524b-aa9d-0c83658877b0}

$$
|\Delta O(t)|\le\lVert O\rVert_\infty
\left(E_0+\int_0^t\lVert\mathcal R(s)\rVert_1\,ds\right).
$$


## E0026 {#4fbaa645-ea32-5c8a-a9aa-6a7980162813}

$$
t\le\frac{\varepsilon/\lVert O\rVert_\infty-E_0}{r}.
$$


## E0027 {#3955081e-8366-582e-84f8-3242f944b079}

$$
\sum_i|O_i(x)-O_i(y)|\le
\left(\sum_i\lVert O_i\rVert\right)\lVert x-y\rVert.
$$


## E0028 {#993a3640-b991-5898-bb89-92cd334cd6f1}

$$
\sum_i|e_i-\widehat e_i|\le\rho
\Longrightarrow
\lVert Ap-e\rVert_1\ge
\max\{0,\langle y,\widehat e\rangle+z-\rho\}.
$$


## E0029 {#8d92bff2-2c0c-5436-b593-a4d2fd4e0adc}

$$
D(t)\ge\nu t-Kt^2,\quad
C(t)\le ct,\quad R(t)\ge D(t)-C(t)
\Longrightarrow R(t)\ge(\nu-c)t-Kt^2.
$$


## E0030 {#496d20a9-4eeb-5e4e-bd7d-822f38542bb4}

$$
r>0
$$

## E0031 {#ecdb6e40-04c6-57d0-a5c5-f8ecc97bacf9}

$$
\lVert O\rVert_\infty>0
$$

## E0032 {#6a0eeb08-6884-58e7-8416-677ac55091d7}

$$
r=0
$$

## E0033 {#894a1d4b-cd8a-5293-807a-53381f7868ba}

$$
\lVert O\rVert_\infty E_0\le\varepsilon.
$$

## E0034 {#d7058c49-a5de-5c9a-93d4-f9dc9c2d0218}

$$
\bar e
$$

## E0035 {#1356c3c6-292f-59e3-a2b6-a0b8fbbee27e}

$$
\rho+\lVert\bar e-\widehat e\rVert_1,
$$

## E0036 {#9b0038e9-c884-5efa-bc84-601f7b751cc0}

$$
\min c^T x,\qquad Ax=b,\qquad x\ge0.
$$

## E0037 {#8b06dbe4-65b0-57e9-be90-d54216d079af}

$$
A^T y\ge0,\qquad b^T y<0
$$

## E0038 {#f603653c-a35d-5d4e-bafd-f9527b725a15}

$$
Ax_0=b,\quad x_0\ge0,\quad d\ge0,\quad Ad=0,\quad c^Td<0
$$

## E0039 {#2c2fb2d9-647c-5184-a487-21ea56aac391}

$$
x(t)=x_0+td,\qquad c^Tx(t)=c^Tx_0+t c^Td\quad(t\ge0).
$$

## E0040 {#c09a7a45-ae97-54bb-a654-82be4e73b9bd}

$$
\begin{aligned}
E(t)&=e^{\Lambda(t,0)}E_0+
\int_0^t e^{\Lambda(t,s)}\eta(s)\,ds\\
&\quad+\sum_{\tau_j\le t}e^{\Lambda(t,\tau_j)}\epsilon_j,\\
\Lambda(t,s)&=\int_s^t\lambda(u)\,du.
\end{aligned}
$$

## E0041 {#b64d1ae7-2ddc-57cb-a5f5-065002a14542}

$$
\begin{gathered}
|V_a-s_a|\le b\ (\forall a),\quad s_a\le s_{\widehat a}\ (\forall a)\\
\Longrightarrow\quad V_a-V_{\widehat a}\le2b\ (\forall a).
\end{gathered}
$$

## E0042 {#ce27f490-bc9b-5512-9a38-7b1c8428e173}

$$
b=KE+\zeta.
$$

## E0043 {#1ad70303-a6d9-4931-a207-5e701665c5bb}

$$
e(t)=\lVert x(t)-\widehat x(t)\rVert\le E(t)
$$

## E0044 {#a26d749d-ad8c-5675-86a6-3bb6ea4d16bf}

$$
0\le L_i\le1\quad\Longrightarrow\quad
\left|\sum_i p_i L_i-\sum_i q_i L_i\right|
\le\operatorname{TV}(p,q).
$$

## E0045 {#f5d3a0f3-ad3e-5434-8942-b0c37211713e}

$$
\delta(E,F)=\inf_K\sup_\theta
\operatorname{TV}(K E_\theta,F_\theta).
$$

## E0046 {#c5b99839-042c-5317-9725-63dd06356ed6}

$$
\operatorname{TV}(p,q)=\frac12\sum_i|p_i-q_i|.
$$

## E0047 {#9b57aa9f-2266-55e8-b8c5-f9b8d11e0372}

$$
d(o)=\frac{\ell(o)+u(o)}2,\qquad
R=\frac12\max_{r(x)=r(y)}|f(x)-f(y)|.
$$

## E0048 {#4923c56c-b0bf-5863-a1e4-8eaddd4a4f3c}

$$
q_0=(0,0,1,1),\quad q_1=(0,1,0,0),\quad
q_2=(0,0,0,1),\quad f=(0,1,2,3).
$$
