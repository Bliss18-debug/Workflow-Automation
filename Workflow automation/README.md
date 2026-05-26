# Leceil Morgan Corp - Workflow Automation & Document Management

## Project Overview

This is a comprehensive workflow automation and document management system designed for Leceil Morgan Corp. It provides tools for automating business processes, managing electronic forms, and handling document lifecycles with compliance and audit trail support.

## Key Features

### 🔄 Workflow Automation
- **Event-driven workflows** - Trigger actions based on form submissions, document uploads, scheduled tasks
- **Conditional logic** - Route workflows based on data values
- **Retry & error handling** - Resilient workflow execution
- **Audit trails** - Complete execution logging and tracking

### 📋 Electronic Forms (e-Forms)
- **Dynamic form builder** - Create forms programmatically
- **Comprehensive validation** - Email, phone, custom patterns, cross-field rules
- **Digital signatures** - Capture and verify signatures
- **Data export** - Export to JSON/CSV with audit trails
- **Conditional fields** - Show/hide fields based on user input

### 📁 Document Management
- **Auto-tagging** - Automatic categorization based on filename and metadata
- **Version control** - Track document history with rollback capability
- **Metadata extraction** - Automatic extraction from documents
- **Access control** - Granular permissions (view, edit, delete)
- **Retention policies** - Auto-deletion after retention period
- **Compliance** - Full audit trails for regulatory compliance

### 🔗 Cloud Integration
- **SharePoint** - Upload and manage documents in SharePoint libraries
- **OneDrive** - Store and sync documents in OneDrive for Business
- **Google Drive** - Cloud storage integration (extensible)
- **Notifications** - Email, SMS, Slack, Microsoft Teams support

## Project Structure

```
workflow-automation/
├── src/
│   ├── workflows/              # Workflow engine and orchestration
│   │   ├── workflow_engine.py  # Core execution engine
│   │   ├── workflow_builder.py # Fluent API for building workflows
│   │   └── event_handler.py    # Event triggering and routing
│   ├── eforms/                 # Electronic form management
│   │   ├── form_builder.py     # Dynamic form creation
│   │   ├── form_validator.py   # Form validation
│   │   └── form_processor.py   # Form submission and export
│   ├── documents/              # Document management system
│   │   ├── document_manager.py # Core document operations
│   │   ├── document_metadata.py # Metadata extraction and indexing
│   │   └── version_control.py  # Document versioning
│   ├── integrations/           # Cloud and API integrations
│   │   ├── sharepoint_client.py
│   │   ├── onedrive_client.py
│   │   └── notification_service.py
│   └── utils/                  # Utility functions
├── examples/                   # Example implementations
│   ├── example_1_hr_onboarding.py
│   ├── example_2_document_management.py
│   └── example_3_eform_validation.py
├── config/                     # Configuration files
│   └── config.json
├── tests/                      # Test suite
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── setup.ps1                   # Setup script
```

## Getting Started

### 1. Setup Environment

```powershell
# On Windows (PowerShell)
.\setup.ps1 -Setup

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Examples

```powershell
# Example 1: HR Onboarding Workflow
.\setup.ps1 -RunExample -ExampleNumber 1

# Example 2: Document Management
.\setup.ps1 -RunExample -ExampleNumber 2

# Example 3: E-Form Validation
.\setup.ps1 -RunExample -ExampleNumber 3

# Or directly with Python
python examples/example_1_hr_onboarding.py
```

### 3. Basic Usage

#### Create a Workflow

```python
from src.workflows import WorkflowBuilder, WorkflowEngine

# Build workflow
workflow = WorkflowBuilder("approval_workflow") \
    .add_step("validate", "validate_form", {"required_fields": ["name"]}) \
    .add_step("notify", "send_notification", {"recipient": "manager@company.com"}) \
    .link_steps("validate", "notify") \
    .build()

# Execute workflow
engine = WorkflowEngine()
engine.register_workflow("approval_workflow", workflow)
execution_id = engine.execute_workflow("approval_workflow", form_data)
```

#### Create an E-Form

```python
from src.eforms import FormBuilder, FieldType

form = FormBuilder("contact_form", "Contact Information") \
    .add_field("name", FieldType.TEXT, required=True) \
    .add_field("email", FieldType.EMAIL, required=True) \
    .add_field("phone", FieldType.PHONE) \
    .add_field("message", FieldType.TEXTAREA) \
    .build()
```

#### Manage Documents

```python
from src.documents import DocumentManager, VersionControl

# Upload document
doc_manager = DocumentManager()
doc_id = doc_manager.upload_document(
    name="report.pdf",
    file_content=file_bytes,
    content_type="application/pdf",
    owner_id="user_001",
    tags=["report", "2024"]
)

