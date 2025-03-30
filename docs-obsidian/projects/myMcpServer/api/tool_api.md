---
created: 2025-03-30
tags: [api, documentation, tools, mcp-hub]
parent: [[../Project MOC]]
---

# Tool API Specification

## Overview

The Tool API defines the interface for implementing and interacting with MCP tools. This specification covers both Python and TypeScript tool implementations.

## Tool Implementation

### Base Tool Structure

#### Python Implementation

```python
from mcp_core.models import ToolRequest, ToolResponse

class BaseTool:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    async def handle_request(self, request: ToolRequest) -> ToolResponse:
        raise NotImplementedError()

    async def health_check(self) -> dict:
        return {"status": "healthy"}
```

#### TypeScript Implementation

```typescript
import { ToolRequest, ToolResponse } from '@mcp/core';

export abstract class BaseTool {
  constructor(
    protected name: string,
    protected version: string
  ) {}

  abstract handleRequest(request: ToolRequest): Promise<ToolResponse>;

  async healthCheck(): Promise<Record<string, any>> {
    return { status: 'healthy' };
  }
}
```

## Request/Response Format

### Tool Request

```json
{
  "type": "tool_request",
  "id": "unique-request-id",
  "tool": "tool-name",
  "method": "method-name",
  "params": {
    // Tool-specific parameters
  }
}
```

### Tool Response

```json
{
  "type": "tool_response",
  "id": "unique-request-id",
  "result": {
    // Tool-specific result data
  },
  "error": null // or error object if failed
}
```

## Tool Registration

### Registration Process

1. Tool implements required interfaces
2. Tool provides capabilities description
3. Tool server registers tool with MCP system
4. MCP validates and activates tool

### Capabilities Declaration

```json
{
  "tool": {
    "name": "example-tool",
    "version": "1.0.0",
    "capabilities": {
      "methods": [
        {
          "name": "method1",
          "description": "Method description",
          "params": {
            "type": "object",
            "properties": {
              "param1": {
                "type": "string",
                "description": "Parameter description"
              }
            }
          }
        }
      ],
      "resources": [
        {
          "name": "resource1",
          "type": "string",
          "description": "Resource description"
        }
      ]
    }
  }
}
```

## Implementation Examples

### Python Tool Example

```python
from mcp_core.models import ToolRequest, ToolResponse
from mcp_core.errors import ToolError

class ExampleTool(BaseTool):
    def __init__(self):
        super().__init__("example-tool", "1.0.0")

    async def handle_request(self, request: ToolRequest) -> ToolResponse:
        try:
            if request.method == "method1":
                result = await self._handle_method1(request.params)
                return ToolResponse(result=result)
            raise ToolError("Unknown method")
        except Exception as e:
            raise ToolError(str(e))

    async def _handle_method1(self, params: dict) -> dict:
        # Implementation
        return {"status": "success"}
```

### TypeScript Tool Example

```typescript
import { ToolRequest, ToolResponse, ToolError } from '@mcp/core';

export class ExampleTool extends BaseTool {
  constructor() {
    super('example-tool', '1.0.0');
  }

  async handleRequest(request: ToolRequest): Promise<ToolResponse> {
    try {
      if (request.method === 'method1') {
        const result = await this.handleMethod1(request.params);
        return { result };
      }
      throw new ToolError('Unknown method');
    } catch (error) {
      throw new ToolError(error.message);
    }
  }

  private async handleMethod1(params: Record<string, any>): Promise<Record<string, any>> {
    // Implementation
    return { status: 'success' };
  }
}
```

## Error Handling

### Tool Error Format

```json
{
  "type": "tool_error",
  "code": "error-code",
  "message": "Error description",
  "details": {
    "tool": "tool-name",
    "method": "method-name",
    // Additional error context
  }
}
```

### Common Tool Error Codes

- `TOOL_NOT_FOUND`: Tool not registered
- `METHOD_NOT_FOUND`: Unknown tool method
- `INVALID_PARAMS`: Invalid method parameters
- `TOOL_ERROR`: Tool-specific error
- `INTERNAL_ERROR`: Tool server error

## Related Documentation

### Implementation

- [[../implementation/Server Configuration|Tool Server Configuration]]
- [[../mcpPlanning/final/core/technical-v2|Core Technical Details]]

### SDK Documentation

- [[../../../mcpKnowledge/pythonSDK/Python SDK Overview|Python SDK Guide]]
- [[../../../mcpKnowledge/typeScriptSDK/Implementation Examples|TypeScript Examples]]

### Architecture

- [[../architecture/Component Design|Tool Component Design]]
- [[../architecture/System Overview|System Architecture]]

---

[[../Project MOC|← Back to Project MOC]]
