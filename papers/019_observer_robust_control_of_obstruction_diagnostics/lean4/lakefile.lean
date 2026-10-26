import Lake
open Lake DSL

package «observer_robust_control» where
  version := v!"0.1.0"

@[default_target]
lean_lib «ObserverRobustControl» where
  srcDir := "."
  roots := #[
    `ObserverRobustControlCore,
    `JointDetectorAdequacy,
    `Census
  ]
