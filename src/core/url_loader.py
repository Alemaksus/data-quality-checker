"""
URL Loader - Download and process files from URLs.

Supports downloading CSV, JSON, and XML files from HTTP/HTTPS URLs.
"""

import requests
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
import tempfile
import os


async def download_file_from_url(url: str, timeout: int = 30) -> Path:
    """
    Download a file from URL and save it to a temporary file.
    
    Args:
        url: HTTP/HTTPS URL to download from
        timeout: Request timeout in seconds
        
    Returns:
        Path to temporary file
        
    Raises:
        HTTPException if download fails
    """
    # Validate URL scheme
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL scheme. Only HTTP/HTTPS URLs are supported. Got: {url[:20]}..."
        )
    
    try:
        # Download file with timeout
        response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check content type (optional, but helpful)
        content_type = response.headers.get('content-type', '').lower()
        if 'text/csv' not in content_type and 'application/json' not in content_type and 'text/xml' not in content_type:
            # Allow if content-type is not set (some servers don't set it)
            if content_type and 'text' not in content_type and 'application' not in content_type:
                # Not a blocking error, just a warning
                pass
        
        # Determine file extension from URL or Content-Type
        filename = None
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"\'')
        
        if not filename:
            # Try to get from URL
            filename = url.split('/')[-1].split('?')[0]  # Remove query params
        
        # Determine extension from filename or content-type
        if '.' not in filename or len(filename.split('.')[-1]) > 5:
            # No extension or weird extension, try content-type
            if 'csv' in content_type:
                extension = '.csv'
            elif 'json' in content_type:
                extension = '.json'
            elif 'xml' in content_type:
                extension = '.xml'
            else:
                # Default to CSV for data files
                extension = '.csv'
            
            if '.' not in filename:
                filename = f"downloaded_file{extension}"
            else:
                filename = filename.rsplit('.', 1)[0] + extension
        
        # Create temporary file
        temp_dir = Path("tmp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / f"url_{os.urandom(8).hex()}_{filename}"
        
        # Save downloaded content
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Validate file size (max 100MB for safety)
        file_size = temp_file_path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB
        
        if file_size > max_size:
            temp_file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 100MB."
            )
        
        if file_size == 0:
            temp_file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Downloaded file is empty."
            )
        
        return temp_file_path
    
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail=f"Request timeout after {timeout} seconds. URL may be unreachable or file too large."
        )
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to URL. Check if the URL is accessible and the server is running."
        )
    
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code if hasattr(e, 'response') else 400,
            detail=f"HTTP error: {str(e)}"
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download file: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error downloading file: {str(e)}"
        )

