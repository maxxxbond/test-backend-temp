import requests
from typing import Optional, Dict, Any, BinaryIO
from app.core.config import settings

class BunnyCDNService:
    def __init__(self):
        self.api_key = settings.BUNNYCDN_API_KEY
        self.storage_zone = settings.BUNNYCDN_STORAGE_ZONE
        self.pull_zone = settings.BUNNYCDN_PULL_ZONE
        self.storage_url = f"https://storage.bunnycdn.com/{self.storage_zone}"
        self.headers = {
            "AccessKey": self.api_key,
            "Content-Type": "application/json"
        }

    def upload_video(self, file_path: str, file_object: BinaryIO, folder_path: Optional[str] = "") -> Dict[str, Any]:
        """
        Upload a video file to BunnyCDN storage.
        
        Args:
            file_path: The path/name for the file in BunnyCDN storage
            file_object: The file object to upload
            folder_path: Optional folder path within the storage zone
            
        Returns:
            Response from the BunnyCDN API
        """
        upload_url = f"{self.storage_url}/{folder_path}/{file_path}"
        
        # Set binary content type header
        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"
        
        response = requests.put(upload_url, data=file_object, headers=headers)
        
        if response.status_code in (200, 201):
            # Return the URL to the uploaded video
            return {
                "success": True,
                "url": f"https://{self.pull_zone}.b-cdn.net/{folder_path}/{file_path}",
                "message": "Upload successful"
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": response.text
            }

    def delete_video(self, file_path: str, folder_path: Optional[str] = "") -> Dict[str, Any]:
        """
        Delete a video file from BunnyCDN storage.
        
        Args:
            file_path: The path/name of the file to delete
            folder_path: Optional folder path within the storage zone
            
        Returns:
            Response from the BunnyCDN API
        """
        delete_url = f"{self.storage_url}/{folder_path}/{file_path}"
        
        response = requests.delete(delete_url, headers=self.headers)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Video deleted successfully"
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": response.text
            }

    def get_video_info(self, file_path: str, folder_path: Optional[str] = "") -> Dict[str, Any]:
        """
        Get information about a video file in BunnyCDN storage.
        
        Args:
            file_path: The path/name of the file
            folder_path: Optional folder path within the storage zone
            
        Returns:
            Response from the BunnyCDN API with file information
        """
        info_url = f"{self.storage_url}/{folder_path}/{file_path}"
        
        response = requests.get(info_url, headers=self.headers)
        
        if response.status_code == 200:
            return {
                "success": True,
                "file_info": response.json(),
                "streaming_url": f"https://{self.pull_zone}.b-cdn.net/{folder_path}/{file_path}"
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": response.text
            }
