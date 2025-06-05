from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from supabase import Client

from app.schemas.schemas import User, UserCreate, UserUpdate
from app.services.users import UserService
from app.api.deps import get_db
from app.api.endpoints.auth import get_current_active_superuser, get_current_user

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Only for superusers.
    """
    response = db.table("users").select("*").range(skip, skip + limit - 1).execute()
    return [User(**item) for item in response.data]


@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new user. Only for superusers.
    """
    user_service = UserService(db)
    
    # Check if user with this email already exists
    user = await user_service.get_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Create new user
    user = await user_service.create(user_in)
    return User(**user)


@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update current user.
    """
    user_service = UserService(db)
    updated_user = await user_service.update(current_user.id, user_in)
    return User(**updated_user)


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get a specific user by id. Only for superusers.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return User(**user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user. Only for superusers.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    updated_user = await user_service.update(user_id, user_in)
    return User(**updated_user)
