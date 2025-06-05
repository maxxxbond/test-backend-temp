from datetime import datetime, timezone

def get_current_time():
    """Return current time in UTC with timezone information as ISO format string."""
    return datetime.now(timezone.utc).isoformat()
