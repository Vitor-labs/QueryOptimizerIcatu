# Oracle SQL Query Optimizer

A sophisticated AI-powered tool that optimizes Oracle SQL queries through a two-stage process: converting SQL to natural language explanations, then reconstructing optimized queries from those explanations.

## 🎯 Features

- **Two-Stage Optimization**: SQL → Natural Language → Optimized SQL
- **Oracle DB Specialized**: Tailored prompts and optimization strategies for Oracle databases
- **Version Control**: Automatic versioning and metadata tracking for query optimizations
- **Multi-LLM Support**: Works with OpenAI GPT, Google Gemini, and Anthropic Claude
- **File-Based Processing**: Process `.sql` files and generate JSON metadata
- **Type-Safe**: Full Python 3.12 type hints and modern async/await patterns
- **SOLID Architecture**: Clean, maintainable code following SOLID principles

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- API key for your chosen LLM provider

### Installation

**Install dependencies with uv:**
```bash
# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## 📖 Usage

### Basic Usage

Optimize a SQL file using the default settings (Gemini):

```bash
uv run python src/main.py optimize query.sql
```

### Advanced Usage

**Use a specific LLM provider:**
```bash
# Use OpenAI GPT-4
uv run python src/main.py optimize query.sql --provider openai --model gpt-4

# Use Anthropic Claude
uv run python src/main.py optimize query.sql --provider claude --model claude-3-5-sonnet-20241022

# Use Google Gemini (default)
uv run python src/main.py optimize query.sql --provider gemini --model gemini-2.0-flash
```

**Enable verbose output:**
```bash
uv run python src/main.py optimize query.sql --verbose
```

**Use a custom API key:**
```bash
uv run python src/main.py optimize query.sql --api-key your-custom-api-key
```

**Complete example:**
```bash
uv run python src/main.py optimize examples/complex_query.sql \
  --provider openai \
  --model gpt-4 \
  --verbose \
  --api-key sk-your-openai-key
```

### Example SQL File

Create a file `query.sql`:
```sql
SELECT e.employee_id, e.first_name, e.last_name, d.department_name, e.salary
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE e.hire_date >= TO_DATE('2020-01-01', 'YYYY-MM-DD')
AND e.salary > 50000
ORDER BY e.salary DESC;
```

### Output

The tool generates:

1. **Console output** with optimization summary
2. **JSON metadata file** (`query_optimization.json`) containing:
   ```json
   {
     "query_sql": "SELECT e.employee_id, e.first_name...",
     "explanation_text": "This query retrieves employee information...",
     "version": "0.0",
     "last_optimization": "2024-01-15"
   }
   ```

## 🏗️ Project Structure

```
oracle-sql-optimizer/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── interfaces.py          # Abstract interfaces
│   │   └── types.py               # Core data types
│   ├── llm/
│   │   ├── __init__.py
│   │   └── clients.py             # LLM client implementations
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── file_handler.py        # File operations
│   │   └── metadata_repository.py # Metadata persistence
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prompt_generator.py    # AI prompt generation
│   │   └── query_optimizer.py    # Main optimization logic
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration classes
│   │   └── logger.py              # Logging setup
│   └── main.py                    # CLI entry point
├── examples/                      # Example SQL files
├── tests/                        # Test suite
├── pyproject.toml                # uv project configuration
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## ⚙️ Configuration

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--provider` | `gemini` | LLM provider (`gemini`, `openai`, `claude`) |
| `--model` | Provider default | Specific model to use |
| `--api-key` | From env | API key override |
| `--verbose` | `False` | Enable detailed output |

## 📝 Examples

### Example 1: Simple Query Optimization

**Input (`simple.sql`):**
```sql
SELECT * FROM employees WHERE salary > 50000;
```

**Command:**
```bash
uv run python src/main.py optimize simple.sql --verbose
```

**Output:**
```
🎯 Optimization Results:
==================================================
📄 Original Query: simple.sql
📝 Explanation: This query retrieves all employee records where the salary is greater than 50,000...
⚡ Optimized Query Preview: SELECT /*+ INDEX(employees emp_salary_idx) */ employee_id, first_name, last_name...
📊 Version: 0.0
⏰ Last Optimization: 2024-01-15T10:30:45.123456
💾 Full results saved to: simple_optimization.json
```

### Example 2: Complex Join Optimization

**Input (`complex.sql`):**
```sql
SELECT e.first_name, e.last_name, d.department_name, p.project_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN project_assignments pa ON e.employee_id = pa.employee_id
JOIN projects p ON pa.project_id = p.project_id
WHERE e.hire_date >= '2020-01-01'
AND p.status = 'ACTIVE';
```

**Command:**
```bash
uv run python src/main.py optimize complex.sql --provider openai --model gpt-4
```

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the verbose output with `--verbose` flag
- Ensure your API keys have sufficient credits/permissions
