## Melbourne Transit Assistant

Melbourne Transit Assistant combines Public Transport Victoria (PTV) timetable data with TomTom's real-time parking availability to help travellers plan end-to-end journeys across Melbourne and Geelong. The repo includes a reusable Python client, ready-to-run example scripts, and a Telegram bot scaffolding that surfaces departures and parking availability directly in chat.

### ✨ Features

- PTV API client (`src/ptv_client.py`) for routes, stops, and live departures.
- TomTom parking integration with reusable helpers (`src/parking_service.py`) and CLI tooling.
- Telegram bot (`src/telegram_bot.py`) that responds to `/departures`, `/parking`, and helper commands.
- Example scripts under `examples/` for quick experiments and debugging.

## Getting started

1. **Install dependencies**

	```bash
	pip install -r requirements.txt
	```

2. **Set up credentials** — the bot and examples need PTV and TomTom keys:

   **Option A: Environment variables** (takes precedence)  
   Create a `.env` file or export variables:
   ```bash
   PTV_DEV_ID=your_ptv_developer_id
   PTV_API_KEY=your_ptv_api_key
   TOMTOM_API_KEY=your_tomtom_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

   **Option B: Fallback configuration file**  
   PTV credentials can also live in `config/credentials.py` (used if env vars are missing):
   ```python
   DEV_ID = "your_ptv_developer_id"
   API_KEY = "your_ptv_api_key"
   ```

   **Optional keys:**
   - `TOMTOM_API_KEY` is only needed if you use parking features.
   - `TELEGRAM_BOT_TOKEN` is only needed to run the Telegram bot.

3. **Run a quick departure check**

	```bash
	python examples/quick_departure.py
	```

   or use the parking CLI if `TOMTOM_API_KEY` is available:

	```bash
	python examples/parking_availability.py --list-areas
	```

## Telegram bot

The Telegram bot ships with a minimal command set and runs using long polling.
The bot will auto-load PTV credentials from `config/credentials.py` if not provided via environment variables.

### Getting a Telegram bot token

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts (choose a name and unique username ending in `bot`).
3. BotFather will reply with a token like `123456789:ABCDefGHIjklMNOpqrsTUVwxyzABCDefGH`.
4. Copy that token and set it as `TELEGRAM_BOT_TOKEN` before running the bot.

### Running the bot

```bash
export TELEGRAM_BOT_TOKEN="your_token_from_botfather"
python -m src.telegram_bot
```

Or add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

Available commands:

- `/start` – Welcome message with basic usage.
- `/help` – Short reference for supported commands.
- `/departures <stop_id> [route_type] [max_results]` – Upcoming services for a stop.
- `/parking [area_key]` – Real-time parking availability (default `melbourne_cbd`).
- `/parking_areas` – List configured parking search areas.

The bot caches a `PTVClient` instance internally and fetches parking data via TomTom when configured.

## Parking availability CLI

Use the CLI helper to inspect TomTom parking data from the terminal:

```bash
python examples/parking_availability.py --area melbourne_cbd --limit 5
```

Flags:

- `--area` – Parking area key (try `--list-areas` for options).
- `--limit` – Maximum number of locations to display (defaults to 10).
- `--list-areas` – Print configured areas and exit.

## Project structure

- `src/`
  - `ptv_client.py` – Thin wrapper over the PTV Timetable API v3.
  - `parking_service.py` – High-level helpers for TomTom parking availability.
  - `telegram_bot.py` – Long-polling Telegram bot scaffolding.
- `config/`
  - `parking.py` – Parking area definitions and TomTom API key loader.
- `examples/` – Ready-to-run scripts (departures, route exploration, parking, etc.).
- `docs/` – Additional documentation bundles (e.g., parking-system kit).

## Contributing & next steps

Up next on the roadmap: enrich the Telegram bot with richer stop search, blend parking data into journey suggestions, and expand automated testing. Feel free to open issues or submit PRs with improvements.

