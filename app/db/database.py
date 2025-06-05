from supabase import create_client
from app.core.config import settings

def get_supabase_client():
    """
    Create and return a Supabase client instance.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# Example of a basic database utility function
async def fetch_data(table_name: str, query=None):
    """
    Fetch data from a specific Supabase table with optional query parameters.
    
    Args:
        table_name: The name of the table to query
        query: Optional query function to apply to the request
    
    Returns:
        The query results
    """
    client = get_supabase_client()
    
    base_query = client.table(table_name).select("*")
    
    if query:
        return query(base_query).execute()
    
    return base_query.execute()
