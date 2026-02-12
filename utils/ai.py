"""Groq AI client — same logic as TG bot, adapted for web."""
import asyncio
import logging
from groq import Groq
from config import settings
from utils.prompts import SYSTEM_PROMPT, HUMAN_CHAT_PROMPT

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


async def ask_ai_free(prompt, human_mode=False, history=None):
    """Get AI response using Groq's free tier with retry for rate limits.
    
    Args:
        prompt: The user's message/prompt
        human_mode: If True, uses HUMAN_CHAT_PROMPT instead of SYSTEM_PROMPT
        history: Optional list of {"role": ..., "content": ...} dicts for conversation history
    """
    if not groq_client:
        return "AI system is not configured. Please contact support."

    system = HUMAN_CHAT_PROMPT if human_mode else SYSTEM_PROMPT

    for attempt in range(3):
        try:
            # Build messages list
            messages = [{"role": "system", "content": system}]
            
            # Add conversation history if provided
            if history:
                messages.extend(history)
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt or ""})
            
            # Call Groq API in a thread pool to avoid blocking the event loop
            response = await asyncio.to_thread(
                groq_client.chat.completions.create,
                model="llama-3.1-8b-instant",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            if "rate_limit" in error_msg or "429" in error_msg:
                wait = 2 ** attempt
                logger.warning(f"AI rate limited, retrying in {wait}s (attempt {attempt + 1}/3)")
                await asyncio.sleep(wait)
                continue
            logger.error(f"AI API error: {e}")
            return "AI system is unavailable right now. Please try again shortly."

    return "AI system is temporarily busy. Please try again in a moment."
