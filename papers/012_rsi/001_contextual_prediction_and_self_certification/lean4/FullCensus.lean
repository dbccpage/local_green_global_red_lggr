import Bridge
import CertifiedOutcomes
import ContextualDuality
import Core
import EmbeddedLimits
import EmbeddedQuantitative
import ErrorBudget
import LiveMemory
import MindContracts
import QueryBudget
import RationalCertificates
import ResultI
import ResultII
import ResultIII
import ResultIV
import Simplex
import SimplexDriver
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let modules : Array Name := #[`Bridge, `CertifiedOutcomes, `ContextualDuality, `Core, `EmbeddedLimits, `EmbeddedQuantitative, `ErrorBudget, `LiveMemory, `MindContracts, `QueryBudget, `RationalCertificates, `ResultI, `ResultII, `ResultIII, `ResultIV, `Simplex, `SimplexDriver]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if modules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← collectAxioms name
        if axioms.isEmpty then
          logInfo m!"'{name}' does not depend on any axioms"
        else
          let names := String.intercalate ", " (axioms.toList.map toString)
          logInfo m!"'{name}' depends on axioms: [{names}]"
