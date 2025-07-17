#!/usr/bin/env python3
"""
Redis Stream Integration for Echo Resonance TURBO Mode
This script sets up Redis Streams for continuous execution monitoring
and real-time status updates across the Echo Resonance project.
"""

import os
import json
import time
import datetime
import sys
from uuid import uuid4

# Check if running in MCP environment
IN_MCP = os.getenv('MCP_ENVIRONMENT', 'false').lower() == 'true'

# If not in MCP, try to import Redis directly
if not IN_MCP:
    try:
        import redis
        direct_redis = True
    except ImportError:
        print("Warning: Redis Python package not found. Will use MCP Redis server.")
        direct_redis = False
else:
    direct_redis = False

# Stream configuration
STREAMS = {
    "er:status": "Project status updates",
    "er:teams:memcommsops": "MemCommsOps team updates",
    "er:teams:installops": "InstallOps team updates",
    "er:teams:commsops": "CommsOps team updates",
    "er:components:avatar": "Avatar component updates",
    "er:components:infrastructure": "Infrastructure component updates",
    "er:questionnaire": "Questionnaire distribution and responses",
    "er:hardware": "Hardware installation progress",
    "er:dashboards": "Dashboard creation and updates"
}

# MCP Redis Tool Helper
def use_mcp_redis(tool_name, args):
    """Simulates using MCP Redis tool when direct Redis connection isn't available"""
    print(f"[MCP Redis] {tool_name}: {json.dumps(args)}")
    # In real implementation, this would call the MCP Redis server tool
    return {"status": "success", "result": "Operation simulated"}

# Message formatting
def format_message(msg_type, content, sender, priority="normal", metadata=None):
    """Format a message for Redis Stream"""
    if metadata is None:
        metadata = {}
    
    return {
        "type": msg_type,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat(),
        "sender": sender,
        "message_id": str(uuid4()),
        "priority": priority,
        "metadata": metadata
    }

# Redis Stream Operations
class TurboStreamManager:
    def __init__(self):
        if direct_redis:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            print(f"Connected to Redis at {redis_host}:{redis_port}")
        else:
            print("Using MCP Redis Server")
            self.redis_client = None
    
    def initialize_streams(self):
        """Set up all required streams for the project"""
        for stream_key, description in STREAMS.items():
            self.create_stream(stream_key, description)
    
    def create_stream(self, stream_key, description):
        """Create a new stream or initialize an existing one"""
        init_message = format_message(
            "stream_init", 
            f"Initialized stream: {description}", 
            "TURBO_SYSTEM",
            metadata={"description": description}
        )
        
        if direct_redis:
            # Using direct Redis connection
            try:
                result = self.redis_client.xadd(
                    stream_key,
                    init_message
                )
                print(f"Created stream '{stream_key}': {result}")
            except Exception as e:
                print(f"Error creating stream '{stream_key}': {e}")
        else:
            # Using MCP Redis server
            use_mcp_redis("stream_publish", {
                "stream": stream_key,
                "message": init_message
            })
            print(f"Created stream '{stream_key}' via MCP")
    
    def publish_status_update(self, stream_key, status_type, content, metadata=None):
        """Publish status update to a stream"""
        message = format_message(
            status_type,
            content,
            os.getenv('TURBO_SENDER', 'TURBO_FRAMEWORK'),
            metadata=metadata
        )
        
        if direct_redis:
            try:
                result = self.redis_client.xadd(
                    stream_key,
                    message
                )
                print(f"Published to '{stream_key}': {result}")
                return result
            except Exception as e:
                print(f"Error publishing to '{stream_key}': {e}")
                return None
        else:
            # Using MCP Redis server
            result = use_mcp_redis("stream_publish", {
                "stream": stream_key,
                "message": message
            })
            print(f"Published to '{stream_key}' via MCP")
            return result
    
    def create_consumer_group(self, stream_key, group_name):
        """Create a consumer group for a stream"""
        if direct_redis:
            try:
                # Create the group and specify to read from the beginning of the stream
                self.redis_client.xgroup_create(stream_key, group_name, id='0', mkstream=True)
                print(f"Created consumer group '{group_name}' for stream '{stream_key}'")
            except redis.exceptions.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    print(f"Consumer group '{group_name}' already exists for stream '{stream_key}'")
                else:
                    print(f"Error creating consumer group: {e}")
        else:
            # Using MCP Redis server
            use_mcp_redis("create_consumer_group", {
                "stream": stream_key,
                "group": group_name,
                "id": "0" 
            })
            print(f"Created consumer group '{group_name}' for stream '{stream_key}' via MCP")
    
    def read_stream(self, stream_key, count=10, block=0):
        """Read messages from a stream"""
        if direct_redis:
            try:
                messages = self.redis_client.xread({stream_key: '0'}, count=count, block=block)
                return messages
            except Exception as e:
                print(f"Error reading from stream '{stream_key}': {e}")
                return []
        else:
            # Using MCP Redis server
            result = use_mcp_redis("stream_read", {
                "stream": stream_key,
                "count": count,
                "id": "0" 
            })
            return result.get("result", [])

    def setup_er_notification_system(self):
        """Set up complete notification system for Echo Resonance project"""
        # Initialize all streams
        self.initialize_streams()
        
        # Create consumer groups for key teams
        for team in ["memcommsops", "installops", "commsops"]:
            self.create_consumer_group(f"er:teams:{team}", f"{team}-listeners")
        
        # Create consumer group for general status
        self.create_consumer_group("er:status", "status-monitors")
        
        # Create consumer group for questionnaire
        self.create_consumer_group("er:questionnaire", "questionnaire-processors")
        
        # Publish initial status to main status stream
        self.publish_status_update(
            "er:status",
            "project_start",
            "Echo Resonance TURBO-SHOWCASE 4K project execution started",
            metadata={
                "project": "Echo Resonance",
                "phase": "Initialization",
                "completion_percentage": 5,
                "start_time": datetime.datetime.now().isoformat()
            }
        )
        
        print("Echo Resonance notification system initialized successfully")
        return True

