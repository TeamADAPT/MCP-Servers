#!/bin/bash
# Installation script for MCP Atlassian as a systemd service
# This script installs the MCP Atlassian integration as a systemd service

set -e

# Configuration
SERVICE_NAME="mcp-atlassian"
SERVICE_DESCRIPTION="MCP Atlassian Integration Service"
INSTALL_DIR="/opt/mcp-atlassian"
CONFIG_DIR="/etc/mcp-atlassian"
LOG_DIR="/var/log/mcp-atlassian"
USER="$USER"
GROUP="$USER"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Warning: Not running as root. Service installation may fail.${NC}"
  echo "Please run with sudo if you encounter permission errors."
  echo ""
  read -p "Continue anyway? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Installation aborted.${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}Starting MCP Atlassian installation...${NC}"

# Get the current directory (where the script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create necessary directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

# Copy files
echo "Copying files..."
cp -r "$PROJECT_DIR/src" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/tools" "$INSTALL_DIR/"
cp "$PROJECT_DIR/pyproject.toml" "$INSTALL_DIR/"
cp "$PROJECT_DIR/README.md" "$INSTALL_DIR/"
cp "$PROJECT_DIR/CHANGELOG.md" "$INSTALL_DIR/"

# Create default configuration
if [ ! -f "$CONFIG_DIR/feature_flags.json" ]; then
  echo "Creating default feature configuration..."
  cat > "$CONFIG_DIR/feature_flags.json" << EOF
{
  "enhanced_jira": false,
  "enhanced_confluence": false,
  "jsm": false,
  "jsm_approvals": false,
  "jsm_forms": false,
  "jsm_knowledge_base": false,
  "jsm_queue": false,
  "bitbucket": false,
  "bitbucket_integration": false,
  "bitbucket_pipeline": false,
  "space_management": false,
  "template_management": false,
  "content_management": false,
  "enterprise": false,
  "analytics": false,
  "ai_capabilities": false,
  "marketplace_integration": false
}
EOF
fi

# Create environment file
if [ ! -f "$CONFIG_DIR/env" ]; then
  echo "Creating environment file template..."
  cat > "$CONFIG_DIR/env" << EOF
# Atlassian API credentials
JIRA_URL=
JIRA_USERNAME=
JIRA_API_TOKEN=

CONFLUENCE_URL=
CONFLUENCE_USERNAME=
CONFLUENCE_API_TOKEN=

# Feature flags (uncomment and set to enable)
#ENABLE_ENHANCED_JIRA=true
#ENABLE_ENHANCED_CONFLUENCE=true
#ENABLE_JSM=true
#ENABLE_BITBUCKET=true
#ENABLE_ENTERPRISE=true

# Paths
FEATURE_FLAGS_CONFIG=$CONFIG_DIR/feature_flags.json

# Logging
MCP_ATLASSIAN_LOG_LEVEL=INFO
EOF
  echo -e "${YELLOW}Please edit $CONFIG_DIR/env to add your Atlassian credentials.${NC}"
fi

# Set permissions
echo "Setting permissions..."
chown -R "$USER:$GROUP" "$INSTALL_DIR"
chown -R "$USER:$GROUP" "$CONFIG_DIR"
chown -R "$USER:$GROUP" "$LOG_DIR"
chmod 750 "$CONFIG_DIR"
chmod 640 "$CONFIG_DIR/env"
chmod 640 "$CONFIG_DIR/feature_flags.json"

# Create virtual environment if it doesn't exist
if [ ! -d "$INSTALL_DIR/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$INSTALL_DIR/venv"
  
  echo "Installing dependencies..."
  "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
  "$INSTALL_DIR/venv/bin/pip" install -e "$INSTALL_DIR"
  "$INSTALL_DIR/venv/bin/pip" install mcp atlas-python-api pydantic python-dotenv
fi

# Create systemd service file
echo "Creating systemd service..."
cat > /tmp/mcp-atlassian.service << EOF
[Unit]
Description=$SERVICE_DESCRIPTION
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$CONFIG_DIR/env
ExecStart=$INSTALL_DIR/venv/bin/python -m src.mcp_atlassian.server
Restart=on-failure
RestartSec=5
StandardOutput=append:$LOG_DIR/mcp-atlassian.log
StandardError=append:$LOG_DIR/mcp-atlassian-error.log

[Install]
WantedBy=multi-user.target
EOF

# Install the service
if [ "$EUID" -eq 0 ]; then
  mv /tmp/mcp-atlassian.service /etc/systemd/system/
  systemctl daemon-reload
  echo -e "${GREEN}Service installed successfully!${NC}"
  echo "To enable and start the service, run:"
  echo "  sudo systemctl enable $SERVICE_NAME"
  echo "  sudo systemctl start $SERVICE_NAME"
else
  echo -e "${YELLOW}Cannot install systemd service without root privileges.${NC}"
  echo "To complete installation, run the following commands as root:"
  echo "  sudo mv /tmp/mcp-atlassian.service /etc/systemd/system/"
  echo "  sudo systemctl daemon-reload"
  echo "  sudo systemctl enable $SERVICE_NAME"
  echo "  sudo systemctl start $SERVICE_NAME"
fi

# Create systemd unit file for feature manager
cat > /tmp/mcp-feature-manager.service << EOF
[Unit]
Description=MCP Atlassian Feature Manager API
After=network.target mcp-atlassian.service

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$CONFIG_DIR/env
ExecStart=$INSTALL_DIR/venv/bin/python -m tools.feature_manager_api
Restart=on-failure
RestartSec=5
StandardOutput=append:$LOG_DIR/feature-manager.log
StandardError=append:$LOG_DIR/feature-manager-error.log

[Install]
WantedBy=multi-user.target
EOF

# Install the feature manager service
if [ "$EUID" -eq 0 ]; then
  mv /tmp/mcp-feature-manager.service /etc/systemd/system/
  systemctl daemon-reload
  echo -e "${GREEN}Feature manager service installed successfully!${NC}"
else
  echo -e "${YELLOW}Also install the feature manager service with:${NC}"
  echo "  sudo mv /tmp/mcp-feature-manager.service /etc/systemd/system/"
  echo "  sudo systemctl daemon-reload"
  echo "  sudo systemctl enable mcp-feature-manager"
  echo "  sudo systemctl start mcp-feature-manager"
fi

echo -e "\n${GREEN}Installation completed!${NC}"
echo -e "${YELLOW}Important:${NC} Edit $CONFIG_DIR/env to configure your Atlassian credentials before starting the service."
echo -e "Run diagnostics with: $INSTALL_DIR/venv/bin/python -m tools.feature_manager diagnostics"
echo ""

# Print summary
echo "Summary:"
echo "  Install directory: $INSTALL_DIR"
echo "  Config directory:  $CONFIG_DIR"
echo "  Log directory:     $LOG_DIR"
echo "  Service name:      $SERVICE_NAME"
echo ""