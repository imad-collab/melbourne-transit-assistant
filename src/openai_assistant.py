"""OpenAI-powered assistant for natural language queries about transit and parking."""
from __future__ import annotations

import json
import logging
from typing import Optional

from openai import OpenAI

LOGGER = logging.getLogger(__name__)


class TransitAssistant:
    """Uses OpenAI to understand user queries and route them to appropriate functions."""

    SYSTEM_PROMPT = """You are a helpful Melbourne transit and parking assistant. 
You help users find:
1. Public transport departures (trains, trams, buses)
2. Parking spots near locations

When users ask about departures or transport:
- Extract the stop name or ID
- Return JSON: {"type": "departures", "stop": "stop_name_or_id", "route_type": "optional"}

When users ask about parking:
- Extract the location they want parking near
- Return JSON: {"type": "parking", "location": "location_name"}

Always respond with valid JSON only. No other text."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"

    def understand_query(self, user_message: str) -> dict:
        """Parse user message and extract intent and parameters.
        
        Returns dict with:
        - type: "departures" or "parking"
        - location or stop: the query target
        - Other relevant fields
        """
        LOGGER.debug(f"Processing user query: {user_message}")

        response_text = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            response_text = response.choices[0].message.content or ""
            response_text = response_text.strip()
            LOGGER.debug(f"OpenAI response: {response_text}")

            # Parse JSON response
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError:
            LOGGER.error(f"Failed to parse OpenAI response as JSON: {response_text}")
            return {"type": "unknown", "error": "Could not understand query"}
        except Exception as e:
            LOGGER.exception(f"OpenAI API error: {e}")
            raise

    def generate_response(
        self, query: str, data: dict, context: str = ""
    ) -> str:
        """Generate a natural language response based on data retrieved.
        
        Args:
            query: Original user query
            data: Data returned from API (departures, parking, etc.)
            context: Additional context about what was searched
            
        Returns:
            Natural language response
        """
        LOGGER.debug(f"Generating response for query: {query}")

        prompt = f"""Based on this Melbourne transit/parking data, provide a helpful natural response to the user's question.

User question: {query}

Search context: {context}

Data retrieved: {json.dumps(data, default=str)[:1000]}

Provide a concise, friendly response in 1-3 sentences."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )

            response_text = response.choices[0].message.content or ""
            response_text = response_text.strip()
            LOGGER.debug(f"Generated response: {response_text}")
            return response_text

        except Exception as e:
            LOGGER.exception(f"OpenAI generation error: {e}")
            return "I couldn't generate a response. Please try again."
