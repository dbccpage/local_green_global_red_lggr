"""Independent finite Clifford/Born replay of the smallest smoothed Gram member.

The maximally-entangled trace identity avoids allocating a 65536-square density
matrix.  This is a numerical check, not the arbitrary-size quantum proof.
"""
import json
import numpy as np
from smoothed_gram import certificate, behavior


def clifford(d):
    if d < 2 or d % 2:
        raise ValueError("an even positive vector dimension is required")
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.diag([1, -1]).astype(complex)
    I = np.eye(2, dtype=complex)
    out = []
    for j in range(d//2):
        for pauli in (X, Y):
            mat = np.ones((1, 1), dtype=complex)
            for t in range(d//2):
                mat = np.kron(mat, Z if t < j else pauli if t == j else I)
            out.append(mat)
    return np.array(out)


def replay():
    cert = certificate(2)
    f = np.array([float(x) for x in cert["profile"]])
    d, n = cert["dimension"], cert["settings"]
    gamma = clifford(d)
    hdim = gamma.shape[1]
    vectors = np.array([np.roll(f, -j)/np.linalg.norm(f) for j in range(2*n)])
    observables = np.einsum("ij,jkl->ikl", vectors, gamma)
    errors = []
    eye = np.eye(hdim)
    for obs in observables:
        errors += [np.max(np.abs(obs-obs.conj().T)),
                   np.max(np.abs(obs@obs-eye)), abs(np.trace(obs))/hdim]
    # Bob uses transpose; <Phi| A tensor B |Phi> = tr(A B^T)/dim.
    for x in range(n):
        for y in range(n):
            for a in (-1, 1):
                for b in (-1, 1):
                    alice = (eye+a*observables[2*x])/2
                    bob = ((eye+b*observables[2*y+1])/2).T
                    born = np.einsum("ij,ij->", alice, bob)/hdim
                    errors.append(abs(born-float(behavior(cert,x,y,a,b))))
    error = float(max(errors))
    if error >= 5e-13:
        raise AssertionError(error)
    return {"scope": "numerical Clifford/Born replay; not an all-size formal proof",
            "k": 2, "settings_per_party": n, "complete_contexts": n*n,
            "local_hilbert_dimension": hdim, "born_cells": 4*n*n,
            "maximum_absolute_error": error, "tolerance": 5e-13}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
