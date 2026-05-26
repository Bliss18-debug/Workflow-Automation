# Leceil Morgan Corp - Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites
- Python 3.8+
- PowerShell (Windows) or Bash (Linux/Mac)

### 2. Setup Environment
```powershell
# On Windows (PowerShell)
.\setup.ps1 -Setup

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Examples

```powershell
# Example 1: HR Onboarding (workflows)
python examples/example_1_hr_onboarding.py

# Example 2: Document Management (versioning, storage)
python examples/example_2_document_management.py

# Example 3: E-Form Validation (forms, export)
python examples/example_3_eform_validation.py
```

## Key Concepts

### 🔄 Workflows
Automate sequences of actions triggered by events:
```python
from src.workflows import WorkflowBuilder, WorkflowEngine

# Create
workflow = WorkflowBuilder("approval_workflow") \
    .add_step("validate", "validate_form", {...}) \
    .add_step("notify", "send_email", {...}) \
    .build()

# Execute
engine = WorkflowEngine()
engine.register_workflow("approval_workflow", workflow)
execution_id = engine.execute_workflow("approval_workflow", data)
```

### 📋 E-Forms
Create and validate dynamic forms:
```python
from src.eforms import FormBuilder, FieldType, FormValidator

# Create
form = FormBuilder("contact_form", "Contact") \
    .add_field("name", FieldType.TEXT, required=True) \
    .add_field("email", FieldType.EMAIL, required=True) \
    .build()

# Validate
validator = FormValidator(form)
is_valid, errors = validator.validate(form_data)

# Export
processor = FormProcessor()
submission_id = processor.submit_form("contact_form", form_data, "user_123")
json_data = processor.export_json(submission_id)
csv_data = processor.export_csv([submission_id])
```

### 📁 Documents
Manage document lifecycle:
```python
from src.documents import DocumentManager, VersionControl

# Upload
doc_manager = DocumentManager()
doc_id = doc_manager.upload_document(
    name="report.pdf",
    file_content=file_bytes,
    content_type="application/pdf",
    owner_id="user_123",
    tags=["report", "2024"]
)

# Version
version_ctrl = VersionControl()
v_id = version_ctrl.create_version(
    document_id=doc_id,
    file_path="./report_v2.pdf",
    created_by="user_123",
    change_summary="Updated analysis"
)

# Search
results = doc_manager.search_documents(tags=["report"])
```

### 🔗 Integrations
Connect with external services:
```python
from src.integrations import NotificationService, SharePointClient

# Send Email
notify = NotificationService()
notify.send_email(
    recipient="manager@company.com",
    subject="Approval Request",
    body="Please review..."
)

# Upload to SharePoint
sharepoint = SharePointClient(site_url, credentials)
sharepoint.connect()
file_id = sharepoint.upload_document(
    file_path="./report.pdf",
    library_name="Documents",
    folder_path="/Reports"
)
```

## Common Tasks

### Task 1: Build a Workflow
```python
from src.workflows import WorkflowBuilder, WorkflowEngine, EventHandler

# 1. Define workflow
builder = WorkflowBuilder("employee_onboarding")
builder.add_step("validate", "validate_form", {"required": ["name", "email"]})
builder.add_step("notify_hr", "send_email", {"recipient": "hr@company.com"})
builder.add_step("archive", "archive_document", {"library": "HR"})

# Link steps
builder.link_steps("validate", "notify_hr")
builder.link_steps("notify_hr", "archive")

workflow = builder.build()

# 2. Register and execute
engine = WorkflowEngine()
engine.register_workflow("employee_onboarding", workflow)

# Define action handlers
def validate_handler(context, config):
    return {"valid": True}

def notify_handler(context, config):
    return {"sent": True}

def archive_handler(context, config):
    return {"archived": True}

engine.register_action("validate_form", validate_handler)
engine.register_action("send_email", notify_handler)
engine.register_action("archive_document", archive_handler)

# 3. Trigger via events
event_handler = EventHandler()
event_handler.subscribe("form_submitted", 
    lambda e: engine.execute_workflow("employee_onboarding", e["data"]))

# 4. Submit form to trigger workflow
event_handler.trigger_event(
    "form_submitted",
    "web_portal",
    {"name": "John Doe", "email": "john@company.com"}
)
```

### Task 2: Create a Form with Validation
```python
from src.eforms import FormBuilder, FieldType, FormValidator

# Build form
form = FormBuilder("expense_form", "Expense Report") \
    .add_section("Employee Info") \
    .add_field("employee_id", FieldType.TEXT, required=True, label="Employee ID") \
    .add_field("email", FieldType.EMAIL, required=True, label="Email") \
    .add_section("Expense Details") \
    .add_field("amount", FieldType.NUMBER, required=True, label="Amount") \
    .add_field("category", FieldType.SELECT, required=True, label="Category",
              options=["Travel", "Meals", "Equipment"]) \
    .add_field("description", FieldType.TEXTAREA, required=True, label="Description") \
    .add_field("receipt", FieldType.FILE, required=True, label="Receipt")

