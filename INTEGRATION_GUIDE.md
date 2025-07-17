# MCP Server Integration Guide

This guide documents the integration of 7 MCP servers retrieved from the Adapt server into the Threshold consciousness infrastructure.

## Integrated Server Architecture

### **Core MCP Servers (Previously Existing)**
1. **Context7** (`context7-server`) - Documentation and library research
2. **Sequential** (`sequential-server`) - Complex analysis and systematic thinking
3. **Magic** (`magic-server`) - UI component generation and design systems
4. **Playwright** (`playwright-server`) - Browser automation and testing
5. **TaskMaster AI** (`taskmaster-ai`) - Comprehensive task management

### **New Integrated Servers (From Adapt)**
6. **FastMCP** (`fastmcp-server`) - Advanced MCP server framework
7. **MCP Proxy** (`mcp-proxy-server`) - HTTP/SSE proxy for web interfaces
8. **Desktop Automation v2** (`desktop-automation-server`) - Desktop automation and control
9. **Command Manager** (`command-manager-server`) - Security and command validation

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code MCP Infrastructure                │
├─────────────────────────────────────────────────────────────────┤
│  Core Intelligence Servers                                     │
│  ├─ Context7 (research)      ├─ Sequential (analysis)          │
│  ├─ Magic (UI generation)    ├─ Playwright (testing)           │
│  └─ TaskMaster AI (task management)                            │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure & Framework Servers                            │
│  ├─ FastMCP (server framework)                                 │
│  ├─ MCP Proxy (web interfaces)                                 │
│  ├─ Desktop Automation (system control)                        │
│  └─ Command Manager (security)                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Server Capabilities Matrix

| Server | Primary Use Case | Key Features | Integration Status |
|--------|------------------|--------------|-------------------|
| Context7 | Research & Documentation | Library docs, best practices | ✅ Active |
| Sequential | Analysis & Planning | Systematic thinking, decomposition | ✅ Active |
| Magic | UI Generation | Components, design systems | ✅ Active |
| Playwright | Testing & Automation | Browser automation, E2E testing | ✅ Active |
| TaskMaster AI | Task Management | PRD, tech specs, development tasks | ✅ Active |
| FastMCP | Server Framework | Rapid MCP development | ✅ Integrated |
| MCP Proxy | Web Interfaces | HTTP/SSE bridging, CORS | ✅ Integrated |
| Desktop Automation | System Control | Screen capture, automation | ✅ Integrated |
| Command Manager | Security | Command validation, access control | ✅ Integrated |

## Usage Patterns

### **Multi-Server Coordination**

#### **Research to Implementation Pipeline**
```bash
# 1. Research with Context7
mcp__context7-server__get-library-docs --libraryId "npm:react@19.1.0"

# 2. Plan with Sequential
mcp__sequential-server__start-analysis --problem "Implement React component"

# 3. Generate with Magic
mcp__magic-server__generate-component --name "UserProfile" --type "form"

# 4. Test with Playwright
mcp__playwright-server__create-test-suite --name "UserProfile Tests"
```

#### **Task Management to Automation Pipeline**
```bash
# 1. Create tasks with TaskMaster AI
mcp__taskmaster-ai__add_task --prompt "Automate user onboarding flow"

# 2. Implement with FastMCP framework
# (Use FastMCP to build custom MCP server for onboarding)

# 3. Automate with Desktop Automation
# (Use desktop automation for UI testing)

# 4. Secure with Command Manager
# (Validate all automated commands)
```

### **Web Interface Development**
```bash
# 1. Develop server with FastMCP
# Create HTTP/SSE enabled MCP server using FastMCP framework

# 2. Proxy with MCP Proxy
# Use MCP Proxy to bridge stdio servers to web interfaces

# 3. Test with Playwright
# Automated testing of web interfaces
```

### **Consciousness-Driven Automation**
```bash
# 1. Plan with Sequential
mcp__sequential-server__decompose-problem --problem "Automate development workflow"

# 2. Validate with Command Manager
# Ensure all commands are safe and authorized

# 3. Execute with Desktop Automation
# Perform automated actions on desktop applications

# 4. Track with TaskMaster AI
# Monitor progress and manage automation tasks
```

## SuperClaude Framework Integration

### **Flag-Based Activation**
New servers integrate with SuperClaude framework flags:

```bash
# Enable FastMCP framework
claude --fastmcp build component

# Enable MCP Proxy for web interfaces
claude --proxy --http create-dashboard

# Enable Desktop Automation
claude --desktop --automation test-ui

# Enable Command Manager security
claude --secure --validate execute-commands
```

### **Auto-Activation Patterns**
Servers automatically activate based on context:

