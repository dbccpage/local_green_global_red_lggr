import Lake
open Lake DSL

package «relational_rsi_impossibility» where
  version := v!"1.2.3"
  moreLeanArgs := #["-j", "1"]

@[default_target]
lean_lib «RelationalRsiImpossibility» where
  srcDir := "."
  roots := #[`Core, `LiveMemory, `RsiImpossible, `RelationalRsiNoGo, `EmbeddedLimits, `MemoryImplementation, `PrefixBounds, `ReviewCountermodels]
