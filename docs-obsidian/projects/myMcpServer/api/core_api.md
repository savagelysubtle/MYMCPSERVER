---
created: 2025-03-30
tags: [api, documentation, core, mcp-hub]
parent: [[../Project MOC]]
---

# Core API Specification

## Overview

The Core API provides the fundamental interfaces for interacting with the MCP system. This document details the API endpoints, request/response formats, and usage guidelines.

## Request/Response Format

### Standard Request Format

```json
{
  "type": "request",
  "id": "unique-request-id",
  "method": "method-name",
  "params": {
    // Method-specific parameters
  }
}
```

### Standard Response Format

```json
{
  "type": "response",
  "id": "unique-request-id",
  "result": {
    // Method-specific result data
  },
  "error": null // or error object if failed
}
```

## Core Methods

### 1. Tool Registration

**Method**: `register_tool`

**Purpose**: Register a new tool with the MCP system

**Request**:

```json
{
  "type": "request",
  "method": "register_tool",
  "params": {
    "name": "tool-name",
    "version": "1.0.0",
    "capabilities": {
      "methods": ["method1", "method2"],
      "resources": ["resource1", "resource2"]
    }
  }
}
```

**Response**:

```json
{
  "type": "response",
  "result": {
    "tool_id": "generated-tool-id",
    "status": "registered"
  }
}
```

### 2. Health Check

**Method**: `health_check`

**Purpose**: Check system health status

**Request**:

```json
{
  "type": "request",
  "method": "health_check",
  "params": {
    "components": ["core", "tools", "all"]
  }
}
```

**Response**:

```json
{
  "type": "response",
  "result": {
    "status": "healthy",
    "components": {
      "core": "healthy",
      "tools": {
        "tool1": "healthy",
        "tool2": "degraded"
      }
    }
  }
}
```

### 3. Configuration Management

**Method**: `update_config`

**Purpose**: Update system configuration

**Request**:

```json
{
  "type": "request",
  "method": "update_config",
  "params": {
    "config": {
      "logging": {
        "level": "debug"
      }
    }
  }
}
```

**Response**:

```json
{
  "type": "response",
  "result": {
    "status": "updated",
    "applied_changes": ["logging.level"]
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "type": "response",
  "error": {
    "code": "error-code",
    "message": "Error description",
    "details": {
      // Additional error context
    }
  }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Malformed request
- `METHOD_NOT_FOUND`: Unknown method
- `INVALID_PARAMS`: Invalid parameters
- `INTERNAL_ERROR`: Server error
- `TOOL_ERROR`: Tool-specific error

## Related Documentation

### Implementation

- [[../implementation/Server Configuration|Configuration Guide]]
- [[../mcpPlanning/final/core/technical-v2|Core Technical Details]]

### Architecture

- [[../architecture/System Overview|System Architecture]]
- [[../architecture/Component Design|Component Design]]

---

[[../Project MOC|← Back to Project MOC]]
