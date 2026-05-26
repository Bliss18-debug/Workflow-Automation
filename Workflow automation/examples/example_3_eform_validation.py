"""
Example 3: E-Form Validation & Export

Demonstrates:
1. Dynamic form creation with validation rules
2. Form submission validation
3. Export to JSON/CSV
4. Audit trail management
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.eforms import FormBuilder, FieldType, FormValidator, FormProcessor


def example_3_eform_validation():
    """Run e-form validation example."""
    
    print("=" * 60)
    print("EXAMPLE 3: E-FORM VALIDATION & EXPORT")
    print("=" * 60)
    
    # 1. Create form with validation rules
    print("\n[Step 1] Creating expense reimbursement form...")
    
    form = FormBuilder("expense_form", "Expense Reimbursement Request") \
        .add_section("Employee Information") \
        .add_field("employee_id", FieldType.TEXT, required=True, label="Employee ID") \
        .add_field("employee_name", FieldType.TEXT, required=True, label="Full Name") \
        .add_field("department", FieldType.SELECT, required=True, label="Department",
                  options=["Sales", "Marketing", "Engineering", "HR", "Finance"]) \
        .add_section("Expense Details") \
        .add_field("expense_date", FieldType.DATE, required=True, label="Expense Date") \
        .add_field("amount", FieldType.NUMBER, required=True, label="Amount ($)") \
        .add_field("category", FieldType.SELECT, required=True, label="Category",
                  options=["Travel", "Meals", "Equipment", "Other"]) \
        .add_field("description", FieldType.TEXTAREA, required=True, label="Description") \
        .add_field("receipt", FieldType.FILE, required=True, label="Receipt (PDF)") \
        .add_section("Approval") \
        .add_field("manager_approval", FieldType.CHECKBOX, required=False, label="Manager Approved") \
        .add_field("signature", FieldType.SIGNATURE, required=True, label="Digital Signature")
    
    # Add validation rules
    form.add_validation("employee_id", "pattern", "^EMP[0-9]{4}$", "Invalid employee ID format")
    form.add_validation("amount", "min_value", 0.01, "Amount must be greater than 0")
    form.add_validation("amount", "max_value", 10000, "Amount cannot exceed $10,000")
    form.add_validation("description", "min_length", 10, "Description must be at least 10 characters")
    
    form_schema = form.build()
    print(f"✓ Form created with {form_schema['field_count']} fields")
    print(f"  Sections: {len(form_schema['sections'])}")
    print(f"  Validation rules: {sum(len(v) for v in form_schema['validation_rules'].values())}")
    
    # 2. Validate form submissions
    print("\n[Step 2] Validating form submissions...")
    
    validator = FormValidator(form_schema)
    
    # Valid submission
    print("\n  Submission 1 (VALID):")
    valid_data = {
        "employee_id": "EMP0001",
        "employee_name": "John Doe",
        "department": "Sales",
        "expense_date": "2026-05-20",
        "amount": 150.00,
        "category": "Travel",
        "description": "Flight for client meeting in New York",
        "receipt": "receipt_001.pdf",
        "manager_approval": True,
        "signature": "base64_encoded_signature"
    }
    
    is_valid, errors = validator.validate(valid_data)
    print(f"    Status: {'✓ VALID' if is_valid else '✗ INVALID'}")
    if not is_valid:
        for error in errors:
            print(f"    Error: {error.field_id} - {error.message}")
    
    # Invalid submission
    print("\n  Submission 2 (INVALID):")
    invalid_data = {
        "employee_id": "INVALID",  # Wrong format
        "employee_name": "Jane Smith",
        "department": "HR",
        "expense_date": "2026-05-20",
        "amount": 25000,  # Exceeds max
        "category": "Travel",
        "description": "Trip",  # Too short
        "receipt": "receipt_002.pdf",
        "signature": "base64_encoded_signature"
    }
    
    is_valid, errors = validator.validate(invalid_data)
    print(f"    Status: {'✓ VALID' if is_valid else '✗ INVALID'}")
    if not is_valid:
        print(f"    Found {len(errors)} error(s):")
        for error in errors:
            print(f"    - {error.field_id}: {error.message}")
    
    # 3. Process form submissions
    print("\n[Step 3] Processing form submissions...")
    
    processor = FormProcessor()
    
    # Submit valid form
    submission_id = processor.submit_form(
        form_id="expense_form",
        form_data=valid_data,
        submitter_id="emp_0001"
    )
    print(f"✓ Form submitted: {submission_id}")
    
    # Capture signature
    processor.capture_signature(
        submission_id=submission_id,
        signer_id="emp_0001",
        signature_data="base64_encoded_digital_signature"
    )
    print("✓ Digital signature captured")
    
    # Update status
    processor.update_submission_status(
        submission_id=submission_id,
        status="approved",
        actor="manager_emp_001",
        reason="Approved for reimbursement"
    )
    print("✓ Submission status updated to 'approved'")
    
    # 4. Export submissions
    print("\n[Step 4] Exporting submissions...")
    
    # Export as JSON
    json_export = processor.export_json(submission_id)
    if json_export:
        print("✓ Exported as JSON")
        print("  First 200 chars:")
        print(f"  {json_export[:200]}...")
    
    # Export as CSV
    csv_export = processor.export_csv([submission_id])
    if csv_export:
        print("✓ Exported as CSV")
        lines = csv_export.split('\n')
        print(f"  Headers: {lines[0][:80]}...")
        if len(lines) > 1:
            print(f"  Data: {lines[1][:80]}...")
    
    # 5. Audit trail
    print("\n[Step 5] Viewing audit trail...")
    
    audit_trail = processor.get_audit_trail(submission_id)
    if audit_trail:
        print(f"✓ Audit trail ({len(audit_trail)} entries):")
        for entry in audit_trail:
            print(f"  - {entry['timestamp']}: {entry['action']} by {entry['actor']}")
    
    # 6. List submissions
    print("\n[Step 6] Listing submissions...")
    
    submissions = processor.list_submissions(form_id="expense_form")
    print(f"✓ Found {len(submissions)} submission(s)")
    for sub in submissions:
        print(f"  - {sub['submission_id']}: {sub['status']} (by {sub['submitter_id']})")
    
    print("\n✓ E-form validation example completed!\n")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    example_3_eform_validation()