# Create versions
version_ctrl = VersionControl()
v1_id = version_ctrl.create_version(
    document_id=doc_id,
    file_path="./documents/report_v1.pdf",
    created_by="user_001",
    change_summary="Initial upload"
)
```

## Core Concepts

### Workflows

Workflows are sequences of automated steps that execute based on events (form submission, document upload, etc.). Each step can:
- Execute an action (send email, archive document)
- Check conditions (validate data, check approval status)
- Retry on failure
- Route based on outcomes

### E-Forms

Dynamic forms that support:
- Multiple field types (text, email, date, file, signature)
- Validation rules (required, min/max length, patterns)
- Conditional visibility
- Data export (JSON, CSV)
- Digital signatures with audit trails

### Documents

Complete lifecycle management:
- Upload with auto-tagging
- Metadata extraction and enrichment
- Version control with rollback
- Access control (granular permissions)
- Retention policies with auto-delete
- Full audit trails

## Configuration

Edit `config/config.json` to customize:
- Storage paths
- Cloud integrations (SharePoint, OneDrive)
- Notification settings (email, Slack, Teams)
- Workflow behavior

## Integration Examples

### Send Email Notification

```python
from src.integrations import NotificationService

notification_service = NotificationService()
notification_id = notification_service.send_email(
    recipient="manager@company.com",
    subject="Approval Request",
    template_name="approval_request",
    template_data={"document_name": "Report.pdf"}
)
```

### Upload to SharePoint

```python
from src.integrations import SharePointClient

sharepoint = SharePointClient(
    site_url="https://company.sharepoint.com",
    credentials={...}
)
sharepoint.connect()
file_id = sharepoint.upload_document(
    file_path="./report.pdf",
    library_name="Documents",
    folder_path="/Approvals"
)
```

### Sync to OneDrive

```python
from src.integrations import OneDriveClient

onedrive = OneDriveClient(credentials={...})
onedrive.connect("user@company.com")
file_id = onedrive.upload_file(
    file_path="./document.pdf",
    target_path="/Documents"
)
```

## Real-World Use Cases

### HR Onboarding
- Collect employee information via e-form
- Route for HR review
- Send notifications to stakeholders
- Archive in SharePoint with retention policy

### Expense Reimbursement
- Submit expense form with receipts
- Validate against limits
- Route to manager for approval
- Export to accounting system
- Send reimbursement notification

### Document Review & Approval
- Upload document with metadata
- Create versions for edits
- Route through approval chain
- Track decisions in audit trail
- Archive with retention policy

### Contract Management
- Collect contract data via form
- Auto-tag by department/type
- Manage versions through negotiation
- Capture signatures
- Retain according to policy

## Compliance & Audit

The system provides:
- **Complete audit trails** - Every action logged with timestamp and actor
- **Digital signatures** - Signature capture and verification
- **Version tracking** - Full document history with change reasons
- **Access control** - Who accessed what, when
- **Retention policies** - Automatic deletion per compliance requirements
- **Data export** - For compliance audits and reporting

## API Reference

### WorkflowEngine
- `register_workflow(workflow_id, definition)` - Register a workflow
- `register_action(action_name, handler)` - Register an action handler
- `execute_workflow(workflow_id, trigger_data)` - Execute a workflow
- `get_execution_status(execution_id)` - Get execution details

### FormBuilder
- `add_field(field_id, field_type, ...)` - Add form field
- `add_validation(field_id, rule_type, ...)` - Add validation rule
- `build()` - Build form schema

### DocumentManager
- `upload_document(name, content, ...)` - Upload document
- `search_documents(query, tags, ...)` - Search documents
- `grant_access(document_id, user_id, permission)` - Grant access
- `set_retention_policy(document_id, retention_days)` - Set retention

### NotificationService
- `send_email(recipient, subject, ...)` - Send email
- `send_chat_message(channel, message, ...)` - Send chat message
- `send_sms(phone_number, message)` - Send SMS
- `register_template(name, template)` - Register notification template

## Development & Testing

### Run Unit Tests
```bash
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Format code
black src/

# Check for issues
pylint src/

# Type checking
mypy src/
```

## Extending the System

### Create Custom Action Handler
```python
def custom_action(context, config):
    # Your custom logic here
    return {"result": "success"}

engine.register_action("my_action", custom_action)
```

### Create Custom Workflow
```python
workflow = WorkflowBuilder("custom_workflow") \
    .add_step("step1", "my_action", {"param": "value"}) \
    .build()
```

### Add Custom Notification Template
```python
notification_service.register_template(
    "my_template",
    "Hello {name}, your {action} has been processed."
)
```

## Production Deployment

For production use:

1. **Configure credentials** - Set up SharePoint, OneDrive, and email credentials in `.env`
2. **Use database** - Switch from in-memory storage to persistent database (MongoDB, PostgreSQL)
3. **Enable API** - Deploy with FastAPI or Flask for REST endpoints
4. **Setup monitoring** - Add logging aggregation and alerting
5. **Implement security** - Add authentication, encryption, rate limiting
6. **Performance** - Add caching, async processing, message queues

Example production setup:
```python
from fastapi import FastAPI
from src.workflows import WorkflowEngine
from src.documents import DocumentManager

app = FastAPI()
engine = WorkflowEngine()
doc_manager = DocumentManager()

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, data: dict):
    execution_id = engine.execute_workflow(workflow_id, data)
    return {"execution_id": execution_id}

@app.post("/api/documents/upload")
async def upload_document(file, metadata: dict):
    doc_id = doc_manager.upload_document(...)
    return {"document_id": doc_id}
```

## Support & Documentation

- **Examples** - See `examples/` directory
- **API Docs** - Generated from docstrings
- **Configuration** - See `config/config.json`
- **Logs** - Check `logs/app.log`

## License

© 2026 Leceil Morgan Corp. All rights reserved.

---

**Last Updated:** May 26, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
