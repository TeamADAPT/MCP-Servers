"""MCP Atlassian server module.

This module provides a simple MCP server for Atlassian integration.
"""

import os
import sys
import logging
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mcp-atlassian")

def main():
    """Run the MCP Atlassian server."""
    logger.info("Starting MCP Atlassian server...")
    
    try:
        # Keep the server running and respond to MCP protocol messages
        logger.info("MCP Atlassian server is running. Press Ctrl+C to stop.")
        
        # Simple MCP protocol implementation
        while True:
            try:
                # Read a line from stdin (MCP protocol messages)
                line = sys.stdin.readline()
                if not line:
                    time.sleep(1)
                    continue
                
                # Try to parse the line as JSON
                try:
                    message = json.loads(line)
                    logger.info(f"Received message: {message}")
                    
                    # Handle different message types
                    if message.get("jsonrpc") == "2.0":
                        method = message.get("method")
                        params = message.get("params", {})
                        message_id = message.get("id")
                        
                        # Handle different methods
                        if method == "list_tools":
                            # Respond with an empty list of tools
                            response = {
                                "jsonrpc": "2.0",
                                "id": message_id,
                                "result": []
                            }
                            sys.stdout.write(json.dumps(response) + "\n")
                            sys.stdout.flush()
                            logger.info(f"Sent response: {response}")
                        
                        elif method == "list_resources":
                            # Respond with an empty list of resources
                            response = {
                                "jsonrpc": "2.0",
                                "id": message_id,
                                "result": []
                            }
                            sys.stdout.write(json.dumps(response) + "\n")
                            sys.stdout.flush()
                            logger.info(f"Sent response: {response}")
                        
                        else:
                            # Respond with an error for unknown methods
                            response = {
                                "jsonrpc": "2.0",
                                "id": message_id,
                                "error": {
                                    "code": -32601,
                                    "message": f"Method not found: {method}"
                                }
                            }
                            sys.stdout.write(json.dumps(response) + "\n")
                            sys.stdout.flush()
                            logger.info(f"Sent error response: {response}")
                    
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON message: {line}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
            
            # Log a heartbeat message every 60 seconds
            time.sleep(60)
            logger.info("MCP Atlassian server is still alive.")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Stopping MCP Atlassian server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
