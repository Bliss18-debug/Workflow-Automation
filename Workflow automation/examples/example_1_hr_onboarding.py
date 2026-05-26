"""
Example 1: HR Onboarding Workflow

Demonstrates an automated workflow that:
1. Accepts employee onboarding forms
2. Routes to HR department for review
3. Sends notifications
4. Archives completed forms in SharePoint
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.workflows import WorkflowEngine, WorkflowBuilder, EventHandler
from src.eforms import FormBuilder, FieldType, FormValidator, FormProcessor
from src.integrations import NotificationService


def example_1_hr_onboarding():
    """Run HR onboarding workflow example."""
    
    print("=" * 60)
    print("EXAMPLE 1: HR ONBOARDING WORKFLOW")
    print("=" * 60)
    
    # 1. Create an e-form for employee onboarding
    print("\n[Step 1] Creating onboarding form schema...")
    form = FormBuilder("emp_onboarding", "Employee Onboarding Form") \
        .add_section("Personal Information") \
        .add_field("full_name", FieldType.TEXT, required=True, label="Full Name") \
        .add_field("email", FieldType.EMAIL, required=True, label="Work Email") \
        .add_field("department", FieldType.SELECT, required=True, label="Department",
                  options=["HR", "IT", "Finance", "Operations"]) \
        .add_section("Position Details") \
        .add_field("position", FieldType.TEXT, required=True, label="Job Title") \
        .add_field("start_date", FieldType.DATE, required=True, label="Start Date") \
        .add_field("manager_approval", FieldType.CHECKBOX, label="Manager Approval") \
        .build()
    
    print(f"✓ Form created with {form['field_count']} fields")
    
    # 2. Create and register workflow
    print("\n[Step 2] Creating workflow...")
    workflow_builder = WorkflowBuilder("hr_onboarding_workflow", "HR Onboarding Workflow") \
        .add_step("validate_form", "validate_form", {
            "form_id": "emp_onboarding",
            "required_fields": ["full_name", "email", "department"]
        }) \
        .add_step("send_approval_request", "send_notification", {
            "recipient": "hr@leceilmorgan.com",
            "template": "approval_request",
            "priority": "high"
        }) \
        .add_step("archive_to_sharepoint", "archive_document", {
            "library": "HR Documents",
            "folder": "Onboarding",
            "retention_days": 365
        }) \
        .link_steps("validate_form", "send_approval_request") \
        .link_steps("send_approval_request", "archive_to_sharepoint")
    
    workflow_definition = workflow_builder.build()
    print(f"✓ Workflow created with {workflow_builder.get_steps_count()} steps")
    
    # 3. Setup workflow engine
    print("\n[Step 3] Setting up workflow engine...")
    engine = WorkflowEngine()
    
    # Register workflow
    engine.register_workflow("hr_onboarding_workflow", workflow_definition)
    
    # Register action handlers
    def validate_form_handler(context, config):
        validator = FormValidator(form)
        is_valid, errors = validator.validate(context)
        return {"valid": is_valid, "errors": [e.to_dict() for e in errors]}
    
    def send_notification_handler(context, config):
        notification_service = NotificationService()
        notif_id = notification_service.send_email(
            recipient=config.get("recipient", "hr@leceilmorgan.com"),
            subject="New Employee Onboarding Form",
            template_name=config.get("template"),
            template_data={"employee_name": context.get("full_name")}
        )
        return {"notification_id": notif_id}
    
    def archive_document_handler(context, config):
        # In production: connect to SharePoint
        return {"archived": True, "location": f"{config['library']}/{config['folder']}"}
    
    engine.register_action("validate_form", validate_form_handler)
    engine.register_action("send_notification", send_notification_handler)
    engine.register_action("archive_document", archive_document_handler)
    
    print("✓ Action handlers registered")
    
    # 4. Setup event handler
    print("\n[Step 4] Setting up event handling...")
    event_handler = EventHandler()
    
    def on_form_submitted(event):
        """Callback when form is submitted."""
        print(f"  → Form submitted event received: {event['event_id']}")
        execution_id = engine.execute_workflow("hr_onboarding_workflow", event["data"])
        print(f"  → Workflow execution started: {execution_id}")
    
    event_handler.subscribe("form_submitted", on_form_submitted)
    print("✓ Event handlers registered")
    
    # 5. Simulate form submission
    print("\n[Step 5] Simulating form submission...")
    form_data = {
        "full_name": "John Smith",
        "email": "john.smith@leceilmorgan.com",
        "department": "IT",
        "position": "Software Engineer",
        "start_date": "2026-06-01",
        "manager_approval": True
    }
    
    event_id = event_handler.trigger_event(
        event_type="form_submitted",
        source="form_submission_portal",
        data=form_data
    )
    print(f"✓ Form submitted with event ID: {event_id}")
    
    # 6. Check workflow execution status
    print("\n[Step 6] Checking workflow execution status...")
    executions = engine.list_executions()
    if executions:
        execution = executions[-1]
        print(f"  Execution ID: {execution['execution_id']}")
        print(f"  Status: {execution['status']}")
        print(f"  Started: {execution['started_at']}")
    
    print("\n✓ HR Onboarding workflow example completed!\n")


if __name__ == "__main__":
    # Setup logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    example_1_hr_onboarding()
