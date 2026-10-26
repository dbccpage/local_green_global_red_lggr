import Lake
open Lake DSL

package «representation_abundance» where
  version := v!"0.1.0"

@[default_target]
lean_lib «RepresentationAbundance» where
  srcDir := "."
  roots := #[`Representation, `Census]
