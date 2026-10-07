"""
Configuration for the Smart Downloads Organizer.
Edit these values to match your system.
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────────

# Folder to watch for new downloads
DOWNLOADS_DIR = os.path.expanduser("~\\Downloads")

# Root directories to scan for building the folder map
# Add all drives/folders where you keep organized content
SCAN_ROOTS = [
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\OneDrive\\Desktop"),
    os.path.expanduser("~\\OneDrive\\Documents"),
    "A:\\",  # Your A drive with 5th sem material etc.
    "D:\\",
    "E:\\",
]

# Folders to explicitly exclude from scanning (system folders, etc.)
EXCLUDE_DIRS = {
    "Windows", "Program Files", "Program Files (x86)", "ProgramData",
    "$Recycle.Bin", "System Volume Information", "node_modules",
    ".git", "__pycache__", ".venv", "venv", "AppData",
    "Recovery", "OneDriveTemp", "Temporary Internet Files",
}

# ── Matching Thresholds ──────────────────────────────────────────────────────

# Minimum similarity score (0.0 to 1.0) to auto-move a file.
# If best match is below this, file stays in Downloads.
# Start with 0.15 and tune based on results.
MOVE_THRESHOLD = 0.15

# Minimum similarity to even consider a folder as a candidate
CANDIDATE_THRESHOLD = 0.05

# ── File Type Support ─────────────────────────────────────────────────────────

# Extensions we know how to extract text from
TEXT_EXTENSIONS = {
    # Documents
    ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md",
    # Notes & code
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs",
    ".html", ".css", ".json", ".xml", ".yaml", ".yml",
    # Presentations
    ".pptx", ".ppt", ".key",
    # Spreadsheets
    ".xlsx", ".xls", ".csv",
    # Ebooks
    ".epub", ".mobi",
}

# Extensions we can only use filename for (no text extraction)
FILENAME_ONLY_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv",  # Videos
    ".mp3", ".wav", ".flac", ".aac", ".ogg",   # Audio
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",  # Images
    ".zip", ".rar", ".7z", ".tar", ".gz",      # Archives
    ".exe", ".msi", ".dmg", ".apk",            # Installers
    ".iso", ".img",                            # Disk images
    ".ttf", ".otf", ".woff", ".woff2",         # Fonts
}

# ── Watcher Settings ──────────────────────────────────────────────────────────

# Seconds to wait after file appears before processing
# (ensures download is complete)
DOWNLOAD_SETTLE_TIME = 2.0

# How often to re-scan and update the folder map (in seconds)
MAP_REFRESH_INTERVAL = 300  # 5 minutes

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_FILE = os.path.join(os.path.dirname(__file__), "organizer.log")
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
