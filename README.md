# LLM Monopoly

[![Watch the video](https://img.youtube.com/vi/5R6PUFFjHtw/hqdefault.jpg)](https://www.youtube.com/embed/5R6PUFFjHtw)

A Monopoly simulation where each player can be controlled by:

- an OpenAI model
- a Claude model
- a Gemini model
- an OpenRouter model
- a local Ollama model
- a human in the CLI

The engine runs game logic (movement, property ownership, auctions, trading, mortgages, houses, bankruptcy), while model adapters choose actions from structured prompts and JSON schemas.

## Features

- Config-driven board and player setup from JSON
- Multiple player backends in the same game (`openai`, `claude`, `gemini`, `openrouter`, `local`, `cli`)
- Structured move history via a broadcaster/listener pattern
- Optional Flask + Socket.IO server for static hosting and realtime events
- Pydantic models for IO contracts and game state snapshots

## Requirements

- Python `3.11`
- `uv` (recommended) or `pip`
- Optional:
  - OpenAI API key (for `openai` players)
  - Anthropic API key (for `claude` players)
  - Gemini API key (for `gemini` players)
  - OpenRouter API key (for `openrouter` players)
  - Ollama running locally on `http://localhost:11434` (for `local` players)

## Setup

### 1. Install dependencies

Using `uv`:

```bash
uv sync
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install anthropic dotenv flask flask-socketio openai pydantic
```

### 2. Configure environment variables

Create/update `.env` in the project root.

Example:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key
HOST=0.0.0.0
PORT=8080
```

Notes:

- `OPENAI_API_KEY` is required for `openai` players.
- `ANTHROPIC_API_KEY` is required for `claude` players.
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` is required for `gemini` players.
- `OPENROUTER_API_KEY` is required for `openrouter` players.
- `HOST` and `PORT` are used by the Flask/Socket.IO server.

## Running the Game

Run with a config JSON:

```bash
uv run python -m src.main monopoly_board.json
```

The CLI usage is:

```text
python -m src.main <config_path>
```

## Running the Web Server Only

```bash
uv run python -m src.server
```

Server behavior:

- Serves static files from `public/`
- Serves `public/index.html` at `/` and as fallback for unknown routes
- Exposes Socket.IO handlers under namespace `/ws` (`connect`, `ping`)

## Config File Format

Top-level shape:

```json
{
  "board": {
    "name": "Any name",
    "spaces": []
  },
  "players": []
}
```

### `board.spaces` types

- `space`
  - fields: `name`
- `property`
  - fields: `name`, `price`, `property_group`, `mortgage_value`, `house_cost`, `rent_costs`
- `tax`
  - fields: `name`, `cost`
- `railroad`
  - fields: `name`, `price`, `mortgage_value`, `rent_costs`
- `jail`
  - fields: `name`
- `utilities`
  - fields: `name`, `price`, `mortgage_value`
- `community_chest` / `chance`
  - fields: `name`

### `players` types

- `openai`
  - fields: `name`, `type`, `model`
  - requires `OPENAI_API_KEY`
- `openrouter`
  - fields: `name`, `type`, `model`
  - requires `OPENROUTER_API_KEY`
- `claude`
  - fields: `name`, `type`, `model`
  - requires `ANTHROPIC_API_KEY`
- `gemini`
  - fields: `name`, `type`, `model`
  - requires `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `local`
  - fields: `name`, `type`, `model`
  - uses Ollama-compatible endpoint at `http://localhost:11434/v1`
- `cli`
  - fields: `name`, `type`

### Minimal mixed-player example

```json
{
  "board": {
    "name": "Test Board",
    "spaces": [
      { "type": "space", "name": "Go" },
      {
        "type": "property",
        "name": "Mediterranean Avenue",
        "price": 60,
        "property_group": "brown",
        "mortgage_value": 30,
        "house_cost": 50,
        "rent_costs": [2, 10, 30, 90, 160, 250]
      },
      { "type": "tax", "name": "Income Tax", "cost": 200 },
      { "type": "jail", "name": "Go to Jail" }
    ]
  },
  "players": [
    { "name": "Human", "type": "cli" },
    { "name": "LocalBot", "type": "local", "model": "qwen3-coder:30b" }
  ]
}
```

## Game Flow Summary

- On startup, the board and players are created from config.
- Each turn, the current player chooses among actions such as:
  - `Roll`
  - `Trade`
  - `Mortgage`
  - `Manage houses` (if monopoly is owned)
- The engine emits move events (`begin_game`, `dice_roll`, property purchases, trades, bankruptcy, etc.).
- The game ends when only one non-bankrupt player remains.

## Architecture

- `src/main.py`
  - entrypoint, config parsing, board/player construction, starts game loop
- `src/board.py`
  - core turn engine and Monopoly mechanics
- `src/player.py`
  - player state and money/property operations
- `src/spaces/*`
  - behavior of board spaces
- `src/io/*`
  - model and CLI adapters + request/response schema contracts
- `src/move_broadcaster.py`
  - event history and listener fan-out
- `src/server.py`
  - Flask static hosting + Socket.IO setup

## Event Payload Shape

Moves are serialized as:

```json
{
  "player_name": "AI Player 1",
  "action_name": "dice_roll",
  "data": {},
  "game_state": {
    "player_locations": {},
    "properties_owned": {},
    "player_banks": {},
    "last_roll": 7,
    "doubles_count": 0,
    "previous_player_name": "AI Player 4"
  }
}
```

## Troubleshooting

- `ModuleNotFoundError` for dependencies:
  - run through `uv run ...` or install deps in your active environment.
- Missing API key errors:
  - ensure required keys are present in `.env`.
- Local model errors:
  - ensure Ollama is running and the specified model is installed.
