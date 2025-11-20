"""Telegram bot scaffolding for Melbourne Transit Assistant."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .ptv_client import PTVClient
from .parking_service import (
    UnknownParkingAreaError,
    fetch_parking_availability,
    list_parking_areas,
)
from .openai_assistant import TransitAssistant

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

    LOGGER.info(f"=== /start command received ===")
    
    message = update.effective_message
    if message is None:
        LOGGER.warning("No effective_message in /start update")
        return

    intro_lines = [
        "👋 Welcome to the Melbourne Transit Assistant!",
        "Use /departures <stop_id> [route_type] [max_results] to see upcoming services.",
        "Try /parking to discover available parking bays in the CBD.",
    ]
    
    LOGGER.info("Sending start message")
    await message.reply_text("\n".join(intro_lines))
    LOGGER.info("=== /start command SUCCESS ===")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain available commands."""

    message = update.effective_message
    if message is None:
        return

    help_text = (
        "Available commands:\n\n"
        "🚆 Transit:\n"
        "/departures <stop_id> [route_type] [max_results] - Upcoming departures\n\n"
        "🅿️ Parking:\n"
        "/parking [area_key] - Parking in configured areas (melbourne_cbd, geelong_cbd)\n"
        "/find_parking <location> - Find parking near any location\n"
        "/parking_areas - List all configured parking areas\n\n"
        "🤖 AI Assistant:\n"
        "/ask <question> - Ask anything about transit/parking (requires OpenAI API key)\n"
        "Example: /ask Where can I park near Southern Cross?\n\n"
        "ℹ️ Info:\n"
        "/start - Welcome message\n"
        "/help - This help"
    )
    await message.reply_text(help_text)


