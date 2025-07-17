# Redis Key Naming Convention

## Overview

This document outlines the naming conventions for Redis keys in the Nova system. The system uses different naming patterns for different types of data, all under the "nova:" namespace.

## 1. Communication Streams

### Pattern
```
nova:domain:category:name
```

### Components
- **nova**: Network namespace
- **domain**: System domain (e.g., devops, system, comms)
- **category**: Subsystem or group (e.g., general, team, direct)
- **name**: Specific identifier

### Examples
```
nova:devops:general          # General DevOps communication
nova:devops:team:mcp        # MCP team channel
nova:devops:direct:cline    # Direct channel for Cline
nova:broadcast:all          # Network-wide broadcasts
```

### Usage
- Real-time communication channels
- Message broadcasting
- Team collaboration
- Direct messaging

## 2. Shell/System Keys

### Pattern
```
nova:shell:{id}:{attribute}
```

### Components
- **nova**: Network namespace
- **shell**: System component identifier
- **id**: Numeric instance identifier
- **attribute**: Data type/property name

### Examples
```
nova:shell:107:activated_at  # Shell #107 activation timestamp
nova:shell:189:status       # Shell #189 current status
nova:shell:162:activated_at # Shell #162 activation timestamp
```

### Usage
- Track shell instance states
- Monitor system components
- Store instance metadata
- Track activation times

## 3. Status Keys

### Pattern
```
nova:{id}:status
```

### Components
- **nova**: Network namespace
- **id**: Numeric instance identifier
- **status**: Status indicator

### Examples
```
nova:092:status  # Status of Nova instance #092
nova:178:status  # Status of Nova instance #178
```

### Usage
- Track Nova instance states
- Monitor system health
- Store operational status

## 4. Task Keys

### Pattern
```
nova:{id}:task
```

### Components
- **nova**: Network namespace
- **id**: Numeric instance identifier
- **task**: Task indicator

### Examples
```
nova:001:task  # Task for Nova instance #001
nova:181:task  # Task for Nova instance #181
```

### Usage
- Track instance tasks
- Store task definitions
- Monitor task progress

## Guidelines

1. **Namespace**
   - All keys must start with "nova:" to maintain system isolation
   - This prevents conflicts with other systems using the same Redis instance

2. **Separators**
   - Use colon (:) as the standard separator
   - No spaces or special characters in key components
   - Use underscore (_) or hyphen (-) within component names if needed

3. **Case Sensitivity**
   - Use lowercase for all components
   - Use snake_case for multi-word attributes
   - Use kebab-case for multi-word names in streams

4. **Identifiers**
   - Use numeric IDs for system components
   - Use descriptive names for streams
   - Keep identifiers concise but meaningful

## Stream Name Validation

The system enforces the following regex pattern for stream names:
```
^nova:[a-z]+:[a-z]+:[a-z0-9_-]+$
```

This ensures:
- Proper namespace (nova:)
- Lowercase domain and category
- Alphanumeric names with optional underscores/hyphens
- Correct number of components

## Migration Notes

1. Legacy keys (shell/system/status) will maintain their current format
2. All new communication streams must follow the nova:domain:category:name format
3. No new keys should be created using legacy formats without explicit approval

## Examples of Valid Stream Names

```
nova:devops:general:announcements
nova:system:metrics:performance
nova:comms:team:alpha
nova:broadcast:alerts:critical
```

## Examples of Invalid Stream Names

```
nova.devops.general         # Wrong separator
nova:DevOps:General        # Wrong case
nova:devops:team:alpha:beta # Too many components
devops:team:alpha          # Missing namespace
```

For questions about naming conventions or to request new patterns, contact the DevOps team.
