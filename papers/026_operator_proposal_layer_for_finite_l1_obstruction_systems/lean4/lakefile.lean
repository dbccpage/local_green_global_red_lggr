import Lake
open Lake DSL

package «operator_proposal» where
  version := v!"0.1.0"

@[default_target]
lean_lib «OperatorProposal» where
  srcDir := "."
  roots := #[`Proposal, `Census]
