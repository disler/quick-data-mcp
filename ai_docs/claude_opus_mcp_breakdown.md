# Building Python MCP Servers with modern syntax

The Model Context Protocol (MCP) has emerged as the open standard for enabling AI applications to connect with external tools and data sources. Since its open-source release by Anthropic in November 2024, the Python SDK has become the primary framework for building MCP servers with over 12,000 GitHub stars and active development.

## Official MCP Python SDK documentation and latest version

The official MCP Python SDK is maintained at **https://github.com/modelcontextprotocol/python-sdk** and provides comprehensive tools for building both servers and clients. The latest SDK supports protocol version **2025-03-26** with significant enhancements.

### Installation and requirements
```bash
# Recommended: Using uv (fast package manager)
uv add "mcp[cli]"

# Alternative: Using pip
pip install "mcp[cli]"
```

**Key requirements:**
- Python 3.7+ (3.10+ recommended for optimal performance)
- FastMCP is now integrated into the official SDK
- CLI tools included for development and testing
- Full async/await support throughout

### Official documentation landscape
- **Main documentation**: modelcontextprotocol.io
- **Protocol specification**: spec.modelcontextprotocol.io
- **GitHub organization**: github.com/modelcontextprotocol
- **Reference implementations**: Over 250 community servers across various domains

## Complete working examples implementing tools, resources, and prompts

### Basic MCP server with all three primitives

```python
#!/usr/bin/env python3
"""Complete MCP Server demonstrating tools, resources, and prompts"""

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base
from typing import List, Dict, Any
import asyncio
import httpx

# Create server instance
mcp = FastMCP("Demo Server", dependencies=["httpx", "pandas"])

# ============================================================================
# TOOLS - Functions that can be called by LLMs
# ============================================================================

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather information for a city."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.example.com/{city}")
        return f"Weather in {city}: {response.json()}"

@mcp.tool()
async def long_running_task(items: List[str], ctx: Context) -> str:
    """Process multiple items with progress reporting."""
    total = len(items)
    
    for i, item in enumerate(items):
        await ctx.info(f"Processing item: {item}")
        await ctx.report_progress(i + 1, total)
        await asyncio.sleep(0.5)
    
    return f"Successfully processed {total} items"

# ============================================================================
# RESOURCES - Data that can be accessed by LLMs
# ============================================================================

@mcp.resource("config://app-settings")
def get_app_config() -> dict:
    """Get application configuration settings."""
    return {
        "version": "1.0.0",
        "environment": "production",
        "features": ["auth", "logging", "monitoring"]
    }

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    """Get user profile information by ID."""
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "status": "active"
    }

# ============================================================================
# PROMPTS - Reusable conversation templates
# ============================================================================

@mcp.prompt()
def code_review_prompt(code: str) -> str:
    """Generate a prompt for code review."""
    return f"""Please review the following code for:
- Security vulnerabilities
- Performance issues
- Code quality and best practices

Code to review:
```
{code}
```

Provide specific feedback and suggestions for improvement."""

@mcp.prompt()
def debug_conversation(error_message: str) -> List[base.Message]:
    """Start a debugging conversation with context."""
    return [
        base.UserMessage(f"I'm encountering this error: {error_message}"),
        base.AssistantMessage("I'll help you debug this issue. Can you provide:"),
        base.AssistantMessage("1. The code that's causing the error"),
        base.AssistantMessage("2. The full stack trace")
    ]

if __name__ == "__main__":
    mcp.run()
```

### Advanced async patterns with database integration

```python
#!/usr/bin/env python3
"""Advanced MCP Server with async patterns and database integration"""

import sqlite3
import asyncio
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import List, Dict, Any

# Database lifecycle management
@asynccontextmanager
async def database_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Initialize database on startup."""
    conn = sqlite3.connect("app_database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
    yield {"database_path": "app_database.db"}

mcp = FastMCP("SQLite Server", lifespan=database_lifespan)

@mcp.tool()
def create_user(name: str, email: str) -> dict:
    """Create a new user in the database."""
    try:
        conn = sqlite3.connect("app_database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "user_id": user_id,
            "message": f"User {name} created successfully"
        }
    except sqlite3.IntegrityError:
        return {
            "status": "error",
            "message": f"User with email {email} already exists"
        }

@mcp.tool()
async def process_files_async(file_paths: List[str], ctx: Context) -> dict:
    """Process multiple files asynchronously with progress reporting."""
    async def process_file(file_path: str) -> dict:
        # Simulate async file processing
        await asyncio.sleep(0.1)
        return {"file": file_path, "processed": True}
    
    tasks = [process_file(fp) for fp in file_paths]
    results = []
    
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        results.append(result)
        await ctx.report_progress(i + 1, len(tasks))
    
    return {
        "total_files": len(file_paths),
        "results": results
    }

@mcp.resource("schema://tables")
def get_database_schema() -> dict:
    """Get the database schema information."""
    conn = sqlite3.connect("app_database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [
            {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "primary_key": bool(col[5])
            }
            for col in cursor.fetchall()
        ]
        schema[table] = columns
    
    conn.close()
    return schema
```

