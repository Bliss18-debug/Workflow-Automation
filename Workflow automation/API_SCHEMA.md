# Leceil Morgan Corp - Workflow Automation System
# API Schema Documentation

## Overview
RESTful API for workflow automation, e-form management, and document handling.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Include `X-User-ID` header in all requests:
```
X-User-ID: user@company.com
```

---

## Workflow Endpoints

### Execute Workflow
```
POST /workflows/{workflow_id}/execute
```

**Request:**
```json
{
  "form_data": {
    "employee_name": "John Doe",
    "department": "IT"
  }
}
```

**Response (202):**
```json
{
  "success": true,
  "execution_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get Execution Status
```
GET /executions/{execution_id}
```

**Response (200):**
```json
{
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "started_at": "2026-05-26T10:30:00",
  "logs": ["[2026-05-26 10:30:00] Step 1 executed"]
}
```

### Get Execution Logs
```
GET /executions/{execution_id}/logs
```

**Response (200):**
```json
{
  "logs": [
    "[2026-05-26 10:30:00] Workflow started",
    "[2026-05-26 10:30:01] Validation passed",
    "[2026-05-26 10:30:02] Notification sent"
  ]
}
```

---

## Form Endpoints

### Submit Form
```
POST /forms/{form_id}/submit
```

**Request:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane.smith@company.com",
  "department": "HR",
  "position": "Manager",
  "start_date": "2026-06-01"
}
```

**Response (201):**
```json
{
  "success": true,
  "submission_id": "sub_550e8400-e29b-41d4"
}
```

### Get Submission
```
GET /submissions/{submission_id}
```

**Response (200):**
```json
{
  "submission_id": "sub_550e8400-e29b-41d4",
  "form_id": "emp_onboarding",
  "submitter_id": "emp_001",
  "submitted_at": "2026-05-26T10:30:00",
  "status": "submitted",
  "form_data": {
    "full_name": "Jane Smith",
    "email": "jane.smith@company.com"
  }
}
```

### Export Submission
```
GET /submissions/{submission_id}/export
```

**Response (200):** JSON-formatted submission data

---

## Document Endpoints

### Upload Document
```
POST /documents/upload
```

**Multipart Form Data:**
- `file`: Binary file content
- `owner_id`: Owner identifier
- `metadata`: JSON metadata (optional)

**Response (201):**
```json
{
  "success": true,
  "document_id": "doc_550e8400-e29b-41d4"
}
```

### Get Document
```
GET /documents/{document_id}
```

**Response (200):**
```json
{
  "document_id": "doc_550e8400-e29b-41d4",
  "name": "report.pdf",
  "content_type": "application/pdf",
  "owner_id": "emp_001",
  "created_at": "2026-05-26T10:30:00",
  "tags": ["report", "2024"],
  "status": "active"
}
```

### Search Documents
```
GET /documents/search?q=keyword&tags=report&tags=2024
```

**Query Parameters:**
- `q` (optional): Search keyword
- `tags` (optional, multiple): Filter by tags

**Response (200):**
```json
{
  "count": 5,
  "documents": [
    {
      "document_id": "doc_550e8400",
      "name": "report.pdf",
      "tags": ["report", "2024"]
    }
  ]
}
```

---

## Notification Endpoints

### Send Email
```
POST /notifications/send-email
```

**Request:**
```json
{
  "recipient": "manager@company.com",
  "subject": "Approval Request",
  "body": "Please review the attached document.",
  "template_name": "approval_request",
  "template_data": {
    "document_name": "Report.pdf",
    "requester": "John Doe"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "notification_id": "notif_550e8400"
}
```

### Get Notification Status
```
GET /notifications/{notification_id}
```

**Response (200):**
```json
{
  "notification_id": "notif_550e8400",
  "type": "email",
  "recipient": "manager@company.com",
  "status": "sent",
  "sent_at": "2026-05-26T10:30:00"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 202 | Accepted |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

## Rate Limiting

- **Limit**: 1000 requests per hour
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

---

## Examples

### cURL

```bash
# Execute workflow
curl -X POST http://localhost:5000/api/workflows/hr_onboarding/execute \
  -H "Content-Type: application/json" \
  -H "X-User-ID: emp_001" \
  -d '{"employee_name": "John Doe"}'

# Get document
curl -X GET http://localhost:5000/api/documents/doc_123 \
  -H "X-User-ID: emp_001"

# Search documents
curl -X GET "http://localhost:5000/api/documents/search?tags=2024&tags=report" \
  -H "X-User-ID: emp_001"

# Send email
curl -X POST http://localhost:5000/api/notifications/send-email \
  -H "Content-Type: application/json" \
  -H "X-User-ID: emp_001" \
  -d '{
    "recipient": "manager@company.com",
    "subject": "Approval",
    "body": "Please review"
  }'
```

### Python (using requests)

```python
import requests

client = requests.Session()
client.headers.update({'X-User-ID': 'emp_001'})

# Execute workflow
response = client.post(
    'http://localhost:5000/api/workflows/hr_onboarding/execute',
    json={'employee_name': 'John Doe'}
)
print(response.json())
```

### JavaScript (using axios)

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'X-User-ID': 'emp_001' }
});

// Execute workflow
client.post('/workflows/hr_onboarding/execute', {
  employee_name: 'John Doe'
}).then(response => console.log(response.data));
```

---

**API Version:** 1.0.0  
**Last Updated:** May 26, 2026
