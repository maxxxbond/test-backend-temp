from typing import Generator
from supabase import Client

from app.db.database import get_supabase_client


def get_db() -> Generator[Client, None, None]:
    """
    Dependency to get Supabase client for database access.
    
    Yields:
        Supabase client: Client for database operations
    """
    client = get_supabase_client()
    try:
        yield client
    finally:
        pass
