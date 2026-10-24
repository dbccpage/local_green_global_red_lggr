import Lake
open Lake DSL

package «LGGR» where
  version := v!"0.1.0"
  buildDir := "b"

@[default_target]
lean_lib «LGGR» where
  srcDir := "."
  roots := #[
    `primitive_difference,
    `«01_local_green_counterexample»,
    `«02_delta_partition»,
    `«03_kernel_composition»,
    `«03b_product_of_sums»,
    `«03c_g1_set_isomorphism»,
    `«04_defect_corrected_kernel»,
    `«05_proposal_weighted_composition»,
    `«06_activation_density»,
    `«07_dashboard_insufficiency»,
    `«08_primitive_difference_bridge»,
    `«09_defect_class_normal_forms»,
    `«10_egd_zero_gate»,
    `«11_egd_decomposition»,
    `«12_signed_defect_balance»,
    `«13_two_rate_dashboard_insufficiency»,
    `«14_defect_moment_reconstruction»,
    `«15_ngd_exposure_decomposition»,
    `«16_diagnostic_quotient_sufficiency»,
    `«17_defect_packet_non_sufficiency»,
    `«18_defect_packet_one_bit_reconstruction»,
    `«19_defect_kind_normal_form»,
    `«20_bool_dashboard_minimality»,
    `«21_carrier_kernel_quotient»,
    `«22_detector_adequacy»,
    `core,
    `lggr_i_evaluated_path_kernels
  ]
