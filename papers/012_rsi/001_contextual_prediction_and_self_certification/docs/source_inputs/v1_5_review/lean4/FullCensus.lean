import Bridge
import ContextualDuality
import Core
import ErrorBudget
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
  let modules : Array Name := #[`Bridge, `ContextualDuality, `Core, `ErrorBudget, `RationalCertificates, `ResultI, `ResultII, `ResultIII, `ResultIV, `Simplex, `SimplexDriver]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if modules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← collectAxioms name
        if axioms.isEmpty then
          logInfo m!"'{name}' does not depend on any axioms"
        else
          let names := String.intercalate ", " (axioms.toList.map toString)
          logInfo m!"'{name}' depends on axioms: [{names}]"