# Add validation
form.add_validation("amount", "min_value", 0, "Must be positive")
form.add_validation("amount", "max_value", 10000, "Cannot exceed $10,000")
form.add_validation("description", "min_length", 10, "At least 10 characters")

schema = form.build()

# Validate submission
validator = FormValidator(schema)
submission_data = {
    "employee_id": "EMP001",
    "email": "user@company.com",
    "amount": 500.00,
    "category": "Travel",
    "description": "Client meeting travel expenses",
    "receipt": "receipt.pdf"
}

is_valid, errors = validator.validate(submission_data)
if is_valid:
    print("✓ Form is valid")
else:
    print("✗ Validation errors:")
    for error in errors:
        print(f"  {error.field_id}: {error.message}")
```

### Task 3: Upload and Version Documents
```python
from src.documents import DocumentManager, VersionControl, DocumentMetadata

# Initialize
doc_manager = DocumentManager()
version_ctrl = VersionControl()
metadata_mgr = DocumentMetadata()

# Upload document
with open("policy.pdf", "rb") as f:
    doc_id = doc_manager.upload_document(
        name="Company_Policy_2024.pdf",
        file_content=f.read(),
        content_type="application/pdf",
        owner_id="emp_001",
        metadata={"department": "HR", "category": "Policies"},
        tags=["policy", "2024"],
        auto_tag=True
    )

print(f"Document uploaded: {doc_id}")

# Create version
v1_id = version_ctrl.create_version(
    document_id=doc_id,
    file_path="./documents/policy_v1.pdf",
    created_by="emp_001",
    change_summary="Initial upload"
)

# Update document and create new version
with open("policy_updated.pdf", "rb") as f:
    v2_id = version_ctrl.create_version(
        document_id=doc_id,
        file_path="./documents/policy_v2.pdf",
        created_by="emp_002",
        change_summary="Updated with new compliance requirements"
    )

# Grant access
doc_manager.grant_access(doc_id, "emp_003", "view")
doc_manager.grant_access(doc_id, "emp_004", "edit")

# Set retention policy (keep for 2 years)
doc_manager.set_retention_policy(doc_id, retention_days=730)

# Search
results = doc_manager.search_documents(tags=["policy"], owner_id="emp_001")
print(f"Found {len(results)} document(s)")

# Extract metadata
metadata = metadata_mgr.extract_metadata("./policy.pdf", "Company_Policy_2024.pdf")
print("Extracted metadata:", metadata)
```

## Next Steps

### For Development
1. Review the [README.md](README.md) for full documentation
2. Check [API_SCHEMA.md](API_SCHEMA.md) for REST API details
3. Run unit tests: `pytest tests/ -v`
4. Review [examples/](examples/) for working code samples

### For Production
1. Follow [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
2. Configure cloud integrations (SharePoint, OneDrive)
3. Setup authentication and security
4. Configure email/chat notifications
5. Setup monitoring and logging
6. Create backup strategy

### For Integration
1. **Python**: Use the modules directly
2. **Node.js**: See [nodejs_integration.js](examples/nodejs_integration.js)
3. **REST API**: Use [Flask API template](examples/example_4_rest_api.py)
4. **PowerShell**: See [powershell_integration.ps1](examples/powershell_integration.ps1)

## File Structure Reference

```
workflow-automation/
├── src/
│   ├── workflows/          # Workflow engine (WorkflowBuilder, WorkflowEngine, EventHandler)
│   ├── eforms/            # Forms (FormBuilder, FormValidator, FormProcessor)
│   ├── documents/         # Document management (DocumentManager, VersionControl, Metadata)
│   ├── integrations/      # Cloud & notifications (SharePoint, OneDrive, Email, SMS)
│   └── utils/             # Helper functions
├── examples/              # 3+ working examples + API template
├── tests/                 # Unit tests
├── config/                # Configuration files
├── README.md              # Full documentation
├── API_SCHEMA.md          # REST API reference
├── DEPLOYMENT.md          # Production deployment guide
└── setup.ps1              # Setup script
```

## Getting Help

### Documentation
- **README.md** - Overview and getting started
- **API_SCHEMA.md** - REST API endpoints
- **DEPLOYMENT.md** - Production setup
- **Docstrings** - In-code documentation

### Examples
- **example_1_hr_onboarding.py** - Workflow automation
- **example_2_document_management.py** - Document lifecycle
- **example_3_eform_validation.py** - Form creation and validation
- **example_4_rest_api.py** - REST API server
- **nodejs_integration.js** - Node.js client
- **powershell_integration.ps1** - PowerShell automation

### Support
- Check existing examples for similar tasks
- Review docstrings in source code
- Check inline comments for complex logic
- Test changes with unit tests

---

**Happy coding!** 🚀

For questions or issues, refer to the comprehensive documentation in README.md or DEPLOYMENT.md.
