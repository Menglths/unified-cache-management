# Pytest
[简体中文](README_zh.md)
A comprehensive Pytest testing framework featuring configuration management, database integration, performance testing, and HTML report generation.

## 📋 Features

- **Modern Testing Framework**: Complete test solution built on Pytest 7.0+
- **Configuration Management**: YAML-based config with thread-safe singleton pattern
- **Database Integration**: Built-in MySQL support with automatic result storage
- **HTML Reports**: Auto-generated pytest HTML test reports
- **Tagging System**: Multi-dimensional test tags (stage, feature, platform, etc.)

## 🗂️ Project Structure

```
pytest_demo/
├── common/                          # Common modules
│   ├── __init__.py
│   ├── config_utils.py              # Configuration utilities
│   ├── db_utils.py                  # Database utilities
│   └── capture_utils                # Return-value capture utilities
├── results/                         # Result storage folder
├── suites/                          # Test suites
│   ├── UnitTest                     # Unit tests
│   ├── Feature                      # Feature tests
│   └── E2E/                         # End-to-end tests
│       └── test_demo_performance.py # Sample test file
├── config.yaml                      # Main config file
├── conftest.py                      # Pytest config
├── pytest.ini                       # Pytest settings
├── requirements.txt                 # Dependencies
└── README.md                        # This doc (CN)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL 5.7+ (optional, for DB features)
- Git

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database** (optional)

   Edit `config.yaml`:
   ```yaml
    database:
      backup: "results/"
      host: "127.0.0.1"
      port: 3306
      name: "ucm_pytest"
      user: "root"
      password: "123456"
      charset: "utf8mb4"
   ```

3. **Run tests**
   ```bash
   # Run all tests
   pytest

   # Run tests by tag
   pytest --stage=1
   pytest --feature=performance
   ```

## ⚙️ Configuration

### config.yaml

Full YAML-based config. Key sections:

- **reports**: Report settings (HTML, timestamp, etc.)
- **database**: MySQL connection details

## 🧪 Test Examples

### Basic functional test

```python
# suites/E2E/test_demo_performance.py
import pytest

@pytest.fixture(scope="module", name="calc")
def calculator():
    return Calculator()

@pytest.mark.feature("mark")
class TestCalculator:
    def test_add(self, calc):
        assert calc.add(1, 2) == 3

    def test_divide_by_zero(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.divide(6, 0)
```

## 🏷️ Tagging System

Multi-dimensional tags supported:

### Stage tags
- `stage(0)`: Unit tests
- `stage(1)`: Smoke tests
- `stage(2)`: Regression tests
- `stage(3)`: Release tests

### Functional tags
- `feature`: Module tag
- `platform`: Platform tag (GPU/NPU)

### Usage

```bash
# Run smoke tests and above
pytest --stage=1+

# Run by feature
pytest --feature=performance
pytest --feature=performance,reliability

# Run by platform
pytest --platform=gpu
```

### HTML Reports

Auto-generated timestamped HTML reports:
- Location: `reports/pytest_YYYYMMDD_HHMMSS/report.html`
- Detailed results, errors, timing
- Customizable title & style

### Database Storage

If enabled, results are auto-saved to MySQL.  
To add new record types, ask DB admin to create tables; otherwise only local files are used.

Example:
```python
@pytest.mark.feature("capture")  # Must be top decorator
@export_vars
def test_capture_mix():
    assert 1 == 1
    return {
        '_name': 'demo',
        '_data': {
            'length': 10086,            # single value
            'accuracy': [0.1, 0.2, 0.3], # list
            'loss': [0.1, 0.2, 0.3],     # list
        }
    }
```

### Config Access

Read settings easily:
```python
from common.config_utils import config_utils
# Get config
db_config = config_utils.get_config("database")
api_config = config_utils.get_nested_config("easyPerf.api")
```

## 🛠️ Development Guide

### Adding New Tests

1. Create test files under `suites/` categories
2. Apply appropriate tags
3. Naming: `test_*.py`
4. Use fixtures & marks for data management
5. Keep custom marks concise and aligned with overall goals
