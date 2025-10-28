# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal AI agent (Agente Personal) powered by Claude that helps users stay organized, manage calendars, plan learning, and more. The project is in early development with CLI interface functional, while Telegram Bot and Web API are planned.

**Language:** Spanish (primary language for user interactions and documentation)
**Target Platform:** Arch Linux and Unix systems
**Python Version:** 3.11+
**Package Manager:** UV (not pip)

## Development Commands

### Running the Agent

```bash
# Using UV (preferred)
uv run python main.py

# Or with activated venv
source .venv/bin/activate
python main.py
```

### Setup and Dependencies

```bash
# Initial setup (creates .env, data dirs, installs deps)
./scripts/setup.sh

# Sync dependencies after pyproject.toml changes
uv sync

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name
```

### Code Quality

```bash
# Format code (line length: 100)
uv run black src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/

# Run all quality checks
uv run black src/ && uv run ruff check src/ && uv run mypy src/
```

### Testing

```bash
# Run all tests (when available)
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src
```

## Architecture

### Core Components

**`src/core/agent.py` - PersonalAgent class**
- Main orchestration layer for the entire system
- Manages conversation history per user (multi-user support via user_id)
- Interfaces with Claude API using Anthropic SDK
- Builds system prompt from `config/agent_config.yaml`
- Key methods: `process()`, `get_agenda()`, `create_task()`, `create_event()`
- All integration methods (calendar, tasks, etc.) are currently stubs returning TODO placeholders

**`src/utils/config.py` - Configuration Management**
- `Settings` class: Loads environment variables from `.env` using pydantic-settings
- `load_yaml_config()`: Loads behavioral configuration from `config/agent_config.yaml`
- Two-layer config system:
  - `.env` → credentials, paths, technical settings (Settings)
  - `agent_config.yaml` → agent personality, behavior, feature flags, schedules

**`src/interfaces/cli.py` - CLI Interface**
- Uses Rich library for formatted console output
- Handles special commands: `/help`, `/agenda [days]`, `/clear`, `/exit`
- Non-command messages are forwarded to `PersonalAgent.process()`
- Displays responses as Markdown in styled panels

### Configuration System

**Environment Variables (`.env`):**
- Required: `ANTHROPIC_API_KEY`
- Optional: Calendar path, Redis URL, Telegram tokens, logging settings
- Interface toggles: `ENABLE_CLI`, `ENABLE_TELEGRAM`, `ENABLE_WEB`

**Agent Config YAML (`config/agent_config.yaml`):**
- Agent personality and language settings
- Feature flags for task management, calendar, learning planner
- Work hours, deep work blocks, default event durations
- Learning session parameters and spaced repetition intervals
- Notification timing (advance warnings, daily summaries)
- Integration settings for Logseq, AppFlowy, GitHub, email (all currently disabled)

### Data Flow

1. User input → CLI Interface (`CLIInterface.run()`)
2. Command check → If command: handle locally; else: forward to agent
3. Agent processes → `PersonalAgent.process(message, user_id)`
4. Conversation history managed per user_id (default: "default")
5. System prompt built from YAML config + user message + history → Claude API
6. Response extracted and added to history
7. Response returned → CLI displays in Rich panel

### Pending Integrations (Stubs in place)

- **Calendar:** Calcurse integration planned (path configurable via CALENDAR_PATH)
- **Notifications:** Desktop notifications via dunst
- **Knowledge bases:** Logseq and AppFlowy integration
- **Telegram:** Bot interface with user ID whitelist
- **Web API:** FastAPI + WebSockets planned
- **Database:** SQLAlchemy + aiosqlite for task/event persistence
- **Caching:** Redis for multi-device sync (USE_REDIS flag)

## Development Guidelines

### Adding New Features

When adding features to the agent:

1. If it's a new integration (e.g., GitHub, email):
   - Create module in `src/integrations/`
   - Add configuration to `config/agent_config.yaml`
   - Add environment variables to `.env.example` if needed
   - Update `PersonalAgent` to orchestrate the integration

2. If it's a new interface (e.g., voice, mobile):
   - Create module in `src/interfaces/`
   - Follow pattern from `cli.py`: create class that wraps `PersonalAgent`
   - Add enable flag to Settings in `config.py`
   - Update `main.py` to support the new interface

3. If it's a new capability for the agent:
   - Add method to `PersonalAgent` class
   - Update system prompt builder if needed
   - Consider if it needs external integration or just LLM processing

### Logging

- All modules should use Python's logging module
- Logger name: `logging.getLogger(__name__)`
- Logs written to `data/logs/agent.log` (configurable via LOG_PATH)
- Log level configurable via LOG_LEVEL environment variable

### Conversation History

- History is stored per user_id in memory (`PersonalAgent.conversation_history`)
- Limited to `AGENT_MAX_CONTEXT_MESSAGES` (default: 20)
- Format: List of dicts with `{"role": "user"|"assistant", "content": str}`
- Use `clear_history(user_id)` to reset

### Model Configuration

- Default model: `claude-sonnet-4-5` (configurable via AGENT_MODEL)
- Temperature: 0.7 (configurable via AGENT_TEMPERATURE)
- Max tokens per response: 2048 (hardcoded in agent.py:111)

## Common Patterns

### Accessing Configuration

```python
from src.utils.config import get_settings, load_yaml_config

settings = get_settings()  # Environment variables
config = load_yaml_config()  # YAML configuration

# Example: Check if feature is enabled
if config.get("features", {}).get("calendar_integration"):
    # Do calendar stuff
```

### Adding to System Prompt

Edit `PersonalAgent._build_system_prompt()` to include new capabilities or instructions.

### Multi-user Support

Always pass `user_id` parameter to agent methods:
```python
response = await agent.process(message, user_id="telegram_123456")
agenda = await agent.get_agenda(user_id="telegram_123456", days=3)
```

## Important Notes

- **All user-facing text should be in Spanish** unless user explicitly requests English
- Agent personality is "profesional y proactivo" by default
- The project uses UV, not pip - always use `uv` commands for package management
- Many integrations have stub implementations with TODO comments
- Current focus is on CLI interface; other interfaces are scaffolded but not implemented
