import Lake
open Lake DSL

package «epistemic_no_go» where
  version := v!"1.8.3"
  extraDepTargets := #[`vendorArchive]
  moreLeanArgs := #["-j", "1"]

require «rsi_mathlib_vendor» from "vendor"

target vendorArchive pkg : System.FilePath :=
  inputBinFile (pkg.dir / "vendor" / "dependencies.tar.gz")

@[default_target]
lean_lib «EpistemicNoGo» where
  srcDir := "."
  roots := #[`Core, `LiveMemory, `ResultI, `ResultII, `ResultIII, `ResultIV, `Bridge, `ContextualDuality, `RationalCertificates, `Simplex, `CertifiedOutcomes, `SimplexDriver, `ErrorBudget, `MindContracts, `EmbeddedLimits, `EmbeddedQuantitative, `QueryBudget]
