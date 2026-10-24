import Lake
open Lake DSL

package «LGGR2» where
  version := v!"1.3.0"
  buildDir := "b"

@[default_target]
lean_lib «LGGR2» where
  srcDir := "."
  roots := #[
    `primitive_difference,
    `«01_certified_closure»,
    `«02_boundary_sufficiency»,
    `«03_non_additivity»,
    `«04_carrier_boundary_obstruction»,
    `«05_detector_adequacy»,
    `core,
    `lggr_ii_organizational_gluing,
    -- The axiom census. It must be a build root: a module nothing imports is
    -- never elaborated, so without this line `lake build` emits no
    -- `#print axioms` report and the package's axiom claim is unwitnessed by
    -- its own build.
    `check_axioms
  ]
