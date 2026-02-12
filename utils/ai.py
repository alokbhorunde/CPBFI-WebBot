"""Groq AI client — same logic as TG bot, adapted for web."""
import time
import logging
from groq import Groq
from config import settings
from utils.prompts import SYSTEM_PROMPT, HUMAN_CHAT_PROMPT

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def ask_ai_free(prompt, human_mode=False):
    """Get AI response using Groq's free tier with retry for rate limits."""
    if not groq_client:
        return "AI system is not configured. Please contact support."

    system = HUMAN_CHAT_PROMPT if human_mode else SYSTEM_PROMPT

    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt or ""}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            if "rate_limit" in error_msg or "429" in error_msg:
                wait = 2 ** attempt
                logger.warning(f"AI rate limited, retrying in {wait}s (attempt {attempt + 1}/3)")
                time.sleep(wait)
                continue
            logger.error(f"AI API error: {e}")
            return "AI system is unavailable right now. Please try again shortly."

    return "AI system is temporarily busy. Please try again in a moment."
