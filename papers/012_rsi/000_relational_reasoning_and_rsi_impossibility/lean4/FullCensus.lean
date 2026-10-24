import Core
import EmbeddedLimits
import LiveMemory
import MemoryImplementation
import PrefixBounds
import RelationalRsiNoGo
import ReviewCountermodels
import RsiImpossible
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[`Core, `EmbeddedLimits, `LiveMemory, `MemoryImplementation, `PrefixBounds, `RelationalRsiNoGo, `ReviewCountermodels, `RsiImpossible]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if modules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← collectAxioms name
        if axioms.isEmpty then
          logInfo m!"'{name}' does not depend on any axioms"
        else
          let names := String.intercalate ", " (axioms.toList.map toString)
          logInfo m!"'{name}' depends on axioms: [{names}]"
