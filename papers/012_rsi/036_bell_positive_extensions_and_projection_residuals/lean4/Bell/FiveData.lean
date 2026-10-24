import Bell.SparseCertificates

/-! Integer certificate data for a complete rational 5-by-5 Bell experiment. -/
namespace Bell.FiveData
open scoped BigOperators
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def bit (g k : ℕ) : Bool := g / 2^(9-k) % 2 == 1
def A (g : Fin 1024) (i : Fin 100) : ℤ :=
  if bit g.val (i.val/20) = (i.val/2%2 == 1) ∧
    bit g.val (5+i.val/4%5) = (i.val%2 == 1) then 1 else 0

theorem assignment_complete (a b : Fin 5 → Bool) : ∃ g : Fin 1024,
    (∀ x : Fin 5, bit g.val x.val = a x) ∧
    (∀ y : Fin 5, bit g.val (5+y.val) = b y) := by
  let v : BitVec 10 := BitVec.ofBoolListBE [a 0,a 1,a 2,a 3,a 4,b 0,b 1,b 2,b 3,b 4]
  let g : Fin 1024 := ⟨v.toNat, v.isLt⟩
  refine ⟨g, ?_, ?_⟩
  · intro x
    simp only [bit, Bool.beq_eq_decide_eq, ← Nat.testBit_eq_decide_div_mod_eq]
    change v.toNat.testBit (9-x.val) = a x
    rw [BitVec.testBit_toNat]
    simp only [v, BitVec.getLsbD_ofBoolListBE]
    fin_cases x <;> rfl
  · intro y
    simp only [bit, Bool.beq_eq_decide_eq, ← Nat.testBit_eq_decide_div_mod_eq]
    change v.toNat.testBit (9-(5+y.val)) = b y
    rw [BitVec.testBit_toNat]
    simp only [v, BitVec.getLsbD_ofBoolListBE]
    fin_cases y <;> rfl
def az : Fin 5 → ℤ := ![185, 148, 57, -57, -148]
def ax : Fin 5 → ℤ := ![0, 111, 176, 176, 111]
def bz : Fin 5 → ℤ := ![175, 111, 0, -111, -175]
def bx : Fin 5 → ℤ := ![60, 148, 185, 148, 60]
def pn (i : Fin 100) : ℤ := 34225 +
  (if i.val/2%2 = i.val%2 then 1 else -1) *
  (az ⟨i.val/20, by omega⟩ * bz ⟨i.val/4%5, by omega⟩ +
   ax ⟨i.val/20, by omega⟩ * bx ⟨i.val/4%5, by omega⟩)
def qid : Fin 31 → Fin 1024 := ![0, 1, 30, 35, 99, 103, 211, 231, 247, 293, 495, 511, 512, 536, 585, 621, 729, 784, 792, 856, 860, 877, 920, 924, 961, 988, 989, 990, 1021, 1022, 1023]
def qn : Fin 31 → ℤ := ![8695, 4891, -6845, 8695, 4995, 7659, 6949, 12476, 296, 104, 19085, 1450, 12425, 710, 6845, 104, 555, 19136, 201, 192, 296, 347, 12032, 8406, -17871, 10272, 296, 1265, 814, 1665, 10760]
def hid : Fin 20 → Fin 1024 := ![0, 1, 33, 35, 99, 103, 231, 239, 495, 511, 512, 528, 784, 792, 920, 924, 988, 990, 1022, 1023]
def hn : Fin 20 → ℤ := ![1850, 1665, 1369, 1850, 1665, 1665, 1850, 1369, 1665, 1850, 1850, 1665, 1369, 1850, 1665, 1665, 1850, 1369, 1665, 1850]
def y : Fin 100 → ℤ := ![0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0]
def z : Fin 100 → ℤ := ![0, 0, 1, 1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0]

theorem directions : (∀ i, az i^2+ax i^2=34225) ∧ (∀ i, bz i^2+bx i^2=34225) := by decide +kernel
theorem cells_nonnegative : ∀ i, 0 ≤ pn i := by decide +kernel
theorem context_total : ∀ xy : Fin 25, (∑ a : Fin 4, pn ⟨4*xy.val+a.val, by omega⟩) = 136900 := by decide +kernel
theorem first_context : ∀ g, (∑ i : Fin 4, A g ⟨i.val,by omega⟩) = 1 := by decide +kernel
theorem point_total : (∑ i, pn i) = 3422500 := by decide +kernel
theorem signed_total : (∑ j, qn j) = 136900 := by decide +kernel
theorem signed_projects : ∀ i, (∑ j, qn j*A (qid j) i) = pn i := by decide +kernel
theorem signed_negative : (∑ j, max (-qn j) 0) = 24716 := by decide +kernel
theorem packing_nonnegative : ∀ j, 0 ≤ hn j := by decide +kernel
theorem packing_total : (∑ j, hn j) = 33596 := by decide +kernel
theorem packing_projects : ∀ i, (∑ j, hn j*A (hid j) i) ≤ pn i := by decide +kernel
theorem cover_nonnegative : ∀ i, 0 ≤ y i := by decide +kernel
def cyid : Fin 20 → Fin 100 := ![1, 2, 16, 19, 21, 22, 25, 26, 45, 46, 49, 50, 69, 70, 73, 74, 93, 94, 97, 98]
def cyval : Fin 20 → ℤ := ![1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
theorem cover : ∀ g, 1 ≤ ∑ i, y i*A g i := by
  have hs : ∀ g, 1 ≤ ∑ j, cyval j*A g (cyid j) := by decide +kernel
  have hr : ∀ i, y i = ∑ j, if cyid j=i then cyval j else 0 := by decide +kernel
  intro g
  have he : (∑ i, y i*A g i) = ∑ j, cyval j*A g (cyid j) := by
    simp_rw [hr,Finset.sum_mul]
    rw [Finset.sum_comm]
    simp [ite_mul]
  simpa only [he] using hs g
theorem cover_value : (∑ i, y i*pn i) = 33596 := by decide +kernel
def czid : Fin 8 → Fin 100 := ![2, 3, 6, 19, 64, 77, 96, 98]
def czval : Fin 8 → ℤ := ![1, 1, -1, -1, 1, -1, -1, -1]
theorem signed_dual : ∀ g, -1 ≤ (∑ i, z i*A g i) ∧ (∑ i, z i*A g i) ≤ 0 := by
  have hs : ∀ g, -1 ≤ (∑ j, czval j*A g (czid j)) ∧ (∑ j, czval j*A g (czid j)) ≤ 0 := by decide +kernel
  have hr : ∀ i, z i = ∑ j, if czid j=i then czval j else 0 := by decide +kernel
  intro g
  have he : (∑ i, z i*A g i) = ∑ j, czval j*A g (czid j) := by
    simp_rw [hr,Finset.sum_mul]
    rw [Finset.sum_comm]
    simp [ite_mul]
  simpa only [he] using hs g
theorem signed_dual_value : (∑ i, z i*pn i) = 24716 := by decide +kernel

end Bell.FiveData
