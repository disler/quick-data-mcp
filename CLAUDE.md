# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python MCP (Model Context Protocol) Server that provides data analytics capabilities for structured datasets (JSON/CSV). The server offers tools for data loading, analysis, visualization, and AI-guided workflows with a modular, dataset-agnostic architecture.

## Development Commands

### Running the Server
```bash
cd quick-data-mcp/
uv run python main.py
```

### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test modules
uv run python -m pytest tests/test_pandas_tools.py -v
uv run python -m pytest tests/test_analytics_tools.py -v
uv run python -m pytest tests/integration/ -v

# Run a single test
uv run python -m pytest tests/test_pandas_tools.py::test_function_name -v

# Run tests matching a pattern
uv run python -m pytest -k "test_pattern" -v

# Quick test run
uv run python -m pytest tests/ -q
```

### Building/Installing
```bash
# Project uses uv for dependency management
uv sync
```

## Architecture

### Core Components
- **Tools**: Data manipulation, analysis, and visualization functions
- **Resources**: Dynamic data resources providing real-time context
- **Prompts**: AI-guided conversation starters for analytics workflows
- **Dataset Manager**: Centralized dataset handling and state management
- **Code Executor**: Python code execution with safety features

### Design Patterns
1. **Manager Pattern**: `DatasetManager` and `EnhancedDatasetManager` for centralized dataset handling
2. **Orchestrator Pattern**: `AnalyticsOrchestrator` coordinates complex workflows  
3. **Executor Pattern**: `AdvancedCodeExecutor` provides safe Python code execution
4. **Resource Mirror Pattern**: Resources have corresponding tools for MCP client compatibility

### Module Structure
```
quick-data-mcp/src/mcp_server/
├── server.py              # Main MCP server entry point
├── tools/                 # Analytics tools implementation
├── resources/             # Dynamic data resources
├── prompts/               # Conversation prompt templates
├── models/                # Data models and schemas
├── managers/              # Dataset management logic
├── orchestration/         # Workflow coordination
├── advanced/              # Advanced analytics features
└── config/                # Configuration settings
```

### Testing Architecture
- Tests located in `quick-data-mcp/tests/`
- Integration tests in `tests/integration/`
- Component-specific test modules for tools, resources, and prompts
- Async test support with `pytest-asyncio`
- Shared fixtures in `tests/conftest.py`

## Important Notes

### MCP Tools Usage
- Always use MCP tools instead of direct API methods
- Use `get_stock_bars_intraday` for multiple stock symbols (more efficient than individual calls)

### Code Execution Context
- The `AdvancedCodeExecutor` provides a safe execution environment
- Import blocking is implemented for safety
- Memory usage is monitored

### Configuration
- Python 3.12+ required
- Main dependencies: `mcp[cli]`, `pandas`, `plotly`, `pytest`, `pytest-asyncio`
- MCP configuration in `.mcp.json` (copy from `.mcp.json.sample`)
- Environment variables: `LOG_LEVEL`, `SERVER_NAME`

### Key Features
- Dataset-agnostic design works with any JSON/CSV structure
- Comprehensive test coverage with integration tests
- Modular architecture with clean separation of concerns
- Safe Python code execution with security features
- Real-time data resources and AI-guided prompts

## Working with the Codebase

### Key Files
- `src/mcp_server/server.py` - Main server with tool, resource, and prompt definitions
- `src/mcp_server/tools/pandas_tools.py` - Core pandas-based analytics tools
- `src/mcp_server/managers/enhanced_dataset_manager.py` - Dataset state management
- `src/mcp_server/advanced/advanced_code_executor.py` - Safe Python code execution
- `tests/conftest.py` - Shared test fixtures and setup

### Data Flow
1. Datasets loaded via `load_dataset` tool into `DatasetManager`
2. Tools access datasets through manager for analysis
3. Resources provide real-time context about loaded data
4. Prompts guide users through analytics workflows
5. Code executor enables custom Python analysis with safety controls