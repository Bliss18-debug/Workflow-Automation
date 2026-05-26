"""
Form Processor - Handles form submission, export, and digital signatures.

Processes validated form data, exports to JSON/CSV, and manages signature capture
for audit trails and compliance.
"""

import json
import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import StringIO
import uuid

logger = logging.getLogger(__name__)


class FormSubmission:
    """Represents a submitted form with metadata."""
    
    def __init__(
        self,
        form_id: str,
        form_data: Dict[str, Any],
        submitter_id: str,
        signature_data: Optional[Dict] = None
    ):
        self.submission_id = str(uuid.uuid4())
        self.form_id = form_id
        self.form_data = form_data
        self.submitter_id = submitter_id
        self.signature_data = signature_data
        self.submitted_at = datetime.now()
        self.status = "submitted"
        self.audit_trail = []
    
    def add_audit_log(self, action: str, actor: str, details: Dict = None):
        """Add an entry to the audit trail."""
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "details": details or {}
        })
    
    def to_dict(self) -> Dict:
        """Convert submission to dictionary."""
        return {
            "submission_id": self.submission_id,
            "form_id": self.form_id,
            "form_data": self.form_data,
            "submitter_id": self.submitter_id,
            "submitted_at": self.submitted_at.isoformat(),
            "status": self.status,
            "signature_data": self.signature_data,
            "audit_trail": self.audit_trail
        }


class FormProcessor:
    """
    Processes form submissions, exports, and manages audit trails.
    
    Handles:
    - Form submission acceptance
    - Data export (JSON, CSV)
    - Signature capture and verification
    - Audit trail management
    """
    
    def __init__(self):
        """Initialize form processor."""
        self.submissions: Dict[str, FormSubmission] = {}
        self.signatures: Dict[str, Dict] = {}
        logger.info("FormProcessor initialized")
    
    def submit_form(
        self,
        form_id: str,
        form_data: Dict[str, Any],
        submitter_id: str,
        signature_data: Optional[Dict] = None
    ) -> str:
        """
        Accept a form submission.
        
        Args:
            form_id: ID of the form being submitted
            form_data: Form field values
            submitter_id: ID of the person submitting
            signature_data: Digital signature (if required)
            
        Returns:
            Submission ID for tracking
        """
        submission = FormSubmission(form_id, form_data, submitter_id, signature_data)
        self.submissions[submission.submission_id] = submission
        
        # Log submission
        submission.add_audit_log(
            "form_submitted",
            submitter_id,
            {"form_id": form_id}
        )
        
        logger.info(f"Form submitted: {submission.submission_id}")
        return submission.submission_id
    
    def capture_signature(
        self,
        submission_id: str,
        signer_id: str,
        signature_data: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Capture digital signature for a submission.
        
        Args:
            submission_id: ID of the form submission
            signer_id: ID of the person signing
            signature_data: Signature data (base64 encoded)
            timestamp: Signature timestamp
            
        Returns:
            Success status
        """
        if submission_id not in self.submissions:
            logger.error(f"Submission not found: {submission_id}")
            return False
        
        submission = self.submissions[submission_id]
        
        signature = {
            "signer_id": signer_id,
            "signature_data": signature_data,
            "timestamp": timestamp or datetime.now(),
            "ip_address": "auto-captured"
        }
        
        self.signatures[submission_id] = signature
        submission.signature_data = signature
        submission.add_audit_log(
            "signature_captured",
            signer_id,
            {"signature_timestamp": signature["timestamp"].isoformat()}
        )
        
        logger.info(f"Signature captured for submission: {submission_id}")
        return True
    
    def export_json(self, submission_id: str) -> Optional[str]:
        """
        Export submission data as JSON.
        
        Args:
            submission_id: ID of the submission to export
            
        Returns:
            JSON string or None if not found
        """
        if submission_id not in self.submissions:
            logger.warning(f"Submission not found: {submission_id}")
            return None
        
        submission = self.submissions[submission_id]
        return json.dumps(submission.to_dict(), indent=2, default=str)
    
    def export_csv(
        self,
        submission_ids: List[str]
    ) -> Optional[str]:
        """
        Export multiple submissions as CSV.
        
        Args:
            submission_ids: List of submission IDs to export
            
        Returns:
            CSV string or None if no valid submissions
        """
        submissions = [
            self.submissions[sid] for sid in submission_ids
            if sid in self.submissions
        ]
        
        if not submissions:
            logger.warning("No submissions found for export")
            return None
        
        # Get all possible field keys
        all_fields = set()
        for sub in submissions:
            all_fields.update(sub.form_data.keys())
        
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["submission_id", "form_id", "submitter_id", "submitted_at"] + sorted(all_fields)
        )
        
        writer.writeheader()
        for sub in submissions:
            row = {
                "submission_id": sub.submission_id,
                "form_id": sub.form_id,
                "submitter_id": sub.submitter_id,
                "submitted_at": sub.submitted_at.isoformat()
            }
            row.update(sub.form_data)
            writer.writerow(row)
        
        return output.getvalue()
    
    def get_submission(self, submission_id: str) -> Optional[Dict]:
        """Get submission details."""
        if submission_id not in self.submissions:
            return None
        return self.submissions[submission_id].to_dict()
    
    def update_submission_status(
        self,
        submission_id: str,
        status: str,
        actor: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update submission status and log the change.
        
        Args:
            submission_id: ID of the submission
            status: New status (e.g., 'approved', 'rejected', 'archived')
            actor: Person making the change
            reason: Optional reason for the change
            
        Returns:
            Success status
        """
        if submission_id not in self.submissions:
            return False
        
        submission = self.submissions[submission_id]
        submission.status = status
        submission.add_audit_log(
            f"status_changed_to_{status}",
            actor,
            {"reason": reason}
        )
        
        logger.info(f"Submission {submission_id} status updated to: {status}")
        return True
    
    def get_audit_trail(self, submission_id: str) -> Optional[List[Dict]]:
        """Get the audit trail for a submission."""
        if submission_id not in self.submissions:
            return None
        return self.submissions[submission_id].audit_trail
    
    def list_submissions(
        self,
        form_id: Optional[str] = None,
        submitter_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        List submissions with optional filtering.
        
        Args:
            form_id: Filter by form ID
            submitter_id: Filter by submitter
            status: Filter by status
            limit: Maximum number to return
            
        Returns:
            List of submission summaries
        """
        results = []
        for sub in self.submissions.values():
            if form_id and sub.form_id != form_id:
                continue
            if submitter_id and sub.submitter_id != submitter_id:
                continue
            if status and sub.status != status:
                continue
            
            results.append({
                "submission_id": sub.submission_id,
                "form_id": sub.form_id,
                "submitter_id": sub.submitter_id,
                "submitted_at": sub.submitted_at.isoformat(),
                "status": sub.status
            })
        
        return results[:limit]