## Best practices for structuring MCP servers

### Recommended project structure
```
project_root/
├── src/
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py          # Main server instance
│   │   ├── tools/             # Tool implementations
│   │   │   ├── database_tools.py
│   │   │   └── api_tools.py
│   │   ├── resources/         # Resource handlers
│   │   │   └── data_resources.py
│   │   ├── prompts/           # Prompt templates
│   │   │   └── task_prompts.py
│   │   ├── models/            # Data models
│   │   │   └── schemas.py
│   │   └── config/            # Configuration
│   │       └── settings.py
├── tests/
├── requirements.txt
└── README.md
```

### Production-ready error handling pattern

```python
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, ValidationError
import logging

mcp = FastMCP("Production Server")

@mcp.tool()
async def resilient_operation(
    operation_type: str,
    retries: int = 3,
    ctx: Context
) -> dict:
    """Demonstrate resilient operations with retries and error handling."""
    for attempt in range(retries):
        try:
            await ctx.info(f"Attempt {attempt + 1} of {retries}")
            
            # Your operation logic here
            if attempt < retries - 1:
                # Simulate failure for demonstration
                raise Exception(f"Simulated failure on attempt {attempt + 1}")
            
            return {
                "status": "success",
                "operation": operation_type,
                "attempts": attempt + 1
            }
            
        except ValidationError as e:
            await ctx.error(f"Validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "details": str(e)
            }
        except Exception as e:
            await ctx.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == retries - 1:
                await ctx.error(f"All {retries} attempts failed")
                return {
                    "status": "failed",
                    "error": str(e)
                }
            
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Security best practices with input validation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class SecureInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    filters: Optional[dict] = {}
    limit: int = Field(100, ge=1, le=1000)
    
    @validator('query')
    def validate_query(cls, v):
        # Prevent SQL injection
        forbidden = ['DROP', 'DELETE', 'INSERT', 'UPDATE', '--', ';']
        if any(word in v.upper() for word in forbidden):
            raise ValueError("Query contains forbidden keywords")
        return v

@mcp.tool()
def secure_query(input_data: SecureInput) -> dict:
    """Tool with validated inputs."""
    # Input is automatically validated by Pydantic
    return execute_safe_query(input_data.query, input_data.filters)
```

## Claude Code integration examples

### Configuration for Claude Code

Claude Code uses a JSON configuration format similar to Claude Desktop:

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "python",
      "args": ["/path/to/your/server.py"],
      "env": {
        "API_KEY": "your-api-key",
        "DATABASE_URL": "your-database-url"
      }
    },
    "fastmcp-server": {
      "command": "fastmcp",
      "args": ["run", "/path/to/fastmcp_server.py"]
    }
  }
}
```

### Integration best practices
- **Direct config editing**: Developers prefer editing configuration files directly for better control
- **Environment variables**: Secure handling of API keys and secrets
- **Absolute paths**: Use absolute paths for reliability across environments
- **Auto-discovery**: Claude Code can auto-discover servers from Claude Desktop configurations
- **Status monitoring**: Use `/mcp` command to check server connection status

## Latest MCP syntax and patterns

### Modern type annotations with Python 3.8+

```python
from typing import Union, Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

@mcp.tool()
def create_task(task: TaskModel) -> dict:
    """Create a new task with full validation."""
    return {
        "status": "created",
        "task_id": f"task_{hash(task.title)}",
        "task": task.dict()
    }

# Union types for flexible parameters
@mcp.tool()
def process_data(
    data: Union[str, dict, List[dict]],
    output_format: Literal["json", "csv", "xml"] = "json"
) -> str:
    """Process data in multiple formats."""
    return f"Processed data in {output_format} format"
