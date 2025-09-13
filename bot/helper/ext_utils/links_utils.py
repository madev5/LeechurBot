from re import match as re_match
from os import path as ospath, access, W_OK

from bot.core.config_manager import Config


def is_magnet(url: str):
    return bool(re_match(r"^magnet:\?.*xt=urn:(btih|btmh):([a-zA-Z0-9]{32,40}|[a-z2-7]{32}).*", url))


def is_url(url: str):
    return bool(
        re_match(
            r"^(?!\/)(rtmps?:\/\/|mms:\/\/|rtsp:\/\/|https?:\/\/|ftp:\/\/)?([^\/:]+:[^\/@]+@)?(www\.)?(?=[^\/:\s]+\.[^\/:\s]+)([^\/:\s]+\.[^\/:\s]+)(:\d+)?(\/[^#\s]*[\s\S]*)?(\?[^#\s]*)?(#.*)?$",
            url,
        )
    )


def is_gdrive_link(url: str):
    return "drive.google.com" in url or "drive.usercontent.google.com" in url


def is_telegram_link(url: str):
    return url.startswith(("https://t.me/", "tg://openmessage?user_id="))


def is_share_link(url: str):
    return bool(
        re_match(
            r"https?:\/\/.+\.gdtot\.\S+|https?:\/\/(filepress|filebee|appdrive|gdflix)\.\S+",
            url,
        )
    )


def is_rclone_path(path: str):
    """
    Check if a path is a valid rclone path or local path.
    Supports: 
    - Regular rclone paths: remote:path
    - User rclone paths: mrcc:remote:path  
    - Local paths: local:/absolute/path
    - Special values: rcl
    """
    return bool(
        re_match(
            r"^(mrcc:)?(?!(magnet:|mtp:|sa:|tp:))(?![- ])[a-zA-Z0-9_\. -]+(?<! ):(?!.*\/\/).*$|^rcl$|^local:\/.*$",
            path,
        )
    )


def is_local_path(path: str):
    """
    Check if a path is a local path (starts with local:)
    Case-sensitive to ensure security.
    """
    return path.startswith("local:")


def get_local_path(destination: str):
    """
    Extract and resolve the actual local path from local: destination.
    
    Uses LOCAL_STORAGE_PATH environment variable as base directory for relative paths.
    Examples:
    - local:myfolder -> LOCAL_STORAGE_PATH/myfolder (if LOCAL_STORAGE_PATH is set)
    - local:/absolute/path -> /absolute/path (absolute paths used as-is)
    - local:myfolder -> ./myfolder (if LOCAL_STORAGE_PATH is not set - backward compatibility)
    
    Args:
        destination: String in format "local:path"
        
    Returns:
        Resolved absolute path or None if invalid format
    """
    if not is_local_path(destination):
        return None
        
    # Extract the path part after "local:"
    local_path = destination.split("local:", 1)[1]
    
    if not local_path:
        return None
    
    # If path is absolute, use it as-is (but warn for Docker users in calling code)
    if ospath.isabs(local_path):
        return local_path
    
    # For relative paths, use LOCAL_STORAGE_PATH as base if configured
    base_path = Config.LOCAL_STORAGE_PATH.strip() if Config.LOCAL_STORAGE_PATH else ""
    
    if base_path:
        # Use configured base path for relative paths
        return ospath.join(base_path, local_path)
    else:
        # Backward compatibility: use current directory as base
        return ospath.abspath(local_path)


def validate_local_path(path: str):
    """
    Validate if a local path exists and is writable.
    Returns tuple (is_valid, error_message)
    """
    if not path:
        return False, "Empty path provided"
    
    # Reject relative paths for security
    if not ospath.isabs(path):
        return False, f"Path must be absolute, got relative path: {path}"
    
    # Convert to absolute path and normalize
    abs_path = ospath.abspath(ospath.normpath(path))
    
    # Check if the path exists
    if not ospath.exists(abs_path):
        # Check if parent directory exists and is writable (for creating new directories)
        parent_dir = ospath.dirname(abs_path)
        if not ospath.exists(parent_dir):
            return False, f"Parent directory does not exist: {parent_dir}"
        if not ospath.isdir(parent_dir):
            return False, f"Parent path is not a directory: {parent_dir}"
        if not access(parent_dir, W_OK):
            return False, f"Parent directory is not writable: {parent_dir}"
        return True, ""  # Path is valid for creation
    
    # Path exists, check if it's a directory and writable
    if not ospath.isdir(abs_path):
        return False, f"Path exists but is not a directory: {abs_path}"
    
    if not access(abs_path, W_OK):
        return False, f"Directory is not writable: {abs_path}"
    
    return True, ""


def is_gdrive_id(id_: str):
    return bool(
        re_match(
            r"^(tp:|sa:|mtp:)?(?:[a-zA-Z0-9-_]{33}|[a-zA-Z0-9_-]{19})$|^gdl$|^(tp:|mtp:)?root$",
            id_,
        )
    )
