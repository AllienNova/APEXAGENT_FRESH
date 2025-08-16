"""
Event visualization utilities for the ApexAgent event system.

This module provides tools for visualizing event flow, relationships, and statistics
for debugging and monitoring purposes.
"""

import asyncio
from datetime import datetime
import json
from typing import Dict, List, Optional, Set, Tuple, Union
import uuid

from .event import Event
from .event_manager import EventManager


class EventVisualizer:
    """
    Visualizer for events in the ApexAgent system.
    
    The EventVisualizer provides tools for creating visual representations of events,
    event flow, and event relationships for debugging and monitoring.
    """
    
    def __init__(self, event_manager: Optional[EventManager] = None):
        """
        Initialize a new EventVisualizer.
        
        Args:
            event_manager: Optional EventManager to connect to
        """
        self._event_manager = event_manager
        self._visualization_data = {
            "events": [],
            "relationships": [],
            "stats": {}
        }
        self._event_types_seen = set()
        self._sources_seen = set()
        
        # If event manager is provided, register as a subscriber
        if event_manager:
            asyncio.create_task(self._register_with_manager())
    
    async def _register_with_manager(self):
        """Register with the event manager as a subscriber."""
        if self._event_manager:
            await self._event_manager.register_callback(
                self.process_event,
                event_types=".*",  # Subscribe to all events
            )
    
    async def process_event(self, event: Event) -> None:
        """
        Process an event for visualization.
        
        Args:
            event: The event to process
        """
        # Add event to visualization data
        event_data = {
            "id": event.id,
            "type": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "priority": event.priority.name,
            "parent_id": event.parent_id
        }
        self._visualization_data["events"].append(event_data)
        
        # Add relationship if parent_id is set
        if event.parent_id:
            relationship = {
                "from": event.parent_id,
                "to": event.id,
                "type": "parent-child"
            }
            self._visualization_data["relationships"].append(relationship)
        
        # Update stats
        self._event_types_seen.add(event.event_type)
        self._sources_seen.add(event.source)
        
        # Update statistics
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Update visualization statistics."""
        events = self._visualization_data["events"]
        self._visualization_data["stats"] = {
            "total_events": len(events),
            "event_types": len(self._event_types_seen),
            "sources": len(self._sources_seen),
            "first_event_time": events[0]["timestamp"] if events else None,
            "last_event_time": events[-1]["timestamp"] if events else None
        }
    
    def get_visualization_data(self) -> Dict:
        """
        Get the current visualization data.
        
        Returns:
            Dictionary containing visualization data
        """
        return self._visualization_data.copy()
    
    def clear_visualization_data(self) -> None:
        """Clear all visualization data."""
        self._visualization_data = {
            "events": [],
            "relationships": [],
            "stats": {}
        }
        self._event_types_seen = set()
        self._sources_seen = set()
    
    def generate_event_flow_diagram(self, format: str = "mermaid") -> str:
        """
        Generate a diagram showing event flow.
        
        Args:
            format: Output format ("mermaid", "dot", "json")
            
        Returns:
            String representation of the diagram in the specified format
        """
        if format == "mermaid":
            return self._generate_mermaid_diagram()
        elif format == "dot":
            return self._generate_dot_diagram()
        elif format == "json":
            return json.dumps(self._visualization_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_mermaid_diagram(self) -> str:
        """
        Generate a Mermaid.js diagram of event flow.
        
        Returns:
            Mermaid.js diagram as a string
        """
        events = self._visualization_data["events"]
        relationships = self._visualization_data["relationships"]
        
        # Start with diagram header
        diagram = ["graph TD;"]
        
        # Add nodes for each event
        for event in events:
            node_id = f"event_{event['id'].replace('-', '_')}"
            label = f"{event['type']}\\n({event['source']})"
            diagram.append(f"    {node_id}[\"{label}\"];")
        
        # Add edges for relationships
        for rel in relationships:
            from_id = f"event_{rel['from'].replace('-', '_')}"
            to_id = f"event_{rel['to'].replace('-', '_')}"
            diagram.append(f"    {from_id} --> {to_id};")
        
        return "\n".join(diagram)
    
    def _generate_dot_diagram(self) -> str:
        """
        Generate a DOT (Graphviz) diagram of event flow.
        
        Returns:
            DOT diagram as a string
        """
        events = self._visualization_data["events"]
        relationships = self._visualization_data["relationships"]
        
        # Start with diagram header
        diagram = ["digraph EventFlow {"]
        diagram.append("    rankdir=TD;")
        diagram.append("    node [shape=box, style=filled, fillcolor=lightblue];")
        
        # Add nodes for each event
        for event in events:
            node_id = f"event_{event['id'].replace('-', '_')}"
            label = f"{event['type']}\\n({event['source']})"
            diagram.append(f"    {node_id} [label=\"{label}\"];")
        
        # Add edges for relationships
        for rel in relationships:
            from_id = f"event_{rel['from'].replace('-', '_')}"
            to_id = f"event_{rel['to'].replace('-', '_')}"
            diagram.append(f"    {from_id} -> {to_id};")
        
        diagram.append("}")
        return "\n".join(diagram)
    
    def generate_event_timeline(self) -> str:
        """
        Generate a timeline representation of events.
        
        Returns:
            Timeline as a formatted string
        """
        events = sorted(
            self._visualization_data["events"],
            key=lambda e: e["timestamp"]
        )
        
        if not events:
            return "No events to display"
        
        # Calculate time range
        start_time = datetime.fromisoformat(events[0]["timestamp"])
        end_time = datetime.fromisoformat(events[-1]["timestamp"])
        duration = (end_time - start_time).total_seconds()
        
        timeline = ["Event Timeline:"]
        timeline.append(f"Start: {start_time.isoformat()} | End: {end_time.isoformat()} | Duration: {duration:.2f}s")
        timeline.append("-" * 80)
        
        # Add each event to the timeline
        for event in events:
            event_time = datetime.fromisoformat(event["timestamp"])
            relative_time = (event_time - start_time).total_seconds()
            timeline.append(
                f"[{relative_time:.3f}s] {event['type']} from {event['source']} "
                f"(Priority: {event['priority']})"
            )
        
        return "\n".join(timeline)
    
    def generate_event_statistics(self) -> str:
        """
        Generate statistics about events.
        
        Returns:
            Statistics as a formatted string
        """
        events = self._visualization_data["events"]
        
        if not events:
            return "No events to analyze"
        
        # Count events by type
        event_type_counts = {}
        for event in events:
            event_type = event["type"]
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Count events by source
        source_counts = {}
        for event in events:
            source = event["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Count events by priority
        priority_counts = {}
        for event in events:
            priority = event["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Format statistics
        stats = ["Event Statistics:"]
        stats.append(f"Total Events: {len(events)}")
        stats.append(f"Unique Event Types: {len(event_type_counts)}")
        stats.append(f"Unique Sources: {len(source_counts)}")
        
        stats.append("\nEvents by Type:")
        for event_type, count in sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True):
            stats.append(f"  {event_type}: {count}")
        
        stats.append("\nEvents by Source:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            stats.append(f"  {source}: {count}")
        
        stats.append("\nEvents by Priority:")
        for priority, count in sorted(priority_counts.items()):
            stats.append(f"  {priority}: {count}")
        
        return "\n".join(stats)
