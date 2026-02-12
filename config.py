"""Application configuration — validated from .env file."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """App settings loaded from environment variables."""

    # --- Required ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # --- Email (required for escalation) ---
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD: str = os.getenv("SENDER_PASSWORD", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    RECEIVER_EMAIL: str = os.getenv("RECEIVER_EMAIL", "")

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chatbot.db")

    # --- Admin ---
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "changeme")

    # --- CORS ---
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # --- Server ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))

    def validate(self):
        """Check that critical settings are present."""
        missing = []
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if missing:
            print(f"⚠️  Missing env vars: {', '.join(missing)} — some features will be disabled.")
        
        # Warn about insecure admin key
        if not self.ADMIN_KEY or self.ADMIN_KEY == "changeme":
            print("⚠️  WARNING: ADMIN_KEY is not set or using default 'changeme' — admin endpoints are INSECURE!")
            print("   Please set a secure ADMIN_KEY in your .env file.")


settings = Settings()