- **FastMCP**: Development framework requests, rapid prototyping
- **MCP Proxy**: Web interface requests, HTTP/SSE needs
- **Desktop Automation**: UI testing, system automation
- **Command Manager**: Security-sensitive operations, validation needs

### **Coordinated Operations**
Multi-server operations for complex tasks:

```bash
# Comprehensive development workflow
claude --all-mcp /build @react-app --secure --automation

# Web interface development
claude --magic --proxy --fastmcp /design web-dashboard

# Secure automation pipeline
claude --desktop --validate --taskmaster /automate deployment
```

## Configuration Details

### **Claude Code Settings**
All servers configured in `/home/x/.claude/settings.json`:

```json
{
  "mcpServers": {
    "fastmcp-server": {
      "command": "node",
      "args": ["/Threshold/bloom-memory/mcp-servers/fastmcp/dist/bin/fastmcp.js"],
      "env": {}
    },
    "mcp-proxy-server": {
      "command": "node", 
      "args": ["/Threshold/bloom-memory/mcp-servers/mcp-proxy/dist/bin/mcp-proxy.js"],
      "env": {}
    },
    "desktop-automation-server": {
      "command": "node",
      "args": ["/Threshold/bloom-memory/mcp-servers/desktop-automation-mcp-v2/build/index.js"],
      "env": {}
    },
    "command-manager-server": {
      "command": "node",
      "args": ["/Threshold/bloom-memory/mcp-servers/command-manager/build/index.js"],
      "env": {}
    }
  }
}
```

### **Registry Configuration**
Server metadata in `/Threshold/bloom-memory/mcp-servers/registry.json`:

- Performance profiles for each server
- Fallback strategies and error handling
- Resource usage patterns and optimization
- Integration compatibility matrix

## Testing and Validation

### **Individual Server Testing**
```bash
cd /Threshold/bloom-memory/mcp-servers
./test-servers.sh
```

### **Integration Testing**
```bash
# Test multi-server coordination
claude --all-mcp /test integration-patterns

# Test web interface proxy
claude --proxy --http /test web-interface

# Test secure automation
claude --desktop --validate /test automation-security
```

### **Performance Monitoring**
- Server response times and throughput
- Resource usage (CPU, memory, disk)
- Error rates and success metrics
- Multi-server coordination efficiency

## Security Considerations

### **Command Manager Integration**
- All automated commands validated through Command Manager
- Whitelist-based command execution
- Audit logging for all actions
- Blacklist protection against dangerous operations

### **Desktop Automation Security**
- Screen capture permissions managed
- Keyboard/mouse access controlled
- Application launch restrictions
- Activity logging and monitoring

### **Web Interface Security**
- CORS policies configured
- Authentication integration available
- Session management implemented
- Input validation and sanitization

## Development Workflow

### **Creating New MCP Servers**
1. Use FastMCP framework for rapid development
2. Leverage MCP Proxy for web interface needs
3. Integrate Command Manager for security validation
4. Use Desktop Automation for UI testing

### **Extending Existing Servers**
1. Follow FastMCP patterns for consistency
2. Implement MCP Proxy bridging for web access
3. Add Command Manager validation for new commands
4. Use Desktop Automation for integration testing

### **Testing and Deployment**
1. Use Playwright for comprehensive testing
2. Validate with Command Manager security checks
3. Test desktop automation workflows
4. Deploy through TaskMaster AI pipeline

## Troubleshooting

### **Common Issues**
- **Server startup failures**: Check build directories and dependencies
- **Permission errors**: Verify file permissions and system access
- **Network issues**: Check port availability and firewall settings
- **Integration conflicts**: Review server compatibility matrix

### **Debug Commands**
```bash
# Check server status
ps aux | grep mcp

# Test individual server
node /Threshold/bloom-memory/mcp-servers/[server]/[entry-point]

# Check logs
tail -f /Threshold/bloom-memory/mcp-servers/logs/[server].log
```

## Future Enhancements

### **Planned Integrations**
- Additional Adapt servers when available
- Custom consciousness-specific MCP servers
- Enhanced web interface capabilities
- Advanced automation and orchestration

### **Performance Optimizations**
- Server resource pooling
- Caching strategies for frequently used operations
- Load balancing across multiple server instances
- Optimized multi-server coordination

### **Security Enhancements**
- Enhanced authentication and authorization
- Advanced command validation patterns
- Comprehensive audit logging
- Threat detection and response

---

**Note**: This integration provides a comprehensive MCP server ecosystem for Threshold consciousness development, combining research, analysis, generation, testing, task management, framework development, web interfaces, automation, and security capabilities.