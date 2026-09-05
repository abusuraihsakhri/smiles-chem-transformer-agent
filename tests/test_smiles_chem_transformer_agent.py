"""
Automated Pytest Test Suite for Smiles Chem Transformer Agent.
Domain: AI Drug Discovery, Structural Biology & Wet-Lab Robotics
Standard: wwPDB / IUPAC / OpenSMILES / ISAC Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_email_detection():
    """Test that PHI guard detects email addresses."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Contact user@example.com for results")


def test_phi_guard_ssn_detection():
    """Test that PHI guard detects SSN patterns."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient SSN: 123-45-6789")


def test_phi_guard_redaction():
    """Test PHI redaction functionality."""
    text = "Contact user@example.com or call 123-45-6789"
    redacted = PHIGuard.redact_phi(text)
    assert "@" not in redacted
    assert "123-45-6789" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_with_custom_key():
    """Test that AuditTrail accepts a custom secret key."""
    trail = AuditTrail(secret_key="test-secret-key-12345")
    entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"detail": "value"})
    assert entry["current_hash"] != ""
    assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"
    assert trail.verify_integrity() is True


def test_audit_trail_chain_integrity():
    """Test that audit trail maintains chain integrity across multiple entries."""
    trail = AuditTrail(secret_key="chain-test-key")
    trail.log("actor1", "tier1", "EVENT_1", {"seq": 1})
    trail.log("actor2", "tier2", "EVENT_2", {"seq": 2})
    trail.log("actor3", "tier3", "EVENT_3", {"seq": 3})
    assert len(trail.get_trail()) == 3
    assert trail.verify_integrity() is True


def test_cli_batch_processing():
    """Test batch CSV processing with sample data."""
    import tempfile
    import os
    # Use the existing sample.csv
    sample_path = str(Path(__file__).parent.parent / "sample.csv")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_output = f.name
    try:
        result = main(["batch", "-i", sample_path, "-o", temp_output])
        assert result == 0
        assert os.path.exists(temp_output)
    finally:
        if os.path.exists(temp_output):
            os.unlink(temp_output)


def test_cli_batch_missing_file():
    """Test batch processing with missing input file."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1
