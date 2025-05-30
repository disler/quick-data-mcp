# UV Running Python Scripts

Based on the official UV documentation for script execution, here's how `uv run python` works and why it's recommended for MCP servers.

## Key Benefits of `uv run python`

### Automatic Environment Management
- **No manual activation**: UV automatically creates and manages virtual environments
- **Dependency isolation**: Each script runs in its own isolated environment
- **Cross-platform**: Works consistently across macOS, Linux, and Windows

### Declarative Dependencies
Scripts can declare their dependencies inline using script metadata:

```python
# /// script
# dependencies = ["mcp[cli]>=1.9.2", "pydantic>=2.0.0"]
# ///

import mcp
# Script content here...
```

### Flexible Execution Options

```bash
# Basic script execution
uv run python script.py

# Add dependencies on-the-fly
uv run --with mcp[cli] python script.py

# Specify Python version
uv run --python 3.12 python script.py

# Use alternative package indexes
uv run --index-url https://custom.pypi.org/simple/ python script.py
```

## Why Use `uv run python` for MCP Servers?

### 1. **Dependency Isolation**
Each MCP server runs with its exact dependencies without conflicts:

```bash
# Each server gets its own environment
uv run python /path/to/server1/main.py  # Uses server1's dependencies
uv run python /path/to/server2/main.py  # Uses server2's dependencies
```

### 2. **Reproducible Environments**
UV ensures consistent dependency versions across different machines:

```bash
# With pyproject.toml, dependencies are locked
uv run python main.py  # Always uses same versions
```

### 3. **No Pre-activation Required**
Unlike traditional virtual environments, no need to activate:

```bash
# Traditional approach (error-prone)
source .venv/bin/activate
python main.py

# UV approach (automatic)
uv run python main.py
```

### 4. **Better Error Handling**
UV provides clear error messages when dependencies are missing or incompatible.

## MCP Configuration Best Practices

### For Local Development
```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/main.py"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### For Production Deployment
```json
{
  "mcpServers": {
    "production-server": {
      "command": "uv",
      "args": ["run", "--python", "3.12", "python", "/path/to/main.py"],
      "env": {
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/path/to/server"
      }
    }
  }
}
```

## Script Metadata Support

UV supports PEP 723 script metadata for dependency declaration:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.9.2",
#     "pydantic>=2.0.0",
#     "httpx>=0.25.0"
# ]
# ///

"""MCP Server with inline dependencies."""

from mcp.server import FastMCP
# Rest of server implementation...
```

## Performance Considerations

### Environment Caching
UV caches environments for faster subsequent runs:

```bash
# First run: Creates environment
uv run python main.py  # ~2-3 seconds

# Subsequent runs: Uses cached environment  
uv run python main.py  # ~0.1 seconds
```

### Lock Files
Use `uv.lock` for reproducible builds:

```bash
# Generate lock file
uv lock

# Run with exact locked versions
uv run python main.py
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure UV has write access to cache directory
2. **Path Issues**: Always use absolute paths in MCP configurations
3. **Python Version**: Specify Python version if system default differs

### Debug Commands

```bash
# Check UV environment
uv run python -c "import sys; print(sys.executable)"

# List installed packages
uv run python -m pip list

# Verbose execution
uv run --verbose python main.py
```

## Inline Dependencies with `--with` Flag

UV's `--with` flag allows you to add dependencies on-the-fly without modifying project files. This is particularly useful for one-off scripts, debugging, and quick prototyping.

### Basic Usage

```bash
# Run a script with additional dependencies
uv run --with requests python -c "import requests; print(requests.__version__)"

# Multiple dependencies
uv run --with "pandas>=2.0.0" --with "plotly>=5.0.0" python -c "
import pandas as pd
import plotly.express as px
df = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})
print('Data loaded successfully!')
"
```

### Data Analysis Examples

```bash
# Quick data analysis without a dedicated project
uv run --with pandas --with matplotlib python -c "
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=30),
    'sales': np.random.randint(100, 1000, 30)
})

# Quick analysis
print('Sales Summary:')
print(data['sales'].describe())
print(f'Total Sales: ${data[\"sales\"].sum():,}')
"

# Web scraping with requests and beautifulsoup
uv run --with requests --with beautifulsoup4 python -c "
import requests
from bs4 import BeautifulSoup

