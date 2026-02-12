"""Per-session rate limiter — adapted from TG bot."""
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Limits sessions to a max number of messages per time window."""

    def __init__(self, max_requests=10, window_seconds=30):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {session_id: [timestamp, ...]}
        self._cleanup_counter = 0

    def is_allowed(self, session_id):
        """Returns True if session is within rate limit, False if throttled."""
        now = time.time()
        if session_id not in self.requests:
            self.requests[session_id] = []

        # Remove old timestamps outside the window
        self.requests[session_id] = [
            t for t in self.requests[session_id]
            if now - t < self.window_seconds
        ]

        if len(self.requests[session_id]) >= self.max_requests:
            logger.warning(f"Rate limited session {session_id[:8]}...")
            return False

        self.requests[session_id].append(now)
        
        # Periodic cleanup of stale sessions
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup()
            self._cleanup_counter = 0
        
        return True
    
    def _cleanup(self):
        """Remove sessions where all timestamps are older than window_seconds."""
        now = time.time()
        stale_sessions = [
            sid for sid, timestamps in self.requests.items()
            if not timestamps or all(now - t >= self.window_seconds for t in timestamps)
        ]
        for sid in stale_sessions:
            del self.requests[sid]
        
        if stale_sessions:
            logger.info(f"Cleaned up {len(stale_sessions)} stale rate limiter sessions")
