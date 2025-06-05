from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Any, List, Optional
import uuid
from datetime import datetime

from app.db.database import get_supabase_client
from app.schemas.schemas import Video, VideoCreate, VideoUpdate, User
from app.services.bunnycdn import BunnyCDNService
from app.api.endpoints.auth import get_current_user

router = APIRouter()
bunnycdn = BunnyCDNService()


@router.post("/", response_model=Video)
async def create_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    course_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload a new video.
    """
    # Generate a unique ID for the video
    video_id = str(uuid.uuid4())
    
    # Extract file extension
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
    file_name = f"{video_id}.{file_extension}"
    
    # Upload to BunnyCDN
    upload_result = bunnycdn.upload_video(file_name, file.file, "education")
    
    if not upload_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {upload_result['message']}",
        )
    
    # Create video data in Supabase
    video_data = {
        "id": video_id,
        "title": title,
        "description": description,
        "course_id": course_id,
        "url": upload_result["url"],
        "user_id": current_user.id,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # Insert into Supabase
    supabase = get_supabase_client()
    response = supabase.table("videos").insert(video_data).execute()
    
    if not response.data:
        # If insertion fails, try to delete the uploaded video
        bunnycdn.delete_video(file_name, "education")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video record",
        )
    
    return Video(**response.data[0])


@router.get("/", response_model=List[Video])
async def read_videos(
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve videos, optionally filtered by course_id.
    """
    supabase = get_supabase_client()
    query = supabase.table("videos").select("*").range(skip, skip + limit - 1)
    
    # Apply course_id filter if provided
    if course_id:
        query = query.eq("course_id", course_id)
    
    response = query.execute()
    
    return [Video(**item) for item in response.data]


@router.get("/{video_id}", response_model=Video)
async def read_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific video by ID.
    """
    supabase = get_supabase_client()
    response = supabase.table("videos").select("*").eq("id", video_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return Video(**response.data[0])


@router.put("/{video_id}", response_model=Video)
async def update_video(
    video_id: str,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a video's metadata.
    """
    # First, check if the video exists and belongs to the current user
    supabase = get_supabase_client()
    response = supabase.table("videos").select("*").eq("id", video_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = response.data[0]
    
    # Check if the video belongs to the current user (or is superuser)
    if video["user_id"] != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Prepare update data
    update_data = video_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    # Update in Supabase
    response = supabase.table("videos").update(update_data).eq("id", video_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update video")
    
    return Video(**response.data[0])


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a video.
    """
    # First, check if the video exists and belongs to the current user
    supabase = get_supabase_client()
    response = supabase.table("videos").select("*").eq("id", video_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = response.data[0]
    
    # Check if the video belongs to the current user (or is superuser)
    if video["user_id"] != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Extract the filename from the URL
    url_parts = video["url"].split("/")
    file_name = url_parts[-1]
    folder = url_parts[-2] if len(url_parts) > 2 else ""
    
    # Delete from BunnyCDN
    delete_result = bunnycdn.delete_video(file_name, folder)
    
    # Delete from Supabase (even if BunnyCDN delete fails)
    supabase.table("videos").delete().eq("id", video_id).execute()
    
    # Return no content
    return None