def _parse_int(value: str, *, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


async def departures_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /departures command requests."""

    try:
        message = update.effective_message
        if message is None:
            LOGGER.warning("No effective_message in update")
            return

        LOGGER.info(f"=== /departures command START ===")
        LOGGER.info(f"Raw context.args: {context.args}")
        LOGGER.info(f"Type of args: {type(context.args)}")
        LOGGER.info(f"Num args: {len(context.args) if context.args else 0}")

        # Handle case where all args are in one string (space-separated)
        args = context.args
        if args and len(args) == 1 and ' ' in args[0]:
            LOGGER.info("Detected space-separated args in single string, splitting...")
            args = args[0].split()
            LOGGER.info(f"After split: {args}")

        if not args:
            LOGGER.info("No args provided, sending usage message")
            await message.reply_text("Usage: /departures <stop_id> [route_type] [max_results]\n\nExample: /departures 1071 0 5")
            return

        stop_id = _parse_int(args[0])
        if stop_id is None:
            LOGGER.info(f"Invalid stop_id: {args[0]}")
            await message.reply_text(f"Stop ID must be an integer, got: {args[0]}")
            return

        route_type = _parse_int(args[1], default=0) if len(args) > 1 else 0
        if route_type is None:
            route_type = 0
        
        max_results = _parse_int(args[2], default=5) if len(args) > 2 else 5
        if max_results is None:
            max_results = 5

        LOGGER.info(f"Parsed: stop_id={stop_id}, route_type={route_type}, max_results={max_results}")
        
        ptv_client = context.application.bot_data.get("ptv_client")
        if ptv_client is None:
            LOGGER.error("PTVClient not found in bot_data!")
            await message.reply_text("Bot configuration error: PTV client not initialized")
            return

        LOGGER.info(f"Got PTVClient: {type(ptv_client)}")
        LOGGER.info(f"Calling get_departures...")
        
        response = ptv_client.get_departures(
            route_type=route_type,
            stop_id=stop_id,
            max_results=max_results,
            expand=["run", "route", "stop"],
        )
        
        LOGGER.info(f"Response received: {len(response.get('departures', []))} departures")

        departures = response.get("departures", [])
        if not departures:
            LOGGER.info("No departures in response")
            await message.reply_text("No upcoming departures found.")
            return

        formatted_lines = [
            f"Departures for stop {stop_id} (route type {route_type})",
            "",
        ]

        for dep in departures[:10]:
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

        LOGGER.info(f"Sending response: {len(formatted_lines)} lines")
        await message.reply_text("\n".join(formatted_lines))
        LOGGER.info(f"=== /departures command SUCCESS ===")
        
    except Exception as e:
        LOGGER.exception(f"=== ERROR in departures_command ===: {e}")
        try:
            if update.effective_message:
                await update.effective_message.reply_text(f"Error: {str(e)[:150]}")
        except Exception as send_err:
            LOGGER.error(f"Failed to send error message: {send_err}")


async def parking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List parking availability via TomTom (or mock data if unavailable)."""

    try:
        message = update.effective_message
        if message is None:
            return

        LOGGER.info(f"Received /parking command with args: {context.args}")

        area_key = context.args[0].lower() if context.args else "melbourne_cbd"

        try:
            LOGGER.info(f"Fetching parking availability for area: {area_key}")
            availability = fetch_parking_availability(area_key)
            LOGGER.info(f"Got {len(availability)} parking locations")
        except UnknownParkingAreaError:
            suggestions = ", ".join(area.key for area in list_parking_areas())
            await message.reply_text(f"Unknown area '{area_key}'. Try one of: {suggestions}")
            return
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Parking request failed")
            await message.reply_text(f"Parking lookup failed: {exc}")
            return

        if not availability:
            await message.reply_text("No parking locations returned.")
            return

        lines = [f"🅿️ Parking in {area_key}:"]
        keyboard = []
        
        # Limit to 5 items to keep message under Telegram's 4096 char limit
        for item in availability[:5]:
            status = item.get("status") or "UNKNOWN"
            available = item.get("available")
            total = item.get("total")
            name = item.get("name") or item.get("id")
            address = item.get("address") or "Address unavailable"
            latitude = item.get("latitude")
            longitude = item.get("longitude")
            
            # Shorten address if too long
            if len(address) > 60:
                address = address[:57] + "..."
            
            # Add emoji based on availability
            if status == "AVAILABLE":
                emoji = "✅"
            elif status == "LIMITED":
                emoji = "⚠️"
            else:
                emoji = "❌"
            
            lines.append(
                f"{emoji} {name}\n   {available}/{total} free"
            )
            
            # Add Google Maps button if coordinates available
            if latitude is not None and longitude is not None:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
                button_text = f"📍 {name} - Directions"
                keyboard.append([InlineKeyboardButton(button_text, url=maps_url)])

        text = "\n".join(lines)
        LOGGER.info(f"Sending parking response: {len(text)} chars")
        
        # Add keyboard to message if we have buttons
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(text, reply_markup=reply_markup)
        else:
            await message.reply_text(text)
    except Exception as e:
        LOGGER.exception(f"Error in parking_command: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("Sorry, an error occurred processing your request.")


async def find_parking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Find parking near a specific location (e.g., 'Southern Cross Station')."""

    try:
        message = update.effective_message
        if message is None:
            return

        LOGGER.info(f"Received /find_parking command with args: {context.args}")

        # Get location from arguments
        if not context.args:
            await message.reply_text(
                "Usage: /find_parking <location>\n\n"
                "Examples:\n"
                "  /find_parking Southern Cross Station\n"
                "  /find_parking Flinders Street\n"
                "  /find_parking Queen Victoria Market"
            )
            return

        # Join args as location name
        location = " ".join(context.args)
        LOGGER.info(f"Searching parking near: {location}")

        try:
            from .here_client import HEREParkingClient
            from config.parking import HERE_API_KEY

            if not HERE_API_KEY:
                await message.reply_text("Parking search not configured (missing HERE API key).")
                return

            client = HEREParkingClient(HERE_API_KEY)
            availability = client.search_parking_by_location(location, limit=5)
            LOGGER.info(f"Found {len(availability)} parking locations near {location}")

        except ValueError as e:
            await message.reply_text(f"❌ Location not found: {location}\n\nPlease try a known Melbourne location.")
            return
        except Exception as e:
            LOGGER.exception(f"Parking search failed: {e}")
            await message.reply_text(f"❌ Parking search failed: {e}")
            return

        if not availability:
            await message.reply_text(f"No parking found near {location}")
            return

        # Filter parking spots under 1 km (1000 meters)
        nearby_parking = [item for item in availability if item.get("distance", float('inf')) < 1000]
        
        if not nearby_parking:
            await message.reply_text(f"❌ No parking found under 1 km near {location}\n\nClosest option is {availability[0].get('distance', 0)/1000:.1f}km away.")
            return

        # Format response with inline keyboard buttons for Google Maps
        lines = [f"🅿️ Parking spots under 1km from {location}:\n"]
        
        for i, item in enumerate(nearby_parking, 1):
            name = item.get("name", "Parking")
            distance = item.get("distance", 0)
            address = item.get("address", "")
            latitude = item.get("latitude")
            longitude = item.get("longitude")

            # Convert distance to km or meters
            if distance > 1000:
                distance_str = f"{distance/1000:.1f}km"
            else:
                distance_str = f"{distance}m"

            # Build response with coordinates
            lines.append(f"{i}. {name}")
            lines.append(f"   📍 Distance: {distance_str}")
            if latitude is not None and longitude is not None:
                lines.append(f"   🎯 Coordinates: {latitude:.4f}, {longitude:.4f}")
            if address and address != "Address unavailable":
                lines.append(f"   📮 {address}")
            lines.append("")  # Blank line between entries

        text = "\n".join(lines)
        LOGGER.info(f"Sending find_parking response: {len(text)} chars with {len(nearby_parking)} spots under 1km")
        
        # Create inline keyboard with Google Maps buttons
        keyboard = []
        for item in nearby_parking:
            latitude = item.get("latitude")
            longitude = item.get("longitude")
            name = item.get("name", "Parking")
            
            if latitude is not None and longitude is not None:
                # Create Google Maps URL
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
                button_text = f"📍 {name} - Get Directions"
                keyboard.append([InlineKeyboardButton(button_text, url=maps_url)])
        
        # Add keyboard to message if we have buttons
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(text, reply_markup=reply_markup)
        else:
            await message.reply_text(text)

    except Exception as e:
        LOGGER.exception(f"Error in find_parking_command: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("Sorry, an error occurred processing your request.")


async def list_parking_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    areas = list_parking_areas()
    message = update.effective_message
    if message is None:
        return
    lines = ["Configured parking areas:"]
    for area in areas:
        lines.append(f"• {area.key} – {area.display_name}")
    await message.reply_text("\n".join(lines))


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ask command for natural language queries."""

    try:
        message = update.effective_message
        if message is None:
            return

        LOGGER.info(f"Received /ask command with args: {context.args}")

        # Get query from arguments
        if not context.args:
            await message.reply_text(
                "Ask me anything about Melbourne transit or parking!\n\n"
                "Examples:\n"
                "  /ask Where can I park near Southern Cross Station?\n"
                "  /ask What trains depart from Flinders Street?\n"
                "  /ask Find me parking near Queen Vic Market"
            )
            return

        # Join args as the query
        user_query = " ".join(context.args)
        LOGGER.info(f"Processing AI query: {user_query}")

        # Get OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_key or openai_key == "your_openai_api_key_here":
            await message.reply_text(
                "❌ OpenAI not configured. Please set OPENAI_API_KEY in your .env file.\n\n"
                "Get a free API key at: https://platform.openai.com/api-keys"
            )
            return

        try:
            # Use OpenAI to understand the query
            assistant = TransitAssistant(openai_key)
            intent = assistant.understand_query(user_query)
            LOGGER.info(f"Query intent: {intent}")

            # Route based on intent
            if intent.get("type") == "parking":
                location = intent.get("location")
                if not location:
                    await message.reply_text("❌ Could not understand the location. Please try again.")
                    return

                await message.reply_text(f"🔍 Searching parking near {location}...")

                try:
                    from .here_client import HEREParkingClient
                    from config.parking import HERE_API_KEY

                    if not HERE_API_KEY:
                        await message.reply_text("Parking search not configured.")
                        return

                    client = HEREParkingClient(HERE_API_KEY)
                    parking_data = client.search_parking_by_location(location, limit=5)
                    
                    # Format response
                    response_lines = [f"🅿️ Parking near {location}:"]
                    for item in parking_data[:5]:
                        name = item.get("name", "Parking")
                        available = item.get("available", "?")
                        total = item.get("total", "?")
                        response_lines.append(f"  • {name}: {available}/{total} free")

                    await message.reply_text("\n".join(response_lines))

                except Exception as e:
                    LOGGER.exception(f"Parking search failed: {e}")
                    await message.reply_text(f"❌ Could not find parking: {e}")

            elif intent.get("type") == "departures":
                stop = intent.get("stop")
                if not stop:
                    await message.reply_text("❌ Could not understand the stop. Please try again.")
                    return

                await message.reply_text(f"🔍 Searching departures from {stop}...")
                await message.reply_text("Coming soon: Departures search via AI is in development!")

            else:
                await message.reply_text("I can help you find parking or transit information. Try asking about either!")

        except Exception as e:
            LOGGER.exception(f"AI processing error: {e}")
            await message.reply_text(f"❌ Error processing query: {str(e)[:100]}")

    except Exception as e:
        LOGGER.exception(f"Error in ask_command: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("Sorry, an error occurred.")


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze command for text analysis using OpenAI."""

    try:
        message = update.effective_message
        if message is None:
            return

        LOGGER.info(f"Received /analyze command with args: {context.args}")

        # Get text to analyze
        if not context.args:
            await message.reply_text(
                "📝 Analyze any text!\n\n"
                "Usage: /analyze <text_to_analyze>\n\n"
                "Examples:\n"
                "  /analyze The quick brown fox jumps over the lazy dog\n"
                "  /analyze I love this product, it's amazing!\n"
                "  /analyze Climate change is a serious issue we must address"
            )
            return

        # Join args as the text
        user_text = " ".join(context.args)
        LOGGER.info(f"Analyzing text: {len(user_text)} chars")

        # Get OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_key or openai_key == "your_openai_api_key_here":
            await message.reply_text(
                "❌ OpenAI not configured. Please set OPENAI_API_KEY in your .env file.\n\n"
                "Get a free API key at: https://platform.openai.com/api-keys"
            )
            return

        try:
            from .openai_assistant import TextAnalyzer

            # Show analyzing status
            await message.reply_text("🔍 Analyzing your text...")

            # Create analyzer
            analyzer = TextAnalyzer(openai_key)

            # Perform analysis
            analysis = analyzer.analyze_all(user_text)

            # Format response
            response_lines = []
            response_lines.append("📊 Text Analysis Results:\n")

            # Summary
            response_lines.append("📌 Summary:")
            response_lines.append(analysis["summary"])
            response_lines.append("")

            # Key points
            response_lines.append("🔑 Key Points:")
            for point in analysis["key_points"][:5]:  # Limit to 5 points
                if point.strip():
                    response_lines.append(f"  • {point.strip()}")
            response_lines.append("")

            # Sentiment
            sentiment_info = analysis["sentiment"]
            sentiment = sentiment_info["sentiment"]
            sentiment_emoji = {
                "POSITIVE": "😊",
                "NEGATIVE": "😞",
                "NEUTRAL": "😐",
            }.get(sentiment, "❓")
            response_lines.append(f"😊 Sentiment: {sentiment_emoji} {sentiment}")

            text = "\n".join(response_lines)

            # Check message length (Telegram limit is 4096)
            if len(text) > 4000:
                text = text[:3950] + "\n...(truncated)"

            await message.reply_text(text)
            LOGGER.info(f"Analysis sent: {len(text)} chars")

        except Exception as e:
            LOGGER.exception(f"Text analysis error: {e}")
            await message.reply_text(f"❌ Error analyzing text: {str(e)[:100]}")

    except Exception as e:
        LOGGER.exception(f"Error in analyze_command: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("Sorry, an error occurred.")


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
    application.add_handler(CommandHandler("find_parking", find_parking_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("parking_areas", list_parking_command))

    # Add error handler
    application.add_error_handler(error_handler)

    return application


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    LOGGER.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"Sorry, an error occurred. Please try again."
            )
        except Exception as e:
            LOGGER.error(f"Failed to send error message: {e}")


def _post_init(ptv_client: PTVClient):
    async def _initializer(app: Application) -> None:
        LOGGER.info(f"Initializing bot_data with PTVClient: {ptv_client}")
        app.bot_data["ptv_client"] = ptv_client
        LOGGER.info(f"Bot data initialized: {app.bot_data.keys()}")
    return _initializer


def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    config = build_bot_config()
    application = build_application(config)
    LOGGER.info("Starting Telegram bot")
    LOGGER.info("Bot is listening for messages. Press Ctrl+C to stop.")
    try:
        application.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    run_bot()
