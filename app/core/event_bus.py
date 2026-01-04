"""
Event System - Core Infrastructure
Implements Producer-Consumer pattern with Event Bus.
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class EventType(Enum):
    """All event types in the system."""
    # Member events
    MEMBER_CREATED = "member.created"
    MEMBER_UPDATED = "member.updated"
    MEMBER_DELETED = "member.deleted"
    MEMBER_SEARCH = "member.search"
    
    # Cycle events
    CYCLE_CREATED = "cycle.created"
    CYCLE_UPDATED = "cycle.updated"
    CYCLE_DELETED = "cycle.deleted"
    CYCLE_STATUS_CHANGED = "cycle.status_changed"
    
    # Bidding events
    BID_PLACED = "bid.placed"
    BID_WON = "bid.won"
    
    # Transaction events
    PAYMENT_MADE = "payment.made"
    COLLECTION_EXECUTED = "collection.executed"
    
    # UI events
    DATA_REFRESH_REQUESTED = "ui.refresh_requested"
    NOTIFICATION_SHOW = "ui.notification_show"

@dataclass
class Event:
    """Base event class."""
    type: EventType
    data: Any = None
    source: str = None

class EventBus(QObject):
    """
    Central Event Bus using Qt Signals.
    Producers emit events, Consumers subscribe to events.
    """
    
    # Qt Signal for event emission
    event_emitted = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self._subscribers = {}
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to listen for
            handler: Callback function to handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Emit Qt signal (for cross-thread safety)
        self.event_emitted.emit(event)
        
        # Call subscribers directly (same thread)
        if event.type in self._subscribers:
            for handler in self._subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event.type}: {e}")
    
    def clear_all(self):
        """Clear all subscribers (for testing)."""
        self._subscribers.clear()

_event_bus = None

def get_event_bus():
    """Get the global event bus instance (lazy initialization)."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
