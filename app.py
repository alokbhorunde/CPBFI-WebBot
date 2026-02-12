"""FastAPI server entry — serves API + widget static files."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from config import settings
from db.database import init_db
from api.chat import router as chat_router
from api.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    settings.validate()
    await init_db()
    logger.info("Database initialized")
    logger.info(f"Server running on {settings.HOST}:{settings.PORT}")
    yield


app = FastAPI(
    title="CPBFI Web Chatbot",
    description="Helpdesk chatbot API — drop into any website via a single <script> tag",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(chat_router)
app.include_router(admin_router)

# Serve widget static files
app.mount("/widget", StaticFiles(directory="widget"), name="widget")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serves just the chatbot widget — no demo content."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPBFI Helpdesk</title>
    <style>
        body { margin: 0; min-height: 100vh; background: #fff; }
    </style>
</head>
<body>
    <script src="/widget/chatbot.js"></script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)
