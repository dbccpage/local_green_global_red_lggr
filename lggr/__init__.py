"""Local Green, Global Red: scoped executable witness audits.

AuthorityEffect: None. Adapter vocabulary, not native OE contract constructors.
"""
from .common import ValidationError
from .descent import analyze_descent, decode, evaluator_defect, verify_descent_certificate
from .linear import classify_cochain, verify_l1_certificate
from .streaming import (
    StreamingAuditMonitor,
    StreamingBaselineComparator,
    StreamingBellPolytopeMonitor,
    StreamingCochainMonitor,
    StreamingDashboardAdequacyMonitor,
    StreamingDefectSoundnessMonitor,
    StreamingFiberMonitor,
    StreamingGramProbeMonitor,
    StreamingOrganizationalGluingMonitor,
    StreamingPathKernelMonitor,
    StreamingPositiveExtensionMonitor,
    StreamingProductRetractionMonitor,
    StreamingSixRoleOverlayMonitor,
    StreamingTransportMonitor,
)
from .transport import verify_transport
from .witnesses import BudgetPolicy, StateRef, StepWitness, audit_document, audit_history, history_document, make_witness

__version__ = "0.1.0"
__all__ = ["ValidationError", "analyze_descent", "decode", "evaluator_defect", "verify_descent_certificate",
           "classify_cochain", "verify_l1_certificate", "verify_transport", "BudgetPolicy", "StateRef",
           "StepWitness", "audit_document", "audit_history", "history_document", "make_witness",
           "StreamingAuditMonitor", "StreamingBaselineComparator", "StreamingBellPolytopeMonitor",
           "StreamingCochainMonitor", "StreamingDashboardAdequacyMonitor", "StreamingDefectSoundnessMonitor",
           "StreamingFiberMonitor", "StreamingGramProbeMonitor", "StreamingOrganizationalGluingMonitor",
           "StreamingPathKernelMonitor", "StreamingPositiveExtensionMonitor", "StreamingProductRetractionMonitor",
           "StreamingSixRoleOverlayMonitor", "StreamingTransportMonitor"]
