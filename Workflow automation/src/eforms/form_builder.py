"""
Form Builder - Construct dynamic e-forms with validation rules.

Creates forms that can be rendered in UI, validated on submission,
and exported to JSON/CSV for reporting and archiving.
"""

import uuid
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


class FieldType(Enum):
    """Supported form field types."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE = "file"
    SIGNATURE = "signature"


class FormBuilder:
    """
    Fluent API for building e-forms.
    
    Example:
        form = FormBuilder("employment_form", "Employment Application") \
            .add_field("full_name", FieldType.TEXT, required=True) \
            .add_field("email", FieldType.EMAIL, required=True) \
            .add_field("department", FieldType.SELECT, 
                      options=["HR", "IT", "Finance"], required=True) \
            .add_field("resume", FieldType.FILE, required=True) \
            .add_field("signature", FieldType.SIGNATURE, required=True) \
            .add_section("Personal Information") \
            .build()
    """
    
    def __init__(self, form_id: str, title: str, description: str = ""):
        """Initialize form builder."""
        self.form_id = form_id
        self.title = title
        self.description = description
        self.fields: List[Dict] = []
        self.sections: List[Dict] = []
        self.validation_rules: Dict[str, List[Dict]] = {}
        
    def add_section(self, section_name: str, description: str = "") -> 'FormBuilder':
        """Add a section/group to the form."""
        self.sections.append({
            "name": section_name,
            "description": description,
            "field_count": len(self.fields)
        })
        return self
    
    def add_field(
        self,
        field_id: str,
        field_type: FieldType,
        label: str = "",
        required: bool = False,
        placeholder: str = "",
        default_value: Any = None,
        options: Optional[List[str]] = None,
        help_text: str = "",
        validation_rules: Optional[List[Dict]] = None
    ) -> 'FormBuilder':
        """
        Add a field to the form.
        
        Args:
            field_id: Unique identifier for the field
            field_type: Type of field
            label: Display label
            required: Whether field is required
            placeholder: Placeholder text
            default_value: Default value
            options: Available options (for select/radio)
            help_text: Help text for the user
            validation_rules: List of validation rules for this field
            
        Returns:
            Self for method chaining
        """
        field = {
            "id": field_id,
            "type": field_type.value,
            "label": label or field_id,
            "required": required,
            "placeholder": placeholder,
            "default_value": default_value,
            "options": options,
            "help_text": help_text
        }
        
        self.fields.append(field)
        
        if validation_rules:
            self.validation_rules[field_id] = validation_rules
        
        return self
    
    def add_validation(
        self,
        field_id: str,
        rule_type: str,
        value: Any = None,
        message: str = ""
    ) -> 'FormBuilder':
        """
        Add a validation rule to a field.
        
        Args:
            field_id: ID of the field to validate
            rule_type: Type of validation (min_length, max_length, pattern, custom)
            value: Validation value (e.g., minimum length)
            message: Error message
            
        Returns:
            Self for method chaining
        """
        if field_id not in self.validation_rules:
            self.validation_rules[field_id] = []
        
        self.validation_rules[field_id].append({
            "type": rule_type,
            "value": value,
            "message": message or f"Validation failed: {rule_type}"
        })
        
        return self
    
    def add_conditional_field(
        self,
        field_id: str,
        field_type: FieldType,
        condition: Dict[str, Any],
        **kwargs
    ) -> 'FormBuilder':
        """
        Add a field that appears conditionally based on other field values.
        
        Args:
            field_id: Unique identifier for the field
            field_type: Type of field
            condition: Condition for showing this field
            **kwargs: Additional field parameters
            
        Returns:
            Self for method chaining
        """
        field = {
            "id": field_id,
            "type": field_type.value,
            "condition": condition,
            **kwargs
        }
        self.fields.append(field)
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return the form definition.
        
        Returns:
            Complete form definition
        """
        return {
            "id": self.form_id,
            "title": self.title,
            "description": self.description,
            "created_at": datetime.now().isoformat(),
            "fields": self.fields,
            "sections": self.sections,
            "validation_rules": self.validation_rules,
            "field_count": len(self.fields)
        }
    
    def export_schema(self) -> Dict[str, Any]:
        """Export form schema for frontend rendering."""
        return self.build()
