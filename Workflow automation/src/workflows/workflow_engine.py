"""
Workflow Engine - Core orchestration engine for automated processes.

Handles workflow execution, state management, and event processing.
Supports triggers (form submission, document upload), actions (notifications, archiving),
and conditional logic for complex business processes.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, asdict
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    id: str
    name: str
    action: str
    config: Dict[str, Any]
    conditions: Optional[List[Dict[str, Any]]] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    retry_count: int = 3

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class WorkflowExecution:
    """Tracks workflow execution details."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = None
    logs: List[str] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.logs is None:
            self.logs = []


class WorkflowEngine:
    """
    Core workflow execution engine.
    
    Executes workflows, manages state, handles events, and coordinates actions.
    Supports conditional logic, retries, and error handling.
    """
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.workflows: Dict[str, Dict] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.event_handlers: List[Callable] = []
        logger.info("WorkflowEngine initialized")

    def register_workflow(self, workflow_id: str, workflow_definition: Dict) -> None:
        """
        Register a workflow definition.
        
        Args:
            workflow_id: Unique workflow identifier
            workflow_definition: Workflow structure with steps and configuration
        """
        self.workflows[workflow_id] = workflow_definition
        logger.info(f"Workflow registered: {workflow_id}")

    def register_action(self, action_name: str, handler: Callable) -> None:
        """
        Register an action handler.
        
        Args:
            action_name: Name of the action (e.g., 'send_email', 'archive_document')
            handler: Callable that executes the action
        """
        self.action_handlers[action_name] = handler
        logger.info(f"Action handler registered: {action_name}")

    def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any]) -> str:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of workflow to execute
            trigger_data: Data from the triggering event
            
        Returns:
            Execution ID for tracking
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        # Create execution tracking object
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            current_step=self.workflows[workflow_id]["steps"][0]["id"],
            started_at=datetime.now(),
            context=trigger_data
        )
        self.executions[execution_id] = execution
        
        logger.info(f"Workflow execution started: {execution_id} (workflow: {workflow_id})")

        try:
            # Execute workflow steps
            current_step_id = self.workflows[workflow_id]["steps"][0]["id"]
            
            while current_step_id:
                step = self._find_step(workflow_id, current_step_id)
                if not step:
                    break

                # Check conditions
                if step.get("conditions"):
                    if not self._evaluate_conditions(step["conditions"], execution.context):
                        current_step_id = step.get("on_failure")
                        continue

                # Execute action
                try:
                    execution.logs.append(f"[{datetime.now().isoformat()}] Executing step: {step['id']}")
                    self._execute_action(step, execution)
                    current_step_id = step.get("on_success")
                except Exception as e:
                    logger.error(f"Error in step {step['id']}: {str(e)}")
                    execution.logs.append(f"[{datetime.now().isoformat()}] Error: {str(e)}")
                    current_step_id = step.get("on_failure")

            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            logger.info(f"Workflow execution completed: {execution_id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            execution.logs.append(f"[{datetime.now().isoformat()}] Workflow failed: {str(e)}")
            logger.error(f"Workflow execution failed: {execution_id} - {str(e)}")

        return execution_id

    def _find_step(self, workflow_id: str, step_id: str) -> Optional[Dict]:
        """Find a step in a workflow."""
        for step in self.workflows[workflow_id]["steps"]:
            if step["id"] == step_id:
                return step
        return None

    def _evaluate_conditions(self, conditions: List[Dict], context: Dict) -> bool:
        """Evaluate workflow conditions against context data."""
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            context_value = context.get(field)
            
            if operator == "equals" and context_value != value:
                return False
            elif operator == "contains" and value not in str(context_value):
                return False
            elif operator == "greater_than" and context_value <= value:
                return False
            elif operator == "less_than" and context_value >= value:
                return False
        
        return True

    def _execute_action(self, step: Dict, execution: WorkflowExecution) -> None:
        """Execute an action associated with a step."""
        action_name = step.get("action")
        config = step.get("config", {})
        
        if action_name not in self.action_handlers:
            raise ValueError(f"Unknown action: {action_name}")
        
        handler = self.action_handlers[action_name]
        result = handler(execution.context, config)
        
        # Store result in execution context
        execution.context[f"result_{step['id']}"] = result

    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status and details of a workflow execution."""
        return self.executions.get(execution_id)

    def get_execution_logs(self, execution_id: str) -> List[str]:
        """Get execution logs."""
        execution = self.executions.get(execution_id)
        return execution.logs if execution else []

    def list_executions(self, workflow_id: Optional[str] = None) -> List[Dict]:
        """List all executions, optionally filtered by workflow."""
        results = []
        for exec_id, execution in self.executions.items():
            if workflow_id and execution.workflow_id != workflow_id:
                continue
            results.append({
                "execution_id": execution.execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            })
        return results
