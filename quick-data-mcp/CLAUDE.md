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
# Run all tests (162 tests)
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
- **32 Analytics Tools**: Comprehensive data manipulation, analysis, and visualization functions
- **12 Dynamic Resources**: Real-time data context providers
- **8 Adaptive Prompts**: AI-guided conversation starters with business context
- **Dataset Manager**: Centralized dataset handling with `EnhancedDatasetManager`
- **Analytics Orchestrator**: Business context-aware workflow generation
- **Advanced Code Executor**: Safe Python execution with AI helper functions

### Design Patterns
1. **Manager Pattern**: `DatasetManager` and `EnhancedDatasetManager` for centralized dataset handling
2. **Orchestrator Pattern**: `AnalyticsOrchestrator` coordinates complex workflows with business context
3. **Executor Pattern**: `AdvancedCodeExecutor` provides safe Python code execution with monitoring
4. **Resource Mirror Pattern**: Every resource has a corresponding tool for MCP client compatibility

### Module Structure
```
quick-data-mcp/src/mcp_server/
├── server.py              # Main MCP server entry point (32 tools, 12 resources, 8 prompts)
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
- All tools follow async/await pattern

### Code Execution Context
- The `AdvancedCodeExecutor` provides a safe execution environment
- Import blocking is implemented for safety (blocks os, subprocess, etc.)
- Memory usage is monitored with 512MB limit
- AI helper functions available when `include_ai_context=True`

### Configuration
- Python 3.12+ required
- Main dependencies: `mcp[cli]>=1.9.2`, `pandas>=2.2.3`, `plotly>=6.1.2`, `pytest>=8.3.5`, `pytest-asyncio>=1.0.0`
- MCP configuration in `.mcp.json` (copy from `.mcp.json.sample`)
- Environment variables: `LOG_LEVEL`, `SERVER_NAME`

### Key Features
- Dataset-agnostic design works with any JSON/CSV structure
- +400-500% Intelligence Uplift through adaptive workflows
- 67% Efficiency Improvement by tracking analytics state
- Zero-error execution with comprehensive safety features
- Universal MCP client compatibility (resource-enabled and tool-only)

## Working with the Codebase

### Key Files
- `src/mcp_server/server.py` - Main server with tool, resource, and prompt definitions
- `src/mcp_server/tools/pandas_tools.py` - Core pandas-based analytics tools
- `src/mcp_server/managers/enhanced_dataset_manager.py` - Advanced dataset state management
- `src/mcp_server/advanced/advanced_code_executor.py` - Safe Python code execution with AI helpers
- `src/mcp_server/orchestration/analytics_orchestrator.py` - Business context-aware workflows
- `tests/conftest.py` - Shared test fixtures and setup

### Data Flow
1. Datasets loaded via `load_dataset` tool into `EnhancedDatasetManager`
2. Tools access datasets through manager for analysis
3. Resources provide real-time context about loaded data
4. Prompts guide users through analytics workflows with business context
5. Code executor enables custom Python analysis with safety controls and AI assistance

### Error Handling
- If you get any errors, stop and fix the problem before proceeding
- All tools return comprehensive error messages with actionable suggestions
- Code execution errors include safety analysis and debugging hints