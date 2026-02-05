"""
Supabase Storage helper for file uploads
"""
import os
import uuid
from typing import Optional, BinaryIO
from pathlib import Path
from supabase import Client

from . import config


def generate_filename(listing_id: str, original_filename: str) -> str:
    """
    Generate a unique filename for storage
    Format: listing_id/uuid_original_extension
    """
    # Extract file extension
    extension = Path(original_filename).suffix.lower()
    # Generate unique ID
    unique_id = str(uuid.uuid4())
    # Combine: listing_id/uuid.ext
    return f"{listing_id}/{unique_id}{extension}"


def upload_file(
    supabase: Client,
    bucket_name: str,
    file_path: str,
    file_content: BinaryIO,
    content_type: str = "image/jpeg"
) -> Optional[str]:
    """
    Upload a file to Supabase Storage
    
    Args:
        supabase: Supabase client
        bucket_name: Name of the storage bucket
        file_path: Path within the bucket (e.g., "listing_id/filename.jpg")
        file_content: File content as bytes or file-like object
        content_type: MIME type of the file
    
    Returns:
        Public URL of the uploaded file, or None on failure
    """
    try:
        # Upload file to storage
        result = supabase.storage.from_(bucket_name).upload(
            file_path,
            file_content,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        
        return public_url
    
    except Exception as e:
        print(f"Error uploading file to Supabase Storage: {e}")
        return None


def delete_file(supabase: Client, bucket_name: str, file_path: str) -> bool:
    """
    Delete a file from Supabase Storage
    
    Args:
        supabase: Supabase client
        bucket_name: Name of the storage bucket
        file_path: Path within the bucket
    
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting file from Supabase Storage: {e}")
        return False


def get_content_type(filename: str) -> str:
    """
    Determine content type based on file extension
    """
    extension = Path(filename).suffix.lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf"
    }
    return content_types.get(extension, "application/octet-stream")


def extract_storage_path(url: str, bucket_name: str) -> Optional[str]:
    """
    Extract the storage path from a Supabase public URL
    
    Args:
        url: Full public URL
        bucket_name: Name of the bucket
    
    Returns:
        Storage path (e.g., "listing_id/filename.jpg") or None
    """
    try:
        # URL format: https://PROJECT.supabase.co/storage/v1/object/public/BUCKET/PATH
        parts = url.split(f"/storage/v1/object/public/{bucket_name}/")
        if len(parts) == 2:
            return parts[1]
        return None
    except Exception:
        return None
