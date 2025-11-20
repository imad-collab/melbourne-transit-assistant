"""Telegram bot scaffolding for Melbourne Transit Assistant."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from .ptv_client import PTVClient
from .parking_service import (
    MissingApiKeyError,
    UnknownParkingAreaError,
    fetch_parking_availability,
    list_parking_areas,
)

load_dotenv()

LOGGER = logging.getLogger(__name__)


@dataclass
class BotConfig:
    """Environment-driven configuration for the Telegram bot."""

    telegram_token: str
    ptv_dev_id: str
    ptv_api_key: str


def build_bot_config() -> BotConfig:
    """Load bot configuration from environment variables with config fallback.
    
    Telegram bot token is mandatory (no fallback available).
    PTV credentials fall back to config.credentials if not in env.
    """

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is required. Set it as an environment variable or in .env file."
        )

    ptv_dev_id = os.getenv("PTV_DEV_ID", "").strip()
    ptv_api_key = os.getenv("PTV_API_KEY", "").strip()

    # Try to fall back to config credentials if env vars are missing
    if not ptv_dev_id or not ptv_api_key:
        try:
            from config.credentials import DEV_ID, API_KEY
            if not ptv_dev_id:
                ptv_dev_id = DEV_ID
            if not ptv_api_key:
                ptv_api_key = API_KEY
        except ImportError:
            LOGGER.debug("config.credentials not available; relying on environment variables.")

    if not ptv_dev_id:
        raise RuntimeError(
            "PTV_DEV_ID is required. Set it as an environment variable, in .env file, or in config/credentials.py"
        )
    if not ptv_api_key:
        raise RuntimeError(
            "PTV_API_KEY is required. Set it as an environment variable, in .env file, or in config/credentials.py"
        )

    return BotConfig(
        telegram_token=telegram_token,
        ptv_dev_id=ptv_dev_id,
        ptv_api_key=ptv_api_key,
    )


def build_ptv_client(config: BotConfig) -> PTVClient:
    return PTVClient(config.ptv_dev_id, config.ptv_api_key)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user with a concise introduction."""

    message = update.effective_message
    if message is None:
        return

    intro_lines = [
        "👋 Welcome to the Melbourne Transit Assistant!",
        "Use /departures <stop_id> [route_type] [max_results] to see upcoming services.",
        "Try /parking to discover available parking bays in the CBD.",
    ]
    await message.reply_text("\n".join(intro_lines))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain available commands."""

    message = update.effective_message
    if message is None:
        return

    help_text = (
        "Available commands:\n"
        "/start - Show a welcome message\n"
        "/help - Display this help output\n"
        "/departures <stop_id> [route_type] [max_results] - Upcoming departures\n"
        "/parking [area_key] - Parking availability for configured areas"
    )
    await message.reply_text(help_text)


def _parse_int(value: str, *, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


async def departures_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /departures command requests."""

    message = update.effective_message
    if message is None:
        return

    if not context.args:
        await message.reply_text("Usage: /departures <stop_id> [route_type] [max_results]")
        return

    stop_id = _parse_int(context.args[0])
    if stop_id is None:
        await message.reply_text("Stop ID must be an integer")
        return

    route_type = (
        _parse_int(context.args[1], default=0) if len(context.args) > 1 else 0
    ) or 0
    max_results = (
        _parse_int(context.args[2], default=5) if len(context.args) > 2 else 5
    ) or 5

    ptv_client: PTVClient = context.application.bot_data["ptv_client"]

    try:
        response = ptv_client.get_departures(
            route_type=route_type,
            stop_id=stop_id,
            max_results=max_results,
            expand=["run", "route", "stop"],
        )
    except Exception as exc:  # noqa: BLE001 simple logging to user
        LOGGER.exception("PTV departures request failed")
        await message.reply_text(f"Failed to retrieve departures: {exc}")
        return

    departures = response.get("departures", [])
    if not departures:
        await message.reply_text("No upcoming departures found.")
        return

    formatted_lines = [
        f"Departures for stop {stop_id} (route type {route_type})",
        "",
    ]

    for dep in departures:
        run_id = dep.get("run_id")
        route_id = dep.get("route_id")
        estimated = dep.get("estimated_departure_utc") or dep.get("scheduled_departure_utc")
        platform = dep.get("platform_number")
        formatted_lines.append(
            "• Run #{run_id} on route {route_id} at {time}{platform}".format(
                run_id=run_id,
                route_id=route_id,
                time=estimated or "unknown time",
                platform=f" (Platform {platform})" if platform else "",
            )
        )

    await message.reply_text("\n".join(formatted_lines))


async def parking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List parking availability via TomTom."""

    message = update.effective_message
    if message is None:
        return

    area_key = context.args[0].lower() if context.args else "melbourne_cbd"

    try:
        availability = fetch_parking_availability(area_key)
    except UnknownParkingAreaError:
        suggestions = ", ".join(area.key for area in list_parking_areas())
        await message.reply_text(f"Unknown area '{area_key}'. Try one of: {suggestions}")
        return
    except MissingApiKeyError:
        await message.reply_text("Parking is not configured (missing TomTom API key).")
        return
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("TomTom parking request failed")
        await message.reply_text(f"Parking lookup failed: {exc}")
        return

    if not availability:
        await message.reply_text("No parking locations returned.")
        return

    lines = [f"Parking availability for {area_key}:"]
    for item in availability[:10]:
        status = item.get("status") or "UNKNOWN"
        available = item.get("available")
        total = item.get("total")
        name = item.get("name") or item.get("id")
        address = item.get("address") or "Address unavailable"
        lines.append(
            f"• {name} – {status} ({available}/{total} free)\n  {address}"
        )

    await message.reply_text("\n".join(lines))


async def list_parking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    areas = list_parking_areas()
    message = update.effective_message
    if message is None:
        return
    lines = ["Configured parking areas:"]
    for area in areas:
        lines.append(f"• {area.key} – {area.display_name}")
    await message.reply_text("\n".join(lines))


def build_application(config: BotConfig) -> Application:
    ptv_client = build_ptv_client(config)
    application: Application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .rate_limiter(AIORateLimiter(max_retries=3))
        .post_init(_post_init(ptv_client))
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("departures", departures_command))
    application.add_handler(CommandHandler("parking", parking_command))
    application.add_handler(CommandHandler("parking_areas", list_parking_command))

    return application


def _post_init(ptv_client: PTVClient):
    async def _initializer(app: Application) -> None:
        app.bot_data["ptv_client"] = ptv_client
    return _initializer


def run_bot() -> None:
    logging.basicConfig(level=logging.INFO)
    config = build_bot_config()
    application = build_application(config)
    LOGGER.info("Starting Telegram bot")
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    run_bot()
