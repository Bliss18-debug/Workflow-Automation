"""
Example 4: REST API Integration

Demonstrates building a REST API for the workflow automation system
using Python Flask. This enables remote access to workflows, forms, and documents.

In production, consider using FastAPI for better performance.
"""

# This is a template for building a REST API
# Install flask: pip install flask

flask_app_template = """
from flask import Flask, request, jsonify
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.workflows import WorkflowEngine, EventHandler
from src.eforms import FormValidator, FormProcessor, FormBuilder, FieldType
from src.documents import DocumentManager
from src.integrations import NotificationService

app = Flask(__name__)

# Initialize services
workflow_engine = WorkflowEngine()
event_handler = EventHandler()
form_processor = FormProcessor()
doc_manager = DocumentManager()
notification_service = NotificationService()

# ============= WORKFLOW ENDPOINTS =============

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    '''Execute a workflow with the provided data.'''
    try:
        data = request.get_json()
        execution_id = workflow_engine.execute_workflow(workflow_id, data)
        return jsonify({
            "success": True,
            "execution_id": execution_id
        }), 202
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/executions/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    '''Get the status of a workflow execution.'''
    execution = workflow_engine.get_execution_status(execution_id)
    if not execution:
        return jsonify({"error": "Execution not found"}), 404
    
    return jsonify({
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "started_at": execution.started_at.isoformat(),
        "logs": execution.logs[:10]  # Last 10 logs
    }), 200

@app.route('/api/executions/<execution_id>/logs', methods=['GET'])
def get_execution_logs(execution_id):
    '''Get all logs for an execution.'''
    logs = workflow_engine.get_execution_logs(execution_id)
    return jsonify({"logs": logs}), 200

# ============= FORM ENDPOINTS =============

@app.route('/api/forms/<form_id>/submit', methods=['POST'])
def submit_form(form_id):
    '''Submit a form.'''
    try:
        form_data = request.get_json()
        submitter_id = request.headers.get('X-User-ID', 'anonymous')
        
        submission_id = form_processor.submit_form(
            form_id=form_id,
            form_data=form_data,
            submitter_id=submitter_id
        )
        
        # Trigger workflow event
        event_handler.trigger_event(
            event_type="form_submitted",
            source="rest_api",
            data=form_data
        )
        
        return jsonify({
            "success": True,
            "submission_id": submission_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    '''Get submission details.'''
    submission = form_processor.get_submission(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    return jsonify(submission), 200

@app.route('/api/submissions/<submission_id>/export', methods=['GET'])
def export_submission(submission_id):
    '''Export submission as JSON.'''
    json_data = form_processor.export_json(submission_id)
    if not json_data:
        return jsonify({"error": "Submission not found"}), 404
    return json_data, 200

# ============= DOCUMENT ENDPOINTS =============

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    '''Upload a document.'''
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        owner_id = request.form.get('owner_id', 'anonymous')
        metadata = request.form.get('metadata', {})
        
        doc_id = doc_manager.upload_document(
            name=file.filename,
            file_content=file.read(),
            content_type=file.content_type,
            owner_id=owner_id,
            metadata=metadata,
            auto_tag=True
        )
        
        return jsonify({
            "success": True,
            "document_id": doc_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    '''Get document details.'''
    user_id = request.headers.get('X-User-ID', 'anonymous')
    doc = doc_manager.get_document(document_id, user_id)
    
    if not doc:
        return jsonify({"error": "Document not found or access denied"}), 404
    
    return jsonify(doc.to_dict()), 200

@app.route('/api/documents/search', methods=['GET'])
def search_documents():
    '''Search documents.'''
    query = request.args.get('q')
    tags = request.args.getlist('tags')
    user_id = request.headers.get('X-User-ID', 'anonymous')
    
    results = doc_manager.search_documents(
        query=query,
        tags=tags if tags else None,
        user_id=user_id
    )
    
    return jsonify({"count": len(results), "documents": results}), 200

# ============= NOTIFICATION ENDPOINTS =============

@app.route('/api/notifications/send-email', methods=['POST'])
def send_email_notification():
    '''Send an email notification.'''
    try:
        data = request.get_json()
        
        notif_id = notification_service.send_email(
            recipient=data['recipient'],
            subject=data['subject'],
            body=data.get('body'),
            template_name=data.get('template_name'),
            template_data=data.get('template_data')
        )
        
        return jsonify({
            "success": True,
            "notification_id": notif_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    '''Get notification status.'''
    notification = notification_service.get_notification_status(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    return jsonify(notification), 200

# ============= HEALTH CHECK =============

@app.route('/health', methods=['GET'])
def health_check():
    '''API health check.'''
    return jsonify({
        "status": "healthy",
        "service": "Leceil Morgan Workflow Automation API",
        "version": "1.0.0"
    }), 200

# ============= ERROR HANDLING =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # Production: use gunicorn
    # gunicorn -w 4 -b 0.0.0.0:5000 api:app
"""

# Save template to file
with open("./examples/rest_api_template.py", "w") as f:
    f.write(flask_app_template)

print("✓ REST API template created at: ./examples/rest_api_template.py")
print("\nTo use this API:")
print("1. Install Flask: pip install flask")
print("2. Run the API: python ./examples/rest_api_template.py")
print("3. Access at: http://localhost:5000")
print("\nAPI Endpoints:")
print("  POST   /api/workflows/<workflow_id>/execute - Execute workflow")
print("  GET    /api/executions/<execution_id> - Get execution status")
print("  POST   /api/forms/<form_id>/submit - Submit form")
print("  GET    /api/submissions/<submission_id> - Get submission")
print("  POST   /api/documents/upload - Upload document")
print("  GET    /api/documents/<document_id> - Get document")
print("  GET    /api/documents/search - Search documents")
print("  POST   /api/notifications/send-email - Send email")
print("  GET    /health - Health check")