response = requests.get('https://httpbin.org/json')
print(f'Status: {response.status_code}')
print(f'Data: {response.json()}')
"
```

### MCP Server Prototyping

```bash
# Prototype an MCP server with specific versions
uv run --with "mcp[cli]>=1.9.2" --with "pydantic>=2.11.0" python -c "
from mcp.server import FastMCP
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    value: int

mcp = FastMCP('test-server')

@mcp.tool()
async def test_tool(name: str, value: int) -> dict:
    model = TestModel(name=name, value=value)
    return {'message': f'Created {model.name} with value {model.value}'}

print('MCP server prototype created successfully!')
print(f'Server name: {mcp.name}')
"

# Test database connections
uv run --with psycopg2-binary --with sqlalchemy python -c "
import sqlalchemy
from sqlalchemy import create_engine, text

print(f'SQLAlchemy version: {sqlalchemy.__version__}')
print('Database drivers available')
"
```

### Development Workflow Examples

```bash
# Test package compatibility
uv run --with "fastapi>=0.104.0" --with "uvicorn>=0.24.0" python -c "
import fastapi
import uvicorn
print(f'FastAPI: {fastapi.__version__}')
print(f'Uvicorn: {uvicorn.__version__}')
print('Compatibility check passed!')
"

# Data format conversion
uv run --with "openpyxl>=3.1.0" --with "pandas>=2.2.0" python -c "
import pandas as pd
import json

# Simulate reading Excel and converting to JSON
data = {'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']}
df = pd.DataFrame(data)

json_output = df.to_json(orient='records', indent=2)
print('Excel to JSON conversion:')
print(json_output)
"

# API testing
uv run --with httpx --with pydantic python -c "
import httpx
import asyncio
from pydantic import BaseModel

class ApiResponse(BaseModel):
    status: str
    data: dict

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://httpbin.org/json')
        print(f'Status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        return response.json()

result = asyncio.run(test_api())
print(f'API test result: {result}')
"
```

### Machine Learning Prototyping

```bash
# Quick ML experiment
uv run --with scikit-learn --with numpy python -c "
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f'Model Accuracy: {accuracy:.3f}')
print(f'Feature Importance (top 5):')
for i, importance in enumerate(model.feature_importances_[:5]):
    print(f'  Feature {i}: {importance:.3f}')
"
```

### Advanced Usage Patterns

```bash
# Combine with version constraints
uv run --with "numpy>=1.24.0,<2.0.0" --with "scipy>=1.11.0" python -c "
import numpy as np
import scipy as sp
print(f'NumPy: {np.__version__} (meets constraint)')
print(f'SciPy: {sp.__version__} (compatible)')
"

# Use pre-release versions for testing
uv run --with "django>=5.0.0rc1" --with "channels>=4.0.0" python -c "
import django
print(f'Testing with Django pre-release: {django.__version__}')
"

# Development dependencies for testing
uv run --with pytest --with pytest-asyncio --with hypothesis python -c "
import pytest
import hypothesis
print('Testing framework ready!')
print(f'Pytest: {pytest.__version__}')
print(f'Hypothesis: {hypothesis.__version__}')
"
```

### Benefits of `--with` Flag

- ✅ **No project modification**: Test dependencies without changing `pyproject.toml`
- ✅ **Rapid prototyping**: Quickly test ideas with different package combinations
- ✅ **Debugging**: Add debugging tools without permanent installation
- ✅ **CI/CD testing**: Test different dependency versions in pipelines
- ✅ **Documentation examples**: Run examples without environment setup

### When to Use `--with` vs Project Dependencies

| Use `--with` for: | Use project dependencies for: |
|-------------------|-------------------------------|
| One-off scripts | Production applications |
| Quick prototypes | Long-term projects |
| Testing compatibility | Reproducible builds |
| Debug sessions | Team collaboration |
| Documentation examples | Deployment scenarios |

## Comparison with Traditional Approaches

| Method | Pros | Cons |
|--------|------|------|
| `python main.py` | Simple | No isolation, manual env management |
| `source .venv/bin/activate && python main.py` | Explicit control | Manual activation, platform-specific |
| `uv run python main.py` | Automatic isolation, cross-platform | Requires UV installation |

## Conclusion

Using `uv run python` for MCP servers provides:
- ✅ **Automatic dependency management**
- ✅ **Environment isolation**
- ✅ **Cross-platform compatibility**
- ✅ **Reproducible deployments**
- ✅ **No manual environment activation**

This makes it the recommended approach for running MCP servers in both development and production environments.