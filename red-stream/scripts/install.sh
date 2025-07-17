#!/bin/bash

set -e

echo "Installing Red Stream MCP Server..."

# Build the project
echo "Building project..."
npm install
npm run build

# Create necessary directories
sudo mkdir -p /etc/red-stream
sudo mkdir -p /var/log/red-stream

# Copy service file
echo "Installing systemd service..."
sudo cp system/red-stream.service /etc/systemd/system/

# Set permissions
sudo chown -R x:x /etc/red-stream
sudo chown -R x:x /var/log/red-stream

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
echo "Starting service..."
sudo systemctl enable red-stream
sudo systemctl start red-stream

# Check status
echo "Checking service status..."
sudo systemctl status red-stream

echo "Installation complete. Checking logs..."
journalctl -u red-stream -n 50 --no-pager