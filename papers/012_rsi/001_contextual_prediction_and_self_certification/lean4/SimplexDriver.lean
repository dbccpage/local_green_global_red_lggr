import CertifiedOutcomes
import Lean

open Lean EpistemicNoGo.Simplex
open EpistemicNoGo.CertifiedOutcomes
namespace EpistemicNoGo.SimplexDriver

structure Input where
  costs : List String
  matrix : List (List String)
  rhs : List String
  budget : Nat
  deriving FromJson

def rational (s : String) : Except String ℚ := do
  match s.splitOn "/" with
  | [a, b] =>
    let some a := a.toInt? | throw "invalid numerator"
    let some b := b.toNat? | throw "invalid denominator"
    if b = 0 then throw "zero denominator"
    return (a : ℚ) / b
  | [a] =>
    let some a := a.toInt? | throw "invalid integer"
    return (a : ℚ)
  | _ => throw "invalid rational"

def evaluate (input : Input) : Except String Json := do
  let costs ← input.costs.mapM rational
  let rhs ← input.rhs.mapM rational
  let matrix ← input.matrix.mapM (List.mapM rational)
  if matrix.length ≠ rhs.length ∨ matrix.any (fun r => r.length ≠ costs.length) then
    throw "invalid shape"
  let P : Problem rhs.length costs.length :=
    { A := fun i j => (matrix[i.val]?.getD [])[j.val]?.getD 0
      b := fun i => rhs[i.val]?.getD 0
      c := fun j => costs[j.val]?.getD 0 }
  match solveCertified P input.budget with
  | .error e => return Json.mkObj [("refusal", toJson (reprStr e))]
  | .ok (.infeasible C) => return Json.mkObj [
      ("outcome", toJson "infeasible"), ("dual", toJson ((List.ofFn C.y).map toString)),
      ("pivots", toJson C.pivots)]
  | .ok (.unbounded C) => return Json.mkObj [
      ("outcome", toJson "unbounded"), ("primal", toJson ((List.ofFn C.x).map toString)),
      ("direction", toJson ((List.ofFn C.d).map toString)), ("pivots", toJson C.pivots)]
  | .ok (.optimal C) => return Json.mkObj [
      ("primal", toJson ((List.ofFn C.x).map toString)),
      ("dual", toJson ((List.ofFn C.y).map toString)),
      ("value", toJson (toString C.value)), ("pivots", toJson C.pivots)]

end EpistemicNoGo.SimplexDriver

def main (args : List String) : IO Unit := do
  let [file] := args | throw (IO.userError "usage: lake env lean --run SimplexDriver.lean input.json")
  let raw ← IO.FS.readFile file
  let inputs := (Json.parse raw).bind (fromJson? (α := List EpistemicNoGo.SimplexDriver.Input))
  let inputs ← IO.ofExcept inputs
  let results ← IO.ofExcept (inputs.mapM EpistemicNoGo.SimplexDriver.evaluate)
  IO.println (toJson results).compress
