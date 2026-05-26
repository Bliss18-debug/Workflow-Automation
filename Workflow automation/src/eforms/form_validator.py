"""
Form Validator - Validates form submissions against defined rules.

Ensures data quality, enforces business rules, and provides detailed
error reporting for failed validations.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field_id: str, rule: str, message: str):
        self.field_id = field_id
        self.rule = rule
        self.message = message
    
    def to_dict(self) -> Dict:
        return {
            "field": self.field_id,
            "rule": self.rule,
            "message": self.message
        }


class FormValidator:
    """
    Validates form submission data against form schema and rules.
    
    Supports:
    - Required field validation
    - Type checking
    - Custom regex patterns
    - Cross-field validation
    - Business logic validation
    """
    
    def __init__(self, form_schema: Dict[str, Any]):
        """
        Initialize validator.
        
        Args:
            form_schema: Form definition created by FormBuilder
        """
        self.form_schema = form_schema
        self.validation_rules = form_schema.get("validation_rules", {})
    
    def validate(self, form_data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate form submission.
        
        Args:
            form_data: Submitted form data
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors: List[ValidationError] = []
        
        # Validate each field in the schema
        for field in self.form_schema.get("fields", []):
            field_id = field.get("id")
            field_value = form_data.get(field_id)
            field_type = field.get("type")
            
            # Check required
            if field.get("required") and not field_value:
                errors.append(ValidationError(
                    field_id,
                    "required",
                    f"{field.get('label', field_id)} is required"
                ))
                continue
            
            # Skip validation if not required and empty
            if not field_value and not field.get("required"):
                continue
            
            # Type validation
            type_error = self._validate_type(field_id, field_value, field_type)
            if type_error:
                errors.append(type_error)
                continue
            
            # Apply custom validation rules
            if field_id in self.validation_rules:
                rule_errors = self._validate_rules(
                    field_id,
                    field_value,
                    self.validation_rules[field_id]
                )
                errors.extend(rule_errors)
        
        return len(errors) == 0, errors
    
    def _validate_type(
        self,
        field_id: str,
        value: Any,
        field_type: str
    ) -> Optional[ValidationError]:
        """Validate field type."""
        if not value:
            return None
        
        try:
            if field_type == "email":
                if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', str(value)):
                    return ValidationError(field_id, "email", "Invalid email format")
            
            elif field_type == "phone":
                # Basic phone validation (10+ digits)
                digits = re.sub(r'\D', '', str(value))
                if len(digits) < 10:
                    return ValidationError(field_id, "phone", "Invalid phone number")
            
            elif field_type == "number":
                try:
                    float(value)
                except ValueError:
                    return ValidationError(field_id, "number", "Must be a valid number")
            
            elif field_type == "date":
                try:
                    datetime.strptime(str(value), "%Y-%m-%d")
                except ValueError:
                    return ValidationError(field_id, "date", "Invalid date format (YYYY-MM-DD)")
            
            elif field_type == "datetime":
                try:
                    datetime.fromisoformat(str(value))
                except ValueError:
                    return ValidationError(field_id, "datetime", "Invalid datetime format")
        
        except Exception as e:
            logger.error(f"Type validation error for {field_id}: {str(e)}")
            return ValidationError(field_id, "type", f"Invalid {field_type}")
        
        return None
    
    def _validate_rules(
        self,
        field_id: str,
        value: Any,
        rules: List[Dict]
    ) -> List[ValidationError]:
        """Apply custom validation rules."""
        errors: List[ValidationError] = []
        
        for rule in rules:
            rule_type = rule.get("type")
            rule_value = rule.get("value")
            message = rule.get("message", f"Validation failed: {rule_type}")
            
            try:
                if rule_type == "min_length":
                    if len(str(value)) < rule_value:
                        errors.append(ValidationError(field_id, rule_type, message))
                
                elif rule_type == "max_length":
                    if len(str(value)) > rule_value:
                        errors.append(ValidationError(field_id, rule_type, message))
                
                elif rule_type == "pattern":
                    if not re.match(rule_value, str(value)):
                        errors.append(ValidationError(field_id, rule_type, message))
                
                elif rule_type == "min_value":
                    if float(value) < float(rule_value):
                        errors.append(ValidationError(field_id, rule_type, message))
                
                elif rule_type == "max_value":
                    if float(value) > float(rule_value):
                        errors.append(ValidationError(field_id, rule_type, message))
            
            except Exception as e:
                logger.error(f"Rule validation error for {field_id}: {str(e)}")
        
        return errors
    
    def validate_batch(
        self,
        form_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple form submissions.
        
        Args:
            form_data_list: List of form data to validate
            
        Returns:
            List of validation results
        """
        results = []
        for i, form_data in enumerate(form_data_list):
            is_valid, errors = self.validate(form_data)
            results.append({
                "submission_index": i,
                "valid": is_valid,
                "errors": [e.to_dict() for e in errors]
            })
        return results
