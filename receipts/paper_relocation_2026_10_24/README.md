# Paper relocation, 24 October 2026

The author requested the RSI and Bell paper estates be moved from the_symbol_game to lggr/papers. `before_move.json` records all non-cache bytes, including release ZIPs; `move_verification.json` verifies exact equality after the native same-volume moves and absence of the source paths. Cache directories moved too but were excluded from the content inventory.

The source navigation and active build references were removed. Dated, revision-bound review receipts remain historical evidence rather than live links. `relocation_source_links_before.zip` preserves the replaced navigation bytes, and `relocation_source_links.json` records their before/after hashes. The retired Woland RSI harness retains its original source for history; use the relocated papers' own verifiers for current validation.

The chat's worktree was archived with a recoverable Git snapshot after verifying its clean and pushed state. Its unique Bell v0.7.1 ZIP was preserved with the current Bell archives. The two merged chat branches were removed locally; the Bell remote branch was deleted with an exact-SHA lease and the retirement remote branch was already absent. Other worktrees and the user's current branch were left intact.

The migration is local filesystem work. It does not commit or publish either repository. Existing edits to lggr/__init__.py and lggr/streaming.py were verified unchanged. The destination verification logs distinguish package binding/certificate checks from the separate complete Bell cold-extraction replay. RSI Lean builds were not repeated for a byte-preserving directory relocation.

The shared papers/README.md changed during the verification run. Its final contents were left in place; papers/rsi_and_bell_packages.md supplies the migration navigation without overwriting the shared index.
