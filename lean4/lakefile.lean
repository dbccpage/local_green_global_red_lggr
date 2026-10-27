import Lake
open Lake DSL

package «LGGR» where
  version := v!"0.1.0"
  buildDir := "b"

@[default_target]
lean_lib «LGGR» where
  srcDir := "."
  roots := #[
    `LggrVII,
    `LggrVIII,
    `PrimitiveDifference,
    `WorldLGGRWitness,
    `CheckAxioms
  ]
