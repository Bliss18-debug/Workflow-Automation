"""
Event Handler - Processes events that trigger workflows.

Supports various event types: form submission, document upload, scheduled tasks,
external API webhooks, etc.
"""

import logging
from enum import Enum
from typing import Dict, Callable, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Supported event types."""
    FORM_SUBMITTED = "form_submitted"
    DOCUMENT_UPLOADED = "document_uploaded"
    APPROVAL_REQUESTED = "approval_requested"
    SCHEDULED_TASK = "scheduled_task"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class EventHandler:
    """
    Handles event-based workflow triggers.
    
    Maps events to workflows and manages event routing to the workflow engine.
    """
    
    def __init__(self):
        """Initialize event handler."""
        self.event_subscriptions: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict] = []
        logger.info("EventHandler initialized")
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is triggered
        """
        if event_type not in self.event_subscriptions:
            self.event_subscriptions[event_type] = []
        
        self.event_subscriptions[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")
    
    def trigger_event(
        self,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Trigger an event and notify all subscribers.
        
        Args:
            event_type: Type of event being triggered
            source: Source of the event (e.g., 'form_submission', 'webhook_service')
            data: Event data/payload
            metadata: Additional metadata about the event
            
        Returns:
            Event ID for tracking
        """
        import uuid
        
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "source": source,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "processed": False
        }
        
        # Store in history
        self.event_history.append(event)
        
        logger.info(f"Event triggered: {event_type} (ID: {event_id}) from {source}")
        
        # Call all subscribers
        if event_type in self.event_subscriptions:
            for callback in self.event_subscriptions[event_type]:
                try:
                    callback(event)
                    event["processed"] = True
                except Exception as e:
                    logger.error(f"Error processing event {event_id}: {str(e)}")
        else:
            logger.warning(f"No subscribers for event type: {event_type}")
        
        return event_id
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """Get event details by ID."""
        for event in self.event_history:
            if event["event_id"] == event_id:
                return event
        return None
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get event history, optionally filtered.
        
        Args:
            event_type: Filter by event type
            source: Filter by source
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        results = self.event_history[-limit:]
        
        if event_type:
            results = [e for e in results if e["event_type"] == event_type]
        if source:
            results = [e for e in results if e["source"] == source]
        
        return results
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self.event_subscriptions:
            self.event_subscriptions[event_type].remove(callback)
            logger.info(f"Unsubscribed from event: {event_type}")
