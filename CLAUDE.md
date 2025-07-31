# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal Memory MCP Server - A Model Context Protocol server that enables Claude Desktop to store and retrieve personal information locally using JSON-based storage.

## Development Setup

**Package Manager**: Uses `uv` for dependency management
**Python Version**: 3.10+ (recommended 3.12)

### Essential Commands

```bash
# Install dependencies
uv sync

# Run the server
uv run python server.py

# Run tests (when available)
uv run pytest

# Code formatting and linting
uv run black .
uv run ruff check .
uv run ruff check . --fix
```

### Entry Point Configuration
The entry point is correctly configured as `memory_server:main` in `pyproject.toml`. Use `uv run python memory_server.py` to run the server directly.

## Architecture

### Core Components

**PersonalMemoryStorage Class** (`server.py:16-224`)
- JSON-based local storage in `personal_memory.json`
- Manages 5 data categories: personal_info, preferences, memories, relationships, goals
- Thread-safe file operations with automatic backup on save

**FastMCP Integration** (`memory_server.py:614-656`)
- 17 exposed tools for CRUD operations, data organization, and interactive categorization
- Uses FastMCP library for efficient MCP protocol handling
- Tools follow naming pattern: `store_*`, `get_*`, `add_*`, `update_*`, `search_*`, `reorganize_*`, `move_*`, `categorize_*`

### Data Structure

**Hierarchical Personal Info Structure** (automatically migrated from flat format):
```json
{
  "personal_info": {
    "basic": {                   // Contact & basic info
      "name": "...",
      "woonplaats": "...",
      "linkedin_profile": "...",
      "email_infosupport": "...",
      "email_aigency": "..."
    },
    "career": {                  // Professional background
      "job_title": "...",
      "expertise": "...",
      "research_interests": "..."
    },
    "book": {                    // Book information (book_ prefix removed)
      "title": "...",
      "isbn": "...",
      "publisher": "..."
    },
    "work_roles": {              // Current roles & responsibilities
      "aigency_work": "...",
      "research_center_focus": "..."
    },
    "innovations": {             // Created tools & frameworks
      "formula_ai": {
        "concept": "...",
        "creator": true
      },
      "ai_experiment_canvas": {
        "structure": "...",
        "creator": true
      }
    },
    "communication": {           // Communication style & preferences
      "writing_style": "...",
      "podcast_details": "..."
    },
    "values_insights": {         // Core values & key insights
      "core_values": "...",
      "key_insights": "..."
    }
  },
  "preferences": {},             // Categorized preferences
  "memories": [],                // Timestamped entries with tags
  "relationships": {},           // People and relationship details  
  "goals": [],                   // Goals with status tracking
  "created_at": "ISO datetime",
  "last_updated": "ISO datetime"
}
```

**Key Access Methods:**
- **Hierarchical**: `"basic.name"`, `"book.title"`, `"innovations.formula_ai.concept"`
- **Legacy flat**: `"name"`, `"book_title"`, `"formula_ai_concept"` (backward compatible)
- **Direct category**: Access entire categories like `"book"` returns all book data

**Data Organization Tools:**
- **`reorganize_misc_items()`**: Automatically moves items from `misc` to appropriate categories based on keywords
- **`move_personal_info_item(from_path, to_path)`**: Manually move items between locations
- **`get_pending_categorization()`**: Lists items that need manual categorization with suggestions
- **`categorize_pending_item(key, target_category, new_key_name)`**: Interactively categorize pending items
- **`clear_pending_categorization()`**: Clear pending list (items stay in misc)
- **Smart categorization**: New items automatically placed in logical categories
- **Interactive prompts**: When items can't be auto-categorized, user gets prompted for placement
- **Flexible structure**: Easy to add new categories via dot notation

## Testing Approach

Expected test file location: `tests/test_memory_server.py`
Uses pytest with async support for testing MCP tools and storage operations.

**Test Coverage:**
- Basic storage and retrieval operations
- Hierarchical personal info structure (`test_hierarchical_personal_info`)
- Backward compatibility with legacy flat keys (`test_backward_compatibility`) 
- Flexible categorization for new keys (`test_flexible_categorization`)
- Misc items reorganization (`test_misc_reorganization`)
- Manual item moving (`test_manual_item_move`)
- Interactive categorization workflow (`test_interactive_categorization`)
- Memory, goals, and preference management

## Data Storage

Personal memory data is stored in iCloud at `/Users/joopsnijder/Library/Mobile Documents/com~apple~CloudDocs/personal-memory/personal_memory.json` for automatic backup and sync across devices.

## Claude Desktop Integration

Configure in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "personal-memory": {
      "command": "uv", 
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/personal-memory-mcp"
    }
  }
}
```

## Code Quality Standards

- **Line length**: 100 characters (Black + Ruff configuration)
- **Type hints**: Required for all function parameters and returns
- **Error handling**: JSON decode errors and file operations handled gracefully
- **Security**: Local-only storage, no network operations