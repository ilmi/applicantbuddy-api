# IDE AI Agent Instructions

## Code Quality & Documentation

- Write minimal comments only when code logic is complex or non-obvious
- Prioritize self-documenting code with clear variable and function names
- Add docstrings for public APIs and complex functions

## Dependency Management

- Use `uv add <package>` for all dependency installations
- Never use pip, poetry, or other package managers
- Update pyproject.toml dependencies through uv commands only

## Code Execution Policy

- Do NOT run Python scripts or execute makefiles
- Exception: Use `python -m py_compile <file>` to syntax-check code only
- Avoid any execution that could modify the system or environment

## Research & Implementation

- When implementing new features, use `context7` first to fetch relevant package documentation
- Review official docs and best practices before coding
- Understand the package API thoroughly before implementation

## Code Formatting

- Always run `make format` as the final step after completing all tasks
- Ensure consistent code style across the project
- Do not proceed to next task until formatting is complete

## File Organization

Follow this established project structure:

```
app/
├── core/
│   ├── extended_settings/
│   │   ├── app_settings.py
│   │   ├── database_settings.py
│   │   └── llm_settings.py
│   ├── models.py
│   └── settings.py
├── database/
│   ├── engine.py
│   └── models.py
├── router/
│   └── example_router.py
├── services/
├── tasks/
│   └── example_tasks.py
├── utils/
│   └── generate_ids.py
├── celery.py
└── main.py
```

**Key Rules:**

- Place all Response/Request schemas in the `schema/` folder (create if missing)
- Keep settings modular in `core/extended_settings/`
- Database-related code goes in `database/`
- API routes in `router/`
- Business logic in `services/`
- Background tasks in `tasks/`
- Utility functions in `utils/`
- Use descriptive filenames that indicate the module purpose

## Logging

- Use `loguru` as the logging library (not Python's built-in `logging`)
- Configure appropriate log levels for different environments
- Include contextual information in log messages

## Prohibited Actions

- Never create example usage files or demo scripts
- Do not generate sample data or test fixtures unless explicitly requested
- Avoid creating unnecessary boilerplate files
