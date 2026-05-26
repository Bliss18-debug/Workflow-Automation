"""
Unit Tests for Workflow Automation System

Run tests with: pytest tests/ -v --cov=src
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.workflows import WorkflowEngine, WorkflowBuilder, EventHandler
from src.eforms import FormBuilder, FieldType, FormValidator, FormProcessor
from src.documents import DocumentManager, VersionControl
from src.integrations import NotificationService


class TestWorkflowEngine(unittest.TestCase):
    """Test workflow execution engine."""
    
    def setUp(self):
        self.engine = WorkflowEngine()
    
    def test_workflow_registration(self):
        """Test workflow registration."""
        workflow = {
            "id": "test_workflow",
            "steps": []
        }
        self.engine.register_workflow("test_workflow", workflow)
        self.assertIn("test_workflow", self.engine.workflows)
    
    def test_action_handler_registration(self):
        """Test action handler registration."""
        def test_action(context, config):
            return {"result": "success"}
        
        self.engine.register_action("test_action", test_action)
        self.assertIn("test_action", self.engine.action_handlers)


class TestFormBuilder(unittest.TestCase):
    """Test form builder."""
    
    def setUp(self):
        self.builder = FormBuilder("test_form", "Test Form")
    
    def test_add_field(self):
        """Test adding a field to form."""
        self.builder.add_field("name", FieldType.TEXT, required=True)
        self.assertEqual(self.builder.get_steps_count(), 1)
    
    def test_multiple_fields(self):
        """Test adding multiple fields."""
        self.builder.add_field("name", FieldType.TEXT) \
                   .add_field("email", FieldType.EMAIL) \
                   .add_field("age", FieldType.NUMBER)
        self.assertEqual(self.builder.get_steps_count(), 3)
    
    def test_build_form(self):
        """Test building form schema."""
        self.builder.add_field("name", FieldType.TEXT, required=True)
        form = self.builder.build()
        
        self.assertEqual(form["id"], "test_form")
        self.assertEqual(len(form["fields"]), 1)
        self.assertEqual(form["fields"][0]["type"], "text")


class TestFormValidator(unittest.TestCase):
    """Test form validation."""
    
    def setUp(self):
        self.form = FormBuilder("test_form", "Test Form") \
            .add_field("email", FieldType.EMAIL, required=True) \
            .add_field("age", FieldType.NUMBER) \
            .build()
        self.validator = FormValidator(self.form)
    
    def test_valid_email(self):
        """Test valid email validation."""
        data = {"email": "test@example.com", "age": 25}
        is_valid, errors = self.validator.validate(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_email(self):
        """Test invalid email validation."""
        data = {"email": "invalid-email", "age": 25}
        is_valid, errors = self.validator.validate(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_required_field(self):
        """Test required field validation."""
        data = {"age": 25}  # Missing required email
        is_valid, errors = self.validator.validate(data)
        self.assertFalse(is_valid)


class TestDocumentManager(unittest.TestCase):
    """Test document manager."""
    
    def setUp(self):
        self.manager = DocumentManager(storage_path="./test_documents")
    
    def test_upload_document(self):
        """Test document upload."""
        doc_id = self.manager.upload_document(
            name="test.pdf",
            file_content=b"test content",
            content_type="application/pdf",
            owner_id="user_001"
        )
        self.assertIsNotNone(doc_id)
        self.assertIn(doc_id, self.manager.documents)
    
    def test_search_documents(self):
        """Test document search."""
        self.manager.upload_document(
            name="report.pdf",
            file_content=b"content",
            content_type="application/pdf",
            owner_id="user_001",
            tags=["report", "2024"]
        )
        
        results = self.manager.search_documents(tags=["report"])
        self.assertGreater(len(results), 0)
    
    def test_access_control(self):
        """Test document access control."""
        doc_id = self.manager.upload_document(
            name="sensitive.pdf",
            file_content=b"content",
            content_type="application/pdf",
            owner_id="user_001"
        )
        
        # Grant access
        self.manager.grant_access(doc_id, "user_002", "view")
        
        # Verify access
        doc = self.manager.get_document(doc_id, "user_002")
        self.assertIsNotNone(doc)


class TestVersionControl(unittest.TestCase):
    """Test version control."""
    
    def setUp(self):
        self.vc = VersionControl()
    
    def test_create_version(self):
        """Test creating a version."""
        version_id = self.vc.create_version(
            document_id="doc_001",
            file_path="./v1.pdf",
            created_by="user_001",
            change_summary="Initial version"
        )
        self.assertIsNotNone(version_id)
    
    def test_get_versions(self):
        """Test getting document versions."""
        self.vc.create_version("doc_001", "./v1.pdf", "user_001", "v1")
        self.vc.create_version("doc_001", "./v2.pdf", "user_002", "v2")
        
        versions = self.vc.get_document_versions("doc_001")
        self.assertEqual(len(versions), 2)


class TestNotificationService(unittest.TestCase):
    """Test notification service."""
    
    def setUp(self):
        self.service = NotificationService()
    
    def test_send_email(self):
        """Test sending email."""
        notif_id = self.service.send_email(
            recipient="test@example.com",
            subject="Test Email"
        )
        self.assertIsNotNone(notif_id)
        self.assertIn(notif_id, self.service.notifications)
    
    def test_register_template(self):
        """Test registering notification template."""
        template = "Hello {name}, welcome!"
        self.service.register_template("welcome", template)
        self.assertIn("welcome", self.service.templates)
    
    def test_send_with_template(self):
        """Test sending with template."""
        self.service.register_template(
            "test_template",
            "Hello {name}!"
        )
        
        notif_id = self.service.send_email(
            recipient="test@example.com",
            subject="Test",
            template_name="test_template",
            template_data={"name": "John"}
        )
        
        self.assertIsNotNone(notif_id)


class TestEventHandler(unittest.TestCase):
    """Test event handler."""
    
    def setUp(self):
        self.handler = EventHandler()
    
    def test_subscribe_and_trigger(self):
        """Test subscribing to and triggering events."""
        called = {"count": 0}
        
        def callback(event):
            called["count"] += 1
        
        self.handler.subscribe("test_event", callback)
        self.handler.trigger_event("test_event", "test_source", {})
        
        self.assertEqual(called["count"], 1)
    
    def test_event_history(self):
        """Test event history tracking."""
        self.handler.trigger_event("test_event", "source_1", {"key": "value"})
        
        history = self.handler.get_event_history()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1]["event_type"], "test_event")


class TestFormProcessor(unittest.TestCase):
    """Test form processor."""
    
    def setUp(self):
        self.processor = FormProcessor()
    
    def test_submit_form(self):
        """Test form submission."""
        submission_id = self.processor.submit_form(
            form_id="test_form",
            form_data={"name": "John", "email": "john@example.com"},
            submitter_id="user_001"
        )
        self.assertIsNotNone(submission_id)
    
    def test_capture_signature(self):
        """Test signature capture."""
        submission_id = self.processor.submit_form(
            form_id="test_form",
            form_data={"name": "John"},
            submitter_id="user_001"
        )
        
        success = self.processor.capture_signature(
            submission_id=submission_id,
            signer_id="user_001",
            signature_data="base64_signature"
        )
        
        self.assertTrue(success)
    
    def test_export_json(self):
        """Test JSON export."""
        submission_id = self.processor.submit_form(
            form_id="test_form",
            form_data={"name": "John"},
            submitter_id="user_001"
        )
        
        json_export = self.processor.export_json(submission_id)
        self.assertIsNotNone(json_export)
        self.assertIn("submission_id", json_export)


if __name__ == '__main__':
    unittest.main()
