#!/bin/bash

set -e

echo "Installing Metrics MCP Server..."

# Create logs directory
sudo mkdir -p /logs/metrics-mcp
sudo chown x:x /logs/metrics-mcp
sudo chmod 755 /logs/metrics-mcp

# Build the project
echo "Building project..."
npm run build

# Copy service file
echo "Installing systemd files..."
sudo cp system/metrics-mcp.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Stop existing service if running
sudo systemctl stop metrics-mcp.service || true

# Enable and start service
echo "Starting service..."
sudo systemctl enable metrics-mcp.service
sudo systemctl start metrics-mcp.service

# Check status
echo "Checking service status..."
sudo systemctl status metrics-mcp.service

echo "Installation complete. Checking logs..."
journalctl -u metrics-mcp -n 50 --no-pager

echo "
Installation completed successfully!

Service name: metrics-mcp
Status: Active
Logs: /logs/metrics-mcp/
Systemd service: /etc/systemd/system/metrics-mcp.service

To check status: systemctl status metrics-mcp
To view logs: journalctl -u metrics-mcp -f
To restart: systemctl restart metrics-mcp
"