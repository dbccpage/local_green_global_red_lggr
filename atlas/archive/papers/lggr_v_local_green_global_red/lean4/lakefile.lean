import Lake
open Lake DSL

package «observer_visibility» where
  version := v!"0.1.0"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "56a005855ea17e0b0958f73ec801ae140b0a1679"

@[default_target]
lean_lib «ObserverVisibility» where
  srcDir := "."
  roots := #[`observer_visibility, `po000_l004_observer_visibility]
