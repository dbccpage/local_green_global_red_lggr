# Mutation audit

**Mutation:** change entry `(0, 1)` of `[[1, 0]]` by `+0.25`.  
**Witness:** `k = [0, 1]`.  
**Test:** `test_mutation_breaks_and_restoration_recovers_kernel_claim`.

Expected sequence:

1. baseline accepts the kernel statement because `Qk = 0`;
2. the mutated watcher observes `0.25`, so the statement fails;
3. restoring the original entry makes `Qk = 0` again.

The production function also rejects a witness that was never hidden, an
out-of-range matrix entry, and a perturbation no larger than the declared
tolerance. The audit supports one targeted falsifier only.
