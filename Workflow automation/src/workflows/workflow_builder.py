"""
Workflow Builder - Fluent API for constructing workflows.

Provides a simple, intuitive interface for defining workflows without
needing to manually structure complex JSON/dictionaries.
"""

import uuid
from typing import Dict, List, Callable, Any, Optional


class WorkflowBuilder:
    """
    Fluent builder for creating workflow definitions.
    
    Example:
        builder = WorkflowBuilder("approval_workflow")
        builder.add_step("check_form", "validate_form", {"required_fields": ["name", "email"]}) \
               .add_step("send_approval", "send_notification", {"recipient": "hr@company.com"}) \
               .add_condition("approval_step", "status", "equals", "approved", 
                            on_success="archive", on_failure="send_rejection") \
               .build()
    """
    
    def __init__(self, workflow_id: str, description: str = ""):
        """Initialize workflow builder."""
        self.workflow_id = workflow_id
        self.description = description
        self.steps: List[Dict] = []
        self.step_map: Dict[str, int] = {}  # Map step IDs to indices
        
    def add_step(
        self, 
        step_id: str,
        action: str,
        config: Dict[str, Any],
        description: str = ""
    ) -> 'WorkflowBuilder':
        """
        Add a step to the workflow.
        
        Args:
            step_id: Unique identifier for this step
            action: Name of the action to execute
            config: Configuration for the action
            description: Human-readable description
            
        Returns:
            Self for method chaining
        """
        step = {
            "id": step_id,
            "action": action,
            "config": config,
            "description": description,
            "conditions": None,
            "on_success": None,
            "on_failure": None,
            "retry_count": 3
        }
        self.step_map[step_id] = len(self.steps)
        self.steps.append(step)
        return self
    
    def add_condition(
        self,
        step_id: str,
        field: str,
        operator: str,
        value: Any,
        on_success: Optional[str] = None,
        on_failure: Optional[str] = None
    ) -> 'WorkflowBuilder':
        """
        Add a condition to a step.
        
        Args:
            step_id: ID of the step to add condition to
            field: Field in context to check
            operator: Comparison operator (equals, contains, greater_than, less_than)
            value: Expected value
            on_success: Step to execute if condition is true
            on_failure: Step to execute if condition is false
            
        Returns:
            Self for method chaining
        """
        if step_id not in self.step_map:
            raise ValueError(f"Step not found: {step_id}")
        
        step_index = self.step_map[step_id]
        step = self.steps[step_index]
        
        if step["conditions"] is None:
            step["conditions"] = []
        
        step["conditions"].append({
            "field": field,
            "operator": operator,
            "value": value
        })
        
        if on_success:
            step["on_success"] = on_success
        if on_failure:
            step["on_failure"] = on_failure
        
        return self
    
    def link_steps(self, from_step: str, to_step: str, on_failure: bool = False) -> 'WorkflowBuilder':
        """
        Link two steps together.
        
        Args:
            from_step: Source step ID
            to_step: Destination step ID
            on_failure: If True, link as failure path; otherwise as success path
            
        Returns:
            Self for method chaining
        """
        if from_step not in self.step_map:
            raise ValueError(f"Step not found: {from_step}")
        
        step_index = self.step_map[from_step]
        step = self.steps[step_index]
        
        if on_failure:
            step["on_failure"] = to_step
        else:
            step["on_success"] = to_step
        
        return self
    
    def set_retry(self, step_id: str, retry_count: int) -> 'WorkflowBuilder':
        """Set the retry count for a step."""
        if step_id not in self.step_map:
            raise ValueError(f"Step not found: {step_id}")
        
        step_index = self.step_map[step_id]
        self.steps[step_index]["retry_count"] = retry_count
        return self
    
    def build(self) -> Dict:
        """
        Build and return the workflow definition.
        
        Returns:
            Complete workflow definition ready for execution
        """
        # Auto-link steps if not already linked
        for i, step in enumerate(self.steps):
            if step["on_success"] is None and i < len(self.steps) - 1:
                step["on_success"] = self.steps[i + 1]["id"]
        
        return {
            "id": self.workflow_id,
            "description": self.description,
            "steps": self.steps,
            "created_at": None  # Will be set at execution
        }
    
    def get_steps_count(self) -> int:
        """Get the number of steps in the workflow."""
        return len(self.steps)
