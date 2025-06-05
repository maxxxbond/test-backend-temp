from typing import Optional, Dict, Any, List
from supabase import Client
# from app.core.security import get_password_hash, verify_password
from app.schemas.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, client: Client):
        self.client = client
        self.table = "users"

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User data or None if not found
        """
        response = self.client.table(self.table).select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.
        
        Args:
            email: The user's email
            
        Returns:
            User data or None if not found
        """
        response = self.client.table(self.table).select("*").eq("email", email).execute()
        return response.data[0] if response.data else None

    # async def create(self, user_in: UserCreate) -> Dict[str, Any]:
    #     """
    #     Create a new user.
        
    #     Args:
    #         user_in: User creation data
            
    #     Returns:
    #         Created user data
    #     """
    #     user_data = user_in.dict()
    #     hashed_password = get_password_hash(user_data.pop("password"))
    #     user_data["password"] = hashed_password
        
    #     response = self.client.table(self.table).insert(user_data).execute()
    #     return response.data[0] if response.data else None

    # async def update(self, user_id: str, user_in: UserUpdate) -> Optional[Dict[str, Any]]:
    #     """
    #     Update a user.
        
    #     Args:
    #         user_id: ID of the user to update
    #         user_in: User update data
            
    #     Returns:
    #         Updated user data or None if not found
    #     """
    #     update_data = user_in.dict(exclude_unset=True)
        
    #     # If password is provided, hash it
    #     if "password" in update_data and update_data["password"]:
    #         update_data["password"] = get_password_hash(update_data["password"])
        
    #     response = self.client.table(self.table).update(update_data).eq("id", user_id).execute()
    #     return response.data[0] if response.data else None

    # async def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
    #     """
    #     Authenticate a user.
        
    #     Args:
    #         email: User email
    #         password: User password
            
    #     Returns:
    #         Authenticated user data or None if authentication fails
    #     """
    #     user = await self.get_by_email(email)
    #     if not user:
    #         return None
    #     if not verify_password(password, user["password"]):
    #         return None
    #     return user
