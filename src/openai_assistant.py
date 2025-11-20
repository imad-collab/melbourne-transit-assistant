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


class TextAnalyzer:
    """Uses OpenAI to analyze and understand text."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"

    def summarize(self, text: str, max_tokens: int = 150) -> str:
        """Summarize the given text."""
        LOGGER.debug(f"Summarizing text ({len(text)} chars)")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes text concisely. Provide only the summary, no extra text.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this text in 2-3 sentences:\n\n{text}",
                    },
                ],
                temperature=0.5,
                max_tokens=max_tokens,
            )

            summary = response.choices[0].message.content or ""
            LOGGER.info(f"Summary generated: {len(summary)} chars")
            return summary.strip()

        except Exception as e:
            LOGGER.exception(f"Summarization error: {e}")
            return "Could not summarize text. Please try again."

    def extract_key_points(self, text: str) -> list:
        """Extract key points from the text."""
        LOGGER.debug(f"Extracting key points from text ({len(text)} chars)")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts key points from text. Return only the key points as a numbered list, one per line.",
                    },
                    {
                        "role": "user",
                        "content": f"Extract the 3-5 most important key points from this text:\n\n{text}",
                    },
                ],
                temperature=0.5,
                max_tokens=200,
            )

            points_text = response.choices[0].message.content or ""
            LOGGER.info(f"Key points extracted: {len(points_text)} chars")
            return points_text.strip().split("\n")

        except Exception as e:
            LOGGER.exception(f"Key point extraction error: {e}")
            return ["Could not extract key points."]

    def sentiment_analysis(self, text: str) -> dict:
        """Analyze the sentiment of the text."""
        LOGGER.debug(f"Analyzing sentiment ({len(text)} chars)")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. Analyze the sentiment and respond with only: POSITIVE, NEGATIVE, or NEUTRAL, followed by a brief explanation (1-2 sentences).",
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of this text:\n\n{text}",
                    },
                ],
                temperature=0.3,
                max_tokens=100,
            )

            sentiment_text = response.choices[0].message.content or ""
            sentiment_text = sentiment_text.strip()

            # Parse sentiment
            sentiment = "NEUTRAL"
            if "POSITIVE" in sentiment_text.upper():
                sentiment = "POSITIVE"
            elif "NEGATIVE" in sentiment_text.upper():
                sentiment = "NEGATIVE"

            LOGGER.info(f"Sentiment: {sentiment}")
            return {"sentiment": sentiment, "analysis": sentiment_text}

        except Exception as e:
            LOGGER.exception(f"Sentiment analysis error: {e}")
            return {
                "sentiment": "UNKNOWN",
                "analysis": "Could not analyze sentiment.",
            }

    def answer_question(self, text: str, question: str) -> str:
        """Answer a question about the given text."""
        LOGGER.debug(f"Answering question about text ({len(text)} chars)")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Answer questions based on the provided text. If the answer is not in the text, say so.",
                    },
                    {
                        "role": "user",
                        "content": f"Based on this text:\n\n{text}\n\nAnswer this question: {question}",
                    },
                ],
                temperature=0.5,
                max_tokens=200,
            )

            answer = response.choices[0].message.content or ""
            LOGGER.info(f"Answer generated: {len(answer)} chars")
            return answer.strip()

        except Exception as e:
            LOGGER.exception(f"Question answering error: {e}")
            return "Could not answer the question. Please try again."

    def analyze_all(self, text: str) -> dict:
        """Perform comprehensive analysis on the text."""
        LOGGER.info(f"Performing comprehensive analysis ({len(text)} chars)")

        return {
            "summary": self.summarize(text),
            "key_points": self.extract_key_points(text),
            "sentiment": self.sentiment_analysis(text),
        }


class InputValidator:
    """Validates user input using AI and generates enhanced output."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"

    def validate_input(self, user_input: str, context: str = "general") -> dict:
        """Validate user input and return assessment.
        
        Args:
            user_input: The user's raw input text
            context: Context for validation (general, parking, transit, etc.)
            
        Returns:
            {
                "is_valid": bool,
                "is_safe": bool,
                "reason": str,
                "suggestions": str,
                "confidence": float (0-1)
            }
        """
        LOGGER.info(f"Validating input ({len(user_input)} chars) in context: {context}")

        system_prompt = f"""You are an input validation assistant. Analyze the user input and validate it.
        
Context: {context}

Check for:
1. Is the input meaningful and not spam?
2. Is it safe and appropriate?
3. Can it be processed by the system?

Respond with ONLY valid JSON:
{{
    "is_valid": true/false,
    "is_safe": true/false,
    "reason": "brief reason",
    "suggestions": "suggestions for improvement or alternative phrasing",
    "confidence": 0.0-1.0
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Validate this input: '{user_input}'"},
                ],
                temperature=0.5,
                max_tokens=200,
            )

            response_text = response.choices[0].message.content
            if response_text:
                response_text = response_text.strip()
            else:
                raise ValueError("Empty response from API")

            # Parse JSON response
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError as e:
            LOGGER.error(f"Failed to parse validation response: {e}")
            return {
                "is_valid": True,  # Default to valid if can't parse
                "is_safe": True,
                "reason": "Could not validate, allowing by default",
                "suggestions": "",
                "confidence": 0.3,
            }
        except Exception as e:
            LOGGER.exception(f"Input validation error: {e}")
            return {
                "is_valid": True,
                "is_safe": True,
                "reason": "Validation service error",
                "suggestions": "",
                "confidence": 0.0,
            }

    def generate_response(self, input_text: str, analysis_result: dict) -> str:
        """Generate an enhanced response based on the analysis.
        
        Args:
            input_text: Original user input
            analysis_result: Result from validate_input()
            
        Returns:
            Enhanced response string
        """
        LOGGER.info("Generating enhanced response")

        if not analysis_result.get("is_valid"):
            return f"""❌ Input could not be processed.

**Reason:** {analysis_result.get('reason', 'Invalid input')}

**Suggestions:** {analysis_result.get('suggestions', 'Please rephrase your input')}"""

        if not analysis_result.get("is_safe"):
            return f"""⚠️ Input flagged as unsafe.

**Reason:** {analysis_result.get('reason', 'Inappropriate content')}

Please provide a different input."""

        # Generate constructive response
        system_prompt = f"""You are a helpful assistant. The user's input was validated and approved.
Their input: '{input_text}'

Generate a friendly, constructive response acknowledging their input and suggesting what to do next.
Keep it concise (2-3 sentences)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text},
                ],
                temperature=0.7,
                max_tokens=150,
            )

            response_content = response.choices[0].message.content
            if response_content:
                return response_content.strip()
            return "✓ Input received. Processing your request..."

        except Exception as e:
            LOGGER.exception(f"Response generation error: {e}")
            return "✓ Input received. Processing your request..."

    def validate_and_respond(self, user_input: str, context: str = "general") -> dict:
        """Complete pipeline: validate input and generate response.
        
        Returns:
            {
                "validation": {...validation result...},
                "response": "formatted response",
                "should_process": bool (True if valid and safe)
            }
        """
        LOGGER.info(f"Running complete validation pipeline for: {user_input[:50]}...")

        # Validate input
        validation = self.validate_input(user_input, context)

        # Generate response
        response_text = self.generate_response(user_input, validation)

        # Decide if system should process this
        should_process = validation.get("is_valid", True) and validation.get("is_safe", True)

        return {
            "validation": validation,
            "response": response_text,
            "should_process": should_process,
        }