```

### Async context managers and lifecycle management

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with startup/shutdown logic."""
    # Startup
    print("Starting MCP server...")
    db_connection = await create_db_connection()
    cache = {}
    
    context = AppContext(db_connection=db_connection, cache=cache)
    
    try:
        yield context
    finally:
        # Cleanup
        print("Shutting down MCP server...")
        await db_connection.close()

mcp = FastMCP("Demo Server", lifespan=app_lifespan)
```

## Recent MCP protocol updates (2025)

### Protocol version 2025-03-26 introduces major features

**New capabilities:**
- **OAuth 2.1 authorization**: Comprehensive security framework for agent-server communication
- **Streamable HTTP transport**: Replaces HTTP+SSE for more efficient bidirectional communication
- **Tool annotations**: Rich metadata for describing tool behavior (read-only vs destructive)
- **Audio data support**: Extends content types beyond text and images
- **Enhanced progress notifications**: Descriptive status updates during long operations

**Breaking changes to consider:**
- Transport layer changes affect existing HTTP+SSE implementations
- OAuth 2.1 requires authentication flow updates for HTTP-based servers
- Community concerns about rapid changes without formal deprecation policy

### Migration recommendations
1. **Use stdio transport** for local development to avoid breaking changes
2. **Monitor specification changes** on GitHub for deprecation discussions
3. **Implement compatibility layers** for gradual migration
4. **Test extensively** across different MCP client implementations

## Production-ready MCP server examples

### Enterprise-grade server with comprehensive features

```python
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
import structlog
import os

# Production configuration
class ProductionConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.redis_url = os.getenv("REDIS_URL")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_connections = int(os.getenv("MAX_CONNECTIONS", "100"))

@asynccontextmanager
async def production_lifespan(server: FastMCP):
    """Production lifecycle management"""
    config = ProductionConfig()
    
    # Initialize connections
    db_pool = await create_db_pool(config.database_url)
    redis_client = await aioredis.from_url(config.redis_url)
    
    # Setup monitoring
    metrics_collector = MetricsCollector()
    
    try:
        yield {
            "db_pool": db_pool,
            "redis": redis_client,
            "metrics": metrics_collector,
            "config": config
        }
    finally:
        # Cleanup
        await db_pool.close()
        await redis_client.close()
        await metrics_collector.shutdown()

# Create production server
mcp = FastMCP(
    name="Production MCP Server",
    version="1.0.0",
    lifespan=production_lifespan,
    dependencies=["sqlalchemy", "aioredis", "structlog"]
)

# Health monitoring
@mcp.resource("health://status")
async def health_check() -> dict:
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check database connectivity
    try:
        await check_database_connection()
        health_status["dependencies"]["database"] = "healthy"
    except Exception:
        health_status["dependencies"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status
```

### Docker deployment configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Security: Create non-root user
RUN useradd --create-home --shell /bin/bash mcpuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "src.mcp_server.main"]
```

## Key implementation patterns and recommendations

### Essential patterns for production
1. **Use FastMCP** for rapid development with production-ready features
2. **Implement proper error handling** with retries and graceful failures
3. **Add comprehensive logging** using structured logging libraries
4. **Design for testability** with dependency injection patterns
5. **Optimize performance** through connection pooling and caching
6. **Secure all inputs** with Pydantic validation models
7. **Monitor health** with dedicated health check endpoints

### Development workflow
```bash
# Install and run the MCP Inspector
npx @modelcontextprotocol/inspector python your_server.py

# For FastMCP development
fastmcp dev your_server.py --with pandas --with numpy

# Testing in production
fastmcp install your_server.py
```

### Testing strategy example

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def mcp_server():
    server = FastMCP("Test Server")
    
    @server.tool()
    def test_tool(input_data: str) -> str:
        return f"Processed: {input_data}"
    
    return server

@pytest.mark.asyncio
async def test_tool_functionality(mcp_server):
    """Test MCP tool using in-memory client"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("test_tool", {"input_data": "hello"})
        assert result[0].text == "Processed: hello"
```

## Conclusion

Building Python MCP servers with modern syntax has become streamlined with the official SDK and FastMCP framework. The ecosystem provides comprehensive tools for creating production-ready servers that integrate seamlessly with Claude Code and other MCP clients. While recent protocol updates introduce powerful features like OAuth 2.1 and streamable HTTP transport, developers should carefully manage migration paths and monitor the rapidly evolving specification.