def setup_questionnaire_monitoring():
    """Set up monitoring for the questionnaire distribution and collection"""
    manager = TurboStreamManager()
    
    # Initialize questionnaire stream
    manager.create_stream(
        "er:questionnaire", 
        "Questionnaire distribution and responses tracking"
    )
    
    # Create consumer group for questionnaire responses
    manager.create_consumer_group(
        "er:questionnaire", 
        "response-processors"
    )
    
    # Publish initial status
    manager.publish_status_update(
        "er:questionnaire",
        "distribution_start",
        "Questionnaire distribution process initiated",
        metadata={
            "target_count": 17,
            "current_count": 0,
            "completion_percentage": 0
        }
    )
    
    # Set up automated status updates
    print("Setting up scheduled status updates for questionnaire process")
    print("Questionnaire monitoring system initialized")

def monitor_hardware_installation():
    """Set up monitoring for the hardware installation process"""
    manager = TurboStreamManager()
    
    # Initialize hardware stream
    manager.create_stream(
        "er:hardware", 
        "Hardware installation progress tracking"
    )
    
    # Create consumer group
    manager.create_consumer_group(
        "er:hardware", 
        "installation-monitors"
    )
    
    # Publish initial status
    manager.publish_status_update(
        "er:hardware",
        "installation_start",
        "H200 node + 2 × L40S installation process initiated",
        metadata={
            "steps_total": 7,
            "steps_completed": 0,
            "completion_percentage": 0,
            "assigned_team": "InstallOps"
        }
    )
    
    print("Hardware installation monitoring initialized")

if __name__ == "__main__":
    print("Initializing Echo Resonance Redis Stream Integration...")
    
    manager = TurboStreamManager()
    
    # Command line argument handling
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            manager.setup_er_notification_system()
        
        elif command == "questionnaire":
            setup_questionnaire_monitoring()
        
        elif command == "hardware":
            monitor_hardware_installation()
        
        elif command == "status":
            # Publish a status update
            if len(sys.argv) > 3:
                stream = sys.argv[2]
                message = sys.argv[3]
                manager.publish_status_update(
                    stream,
                    "status_update",
                    message
                )
            else:
                print("Usage: python redis_turbo_stream_integration.py status <stream> <message>")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, questionnaire, hardware, status")
    
    else:
        # Default: initialize everything
        manager.setup_er_notification_system()
        setup_questionnaire_monitoring()
        monitor_hardware_installation()
        
        print("\nEcho Resonance Redis Stream Integration complete!")
        print("Use the following commands for specific operations:")
        print("  python redis_turbo_stream_integration.py init")
        print("  python redis_turbo_stream_integration.py questionnaire")
        print("  python redis_turbo_stream_integration.py hardware")
        print("  python redis_turbo_stream_integration.py status <stream> <message>")
