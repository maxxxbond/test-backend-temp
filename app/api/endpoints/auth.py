from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Any

from app.core.config import settings
from app.db.database import get_supabase_client
from app.schemas.schemas import User, Token, TokenPayload

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate and decode the Supabase JWT token to get the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        supabase_user = user_response.user

        if not supabase_user:
            raise credentials_exception
        
        
        user_id = supabase_user.id
        email = supabase_user.email or ""
        full_name = (
            supabase_user.user_metadata.get("full_name", "")
            if supabase_user.user_metadata else ""
        )
        created_at = supabase_user.created_at.isoformat() if supabase_user.created_at else None
        updated_at = supabase_user.updated_at.isoformat() or created_at

        try:
            user_check = supabase.table("users").select("*").eq("id", user_id).execute()
            if not user_check.data:
                # User doesn't exist in the users table, create them
                new_user = {
                    "id": user_id,
                    "created_at": created_at
                }
                supabase.table("users").insert(new_user).execute()
        except Exception as e:
            print(f"Error ensuring user exists in database: {str(e)}")

        return User(
            id=user_id,
            email=email,
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            created_at=supabase_user.created_at,
            updated_at=supabase_user.updated_at or supabase_user.created_at,
        )

    except Exception:
        raise credentials_exception


async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Check if the current user is a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user.
    """
    return current_user
