# Personal Memory MCP Server

A modern MCP (Model Context Protocol) server that provides Claude Desktop with the ability to store and retrieve personal information locally.

## Features

* **Personal Information**: Store and retrieve basic personal details
* **Preferences**: Organize preferences by category (food, music, work, etc.)
* **Memories**: Store memories with tags and context for easy searching
* **Relationships**: Track information about people you know
* **Goals**: Manage personal and professional goals with status tracking
* **Local Storage**: All data stored securely in a local JSON file

## Quick Start

### Prerequisites

* Python 3.10 or higher
* [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. Clone or download this project
2. Install uv if you haven't already:
   

```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Set up the project:
   

```bash
   cd personal-memory-mcp
   uv sync
   ```

### Configuration

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "personal-memory": {
      "command": "uv",
      "args": ["run", "memory-server"],
      "cwd": "/path/to/personal-memory-mcp"
    }
  }
}
```

Replace `/path/to/personal-memory-mcp` with the actual path to your project directory.

### Usage

After configuration, restart Claude Desktop. You can then use natural language to interact with your memory:

* "Remember that my favorite coffee is cappuccino"
* "Store that I met Sarah at the conference - she's a data scientist"
* "Add a goal to learn Spanish by the end of the year"
* "What do you remember about my food preferences?"
* "Show me my active goals"

### Testing the Server

You can test the server functionality with the MCP Inspector:

```bash
uv run mcp dev server.py
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run ruff check .
```

### Running the Server Directly

```bash
uv run python memory_server.py
```

## Data Storage

All personal data is stored locally in `personal_memory.json` in the project directory. The file includes:

* Personal information (name, location, etc.)
* Categorized preferences
* Timestamped memories with tags
* Relationship information
* Goals with status tracking

## Privacy & Security

* **Local Only**: All data stays on your machine
* **No Network**: No data transmitted to external servers
* **Full Control**: You own and control all your data
* **Backup Friendly**: Simple JSON format for easy backup

## License

MIT License - see LICENSE file for details.
