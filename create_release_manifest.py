import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).parent
files = [
    "doaa_proposal_gate.py",
    "doaa_proposal_repair.py",
    "doaa_audit_log.py",
    "doaa_human_review.py",
    "doaa_dsl_dry_run.py",
    "doaa_safe_file_execute.py",
    "CONTRACT-LLM-0003-bounded-proposal-repair.json",
    "CONTRACT-HUMAN-REVIEW-0001.json",
    "CONTRACT-DSL-DRYRUN-0001.json",
    "CONTRACT-SAFE-FILE-EXECUTION-0002.json",
    "CONTRACT-RELEASE-0001.json",
    "USER-TEST-EXECUTION-0001.md",
    "CONTRACT-SECURITY-DIAGNOSTICS-0001.json",
    "CONTRACT-EXCEL-ARABIC-PHONE-0001.json",
    "CONTRACT-UNIFIED-FLOW-0001.json",
    "CONTRACT-LOCAL-PACKAGE-0001.json",
    "CONTRACT-DSL-SPACE-NORMALIZE-0001.json",
    "CONTRACT-DSL-PHONE-SEPARATORS-0001.json",
    "CONTRACT-DSL-TABS-TO-SPACE-0001.json",
    "CONTRACT-DSL-UNICODE-WHITESPACE-0001.json",
    "CONTRACT-DSL-TRIM-ASCII-SPACES-0001.json",
    "CONTRACT-DAILY-UI-0001.json",
    "CONTRACT-DETERMINISTIC-RETRIEVAL-0001.json",
    "CONTRACT-ALGORITHM-REGISTRY-0001.json",
    "CONTRACT-PREMODEL-ROUTER-0001.json",
    "CONTRACT-LOCAL-INTEGRATION-0001.json",
    "CONTRACT-MODEL-MEDIATION-0001.json",
    "CONTRACT-WEB-RESEARCH-0001.json",
    "doaa_security_diagnostics.py",
    "doaa_excel_safe_execute.py",
    "doaa_unified_flow.py",
    "doaa_local.py",
    "doaa_space_normalize_execute.py",
    "doaa_trim_ascii_spaces_execute.py",
    "doaa_tabs_to_space_execute.py",
    "doaa_capability_validator.py",
    "doaa_static_verifier.py",
    "doaa_local_integration.py",
        "doaa_model_mediation.py",
    "doaa_algorithmic_protocol.py",
    "doaa_algorithmic_mediator.py",
    "doaa_algorithm_catalog.py",
    "doaa_distillation.py",
    "doaa_token_metrics.py",
    "doaa_algorithmic_cli.py",
    "doaa_natural_algorithm_proposer.py",
    "doaa_request_builder.py",
    "doaa_ollama_algorithm_bridge.py",
    "doaa_handshake.py",
    "doaa_session_protocol.py",
    "CONTRACT-DOAA-ALGORITHMIC-MEDIATION-0001.json",
    "CONTRACT-DOAA-HANDSHAKE-0001.json",
    "ADR-DOAA-ALGORITHMIC-MEDIATION-0001.md",
    "DOAA-ORIGINAL-GOAL-GAP-REVIEW-0002.md",
    "DOAA-LONG-INSTRUCTION-AMORTIZATION-REPORT-0001.md",
    "progress.md",

    "test_doaa_unicode_csv_execute.py",
    "CONTRACT-DSL-UNICODE-CSV-EXECUTION-0001.json",
    "ADR-UNICODE-XLSX-EXECUTION-0001.md",
    "DOAA-CYCLE-REPORT-0001.md",
    "DOAA-DODY-INTEGRATION-ASSESSMENT-0001.md",
    "test_doaa_unicode_xlsx_execute.py",
    "doaa_unicode_xlsx_execute.py",
    "CONTRACT-DSL-UNICODE-XLSX-EXECUTION-0001.json",
    "doaa_unicode_csv_execute.py",
    "doaa_web_research_gate.py",
    "doaa_source_registry.py",
    "doaa_research_report.py",
    "doaa_capability_advisor.py",
    "doaa_readonly_monitor.py",
    "doaa_daily_ui.py",
    "doaa_run_report.py",
    "doaa_deterministic_retrieval.py",
    "doaa_algorithm_registry.py",
    "doaa_dsl_contract_verifier.py",
    "test_doaa_dsl_contract_verifier.py",
    "test_doaa_registry_phone_contract.py",
    "test_doaa_tabs_to_space_contract.py",
    "test_doaa_unicode_whitespace_contract.py",
    "doaa_premodel_router.py",
    "run_governed_with_retrieval.ps1",
    "benchmark_retrieval.py",
    "DOAA-LOCAL-README.md",
    "test_doaa_local.py",
    "test_doaa_space_normalize_execute.py",
    "test_doaa_trim_ascii_spaces_execute.py",
    "test_doaa_tabs_to_space_execute.py",
    "test_doaa_capability_validator.py",
    "test_doaa_static_verifier.py",
    "test_doaa_local_integration.py",
        "test_doaa_model_mediation.py",
    "test_doaa_algorithmic_protocol.py",
    "test_doaa_algorithmic_mediator.py",
    "test_doaa_algorithm_catalog.py",
    "test_doaa_distillation.py",
    "test_doaa_token_metrics.py",
    "test_doaa_algorithmic_cli.py",
    "test_doaa_natural_algorithm_proposer.py",
    "test_doaa_request_builder.py",
    "test_doaa_ollama_algorithm_bridge.py",
    "test_doaa_handshake.py",
    "test_doaa_session_protocol.py",

    "test_doaa_model_route_isolation.py",
    "test_doaa_web_research_gate.py",
    "test_doaa_source_registry.py",
    "test_doaa_research_report.py",
    "test_doaa_capability_advisor.py",
    "test_doaa_readonly_monitor.py",
    "test_doaa_full_integration.py",
    "test_doaa_security_rejection_matrix.py",
    "test_doaa_daily_ui.py",
    "test_doaa_deterministic_retrieval.py",
    "RETRIEVAL-BENCHMARK-0001.md",
    "ADR-ALGORITHM-REGISTRY-0001.md",
    "ADR-DSL-TRIM-ASCII-SPACES-0001.md",
    "ADR-DSL-UNICODE-WHITESPACE-0001.md",
    "ADR-MODEL-MEDIATION-0001.md",
    "ADR-UNICODE-CSV-EXECUTION-0001.md",
    "DOAA-CAPABILITY-BUILD-PROTOCOL-0001.md",
    "DOAA-RELEASE-ACCEPTANCE-0001.md",
    "DOAA-SECURITY-ACCEPTANCE-0001.md",
    "DOAA-TRIAL-ACCEPTANCE-0001.md",
    "DOAA-RELEASE-INTEGRITY-0001.md",
    "DOAA-OPERATIONS-GUIDE-0001.md",
    "DOAA-GOVERNED-MVP-READINESS-0001.md",
    "test_doaa_utf8_bom.py",
    "ADR-CSV-UTF8-BOM-ARABIC-0001.md",
    "CONTRACT-PREVIEW-0001.json",
    "ADR-PREVIEW-0001.md",
    "doaa_preview.py",
    "doaa_xlsx_preview.py",
    "test_doaa_xlsx_preview.py",
    "test_doaa_preview.py",
    "test_doaa_full_ui_flow.py",
    "test_doaa_preview_staleness.py",
    "test_doaa_ui_contract.py",
    "ADR-UI-PREVIEW-APPROVAL-0001.md",
    "DOAA-PREVIEW-ACCEPTANCE-0001.md",
    "verify_trial_run.py",
    "trial-run-001/trial-verification.json",
    "KNOWLEDGE-REUSE-0001-DECISION.md",
    "premodel-router-receipt.json",
    "test_doaa_excel_safe_execute.py",
    "test-runs-excel/input-arabic-phone.xlsx",
    "UNIFIED-FLOW-0001-DECISION.md",
    "EXCEL-ARABIC-PHONE-0001-DECISION.md",
    "SECURITY-DIAGNOSTICS-0001-DECISION.md",
    "FULL-SPACE-FLOW-0001-DECISION.md",
    "DOAA-POST-MVP-ROADMAP-0001.md",
    "DOAA-POST-MVP-GAP-REVIEW-0001.md",
    "CONTRACT-OLLAMA-PROPOSAL-ADAPTER-0001.json",
    "doaa_ollama_proposal_adapter.py",
    "test_doaa_ollama_proposal_adapter.py",
    "ADR-OLLAMA-PROPOSAL-ADAPTER-0001.md",
    "test_doaa_ollama_review_ui.py",
    "ADR-UI-OLLAMA-REVIEW-0001.md",
    "test_doaa_readonly_health.py",
    "doaa_readonly_health.py",
    "CONTRACT-READONLY-HEALTH-0001.json",
    "test_doaa_readonly_run_report.py",
    "doaa_readonly_run_report.py",
    "CONTRACT-READONLY-RUN-REPORT-0001.json",
    "test_doaa_state_resume.py",
    "doaa_state_resume.py",
    "CONTRACT-GOVERNED-STATE-RESUME-0001.json",
    "test_doaa_independent_evidence_verifier.py",
    "doaa_independent_evidence_verifier.py",
    "CONTRACT-INDEPENDENT-EVIDENCE-VERIFIER-0001.json",
    "test_doaa_verification_artifact.py",
    "doaa_verification_artifact.py",
    "CONTRACT-VERIFICATION-ARTIFACT-0001.json",
    "test_doaa_artifact_release_consistency.py",
    "doaa_artifact_release_consistency.py",
    "CONTRACT-ARTIFACT-RELEASE-CONSISTENCY-0001.json",
    "test_doaa_artifact_approval_guard.py",
    "doaa_artifact_approval_guard.py",
    "CONTRACT-ARTIFACT-APPROVAL-GUARD-0001.json",
    "test_doaa_artifact_boundary_verifier.py",
    "doaa_artifact_boundary_verifier.py",
    "CONTRACT-ARTIFACT-BOUNDARY-0001.json",
    "test_doaa_human_approval_decision.py",
    "doaa_human_approval_decision.py",
    "CONTRACT-HUMAN-APPROVAL-DECISION-0001.json",
    "test_doaa_decision_execution_separation.py",
    "doaa_decision_execution_separation.py",
    "CONTRACT-DECISION-EXECUTION-SEPARATION-0001.json",
    "test_doaa_governed_chain_audit.py",
    "doaa_governed_chain_audit.py",
    "CONTRACT-GOVERNED-CHAIN-AUDIT-0001.json",
    "test_doaa_decision_chain_consistency.py",
    "doaa_decision_chain_consistency.py",
    "CONTRACT-DECISION-CHAIN-CONSISTENCY-0001.json",
    "test_doaa_next_step_safety.py",
    "doaa_next_step_safety.py",
    "CONTRACT-NEXT-STEP-SAFETY-0001.json",
    "test_doaa_event_order_verifier.py",
    "doaa_event_order_verifier.py",
    "CONTRACT-GOVERNED-EVENT-ORDER-0001.json",
    "test_doaa_event_completeness.py",
    "doaa_event_completeness.py",
    "CONTRACT-EVENT-COMPLETENESS-0001.json",
    "test_doaa_event_identity.py",
    "doaa_event_identity.py",
    "CONTRACT-EVENT-IDENTITY-0001.json",
    "test_doaa_identifier_validator.py",
    "doaa_identifier_validator.py",
    "CONTRACT-IDENTIFIER-FORMAT-0001.json",
    "test_doaa_event_context_match.py",
    "doaa_event_context_match.py",
    "CONTRACT-EVENT-CONTEXT-MATCH-0001.json",
    "test_doaa_event_type_validator.py",
    "doaa_event_type_validator.py",
    "CONTRACT-EVENT-TYPE-VALIDATION-0001.json",
    "test_doaa_path_safety.py",
    "doaa_path_safety.py",
    "CONTRACT-GOVERNED-PATH-SAFETY-0001.json",
    "test_doaa_execution_state_consistency.py",
    "doaa_execution_state_consistency.py",
    "CONTRACT-EXECUTION-STATE-CONSISTENCY-0001.json",
    "test_doaa_state_transition_safety.py",
    "doaa_state_transition_safety.py",
    "CONTRACT-STATE-TRANSITION-SAFETY-0001.json",
    "test_doaa_transition_idempotency.py",
    "doaa_transition_idempotency.py",
    "CONTRACT-GOVERNED-TRANSITION-IDEMPOTENCY-0001.json",
    "test_doaa_terminal_state_safety.py",
    "doaa_terminal_state_safety.py",
    "CONTRACT-TERMINAL-STATE-SAFETY-0001.json",
    "test_doaa_execution_receipt_binding.py",
    "doaa_execution_receipt_binding.py",
    "CONTRACT-EXECUTION-RECEIPT-BINDING-0001.json",
    "test_doaa_receipt_event_consistency.py",
    "doaa_receipt_event_consistency.py",
    "CONTRACT-RECEIPT-EVENT-CONSISTENCY-0001.json",
    "CONTRACT-FINAL-AUDIT-COMPLETENESS-0001.json",
    "doaa_final_audit_completeness.py",
        "test_doaa_final_audit_completeness.py",
    "doaa_raw_proposal_boundary.py",
    "test_doaa_raw_proposal_boundary.py",
    "test_doaa_local_boundary_static.py",
        "DOAA-STATIC-BOUNDARY-ACCEPTANCE-0001.json",
        "DOAA-WORKTREE-SCOPE-REVIEW-0001.json",

    "doaa_zip_manifest_verifier.py",
    "test_doaa_zip_manifest_verifier.py",
    "doaa_ollama_review_ui.py",

    "CONTRACT-UI-OLLAMA-REVIEW-0001.json",
]
entries = []
for name in files:
    path = root / name
    if not path.is_file():
        raise SystemExit(f"missing_release_file:{name}")
    data = path.read_bytes()
    entries.append({"path": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "release_id": "DOAA-GOVERNED-MVP-0001",
    "contract_id": "CONTRACT-RELEASE-0001",
    "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "scope": "CSV input with explicit phone column and new output path only",
    "model_execution_authority": "none",
    "automatic_execution": False,
    "network_request": False,
    "files": entries,
}
manifest["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
(root / "DOAA-GOVERNED-MVP-0001-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
print(json.dumps({"status":"created","release_id":manifest["release_id"],"file_count":len(entries),"manifest_sha256":manifest["manifest_sha256"]},separators=(",",":")))




























































