import Lake
open Lake DSL

package «authority_firewall» where
  version := v!"0.1.0"

@[default_target]
lean_lib «AuthorityFirewall» where
  srcDir := "."
  roots := #[`ResidualNonCreation, `Census]
