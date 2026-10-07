# Smart Downloads Organizer

A self-learning background assistant that watches your `Downloads` folder and automatically sorts files into the correct folders on your computer.

## How It Works

1. **Maps your folders** — Recursively scans your directories (Documents, Desktop, A:\, D:\, etc.) and builds a mathematical profile of what each folder contains using TF-IDF vectorization.

2. **Watches Downloads** — Runs silently in the background, detecting new files the moment they finish downloading.

3. **Analyzes files** — Extracts text from PDFs, Word docs, PowerPoint, Excel, code files, and more. Also uses the filename as a strong signal.

4. **Finds best match** — Compares the new file against every folder on your system using cosine similarity.

5. **Moves or keeps** — If the best match score exceeds the threshold, the file is moved. Otherwise, it stays in Downloads.

## Your Specific Case

```
A:\5th sem material\flat\flat pvqs\
```

When you download `FLAT_Previous_Year_2023.pdf`:
- The system detects keywords: "FLAT", "Previous", "Year", "2023"
- It finds `A:\5th sem material\flat\flat pvqs` has high similarity
- File is moved there automatically within seconds

## Installation

### 1. Install Python
Make sure Python 3.8+ is installed: https://python.org

### 2. Install Dependencies
```bash
cd downloads-organizer
pip install -r requirements.txt
```

### 3. Configure
Edit `config.py` to set your paths:
```python
DOWNLOADS_DIR = os.path.expanduser("~\\Downloads")
SCAN_ROOTS = [
    "A:\\",  # Your 5th sem material drive
    "D:\\",
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Desktop"),
]
MOVE_THRESHOLD = 0.15  # Adjust based on results
```

## Usage

### Run in Foreground (for testing)
```bash
python organizer.py
```

### Run in Background (double-click)
- **With console window**: Double-click `start_background.bat`
- **Silent (no window)**: Double-click `start_silent.vbs`

### Run as Windows Service (auto-start on boot)
See `SERVICE.md` for instructions on setting up as a Windows service.

## Testing

Run the test suite to verify matching works:
```bash
python test_organizer.py
```

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `DOWNLOADS_DIR` | `~/Downloads` | Folder to watch |
| `SCAN_ROOTS` | See config.py | Directories to scan for folder map |
| `MOVE_THRESHOLD` | `0.15` | Minimum score to auto-move (0.0–1.0) |
| `DOWNLOAD_SETTLE_TIME` | `2.0` | Seconds to wait before processing |
| `MAP_REFRESH_INTERVAL` | `300` | Seconds between map refreshes |
| `EXCLUDE_DIRS` | System folders | Directories to skip during scan |

## Supported File Types

**Text extraction** (content analyzed):
- PDF, DOCX, PPTX, XLSX, TXT, MD, CSV
- Code files: PY, JS, TS, JAVA, CPP, C, CS, HTML, CSS, JSON, XML, YAML
- EPUB

**Filename-only matching** (no content extraction):
- Videos: MP4, MKV, AVI, MOV
- Audio: MP3, WAV, FLAC
- Images: JPG, PNG, GIF, SVG
- Archives: ZIP, RAR, 7Z
- Installers: EXE, MSI, APK

## How to Tune

### If files are moved to wrong folders:
- **Increase** `MOVE_THRESHOLD` (e.g., 0.20, 0.25)
- Add more descriptive files to the target folders

### If files are NOT being moved:
- **Decrease** `MOVE_THRESHOLD` (e.g., 0.10, 0.08)
- Make sure the target folder is inside a `SCAN_ROOTS` directory
- Check `organizer.log` for match scores

### To improve matching accuracy:
- Keep folder names descriptive (e.g., `flat pvqs` is better than `folder1`)
- Have at least 3-5 files in each folder for better profiling
- Use consistent naming conventions

## Logs

Check `organizer.log` for detailed information about:
- Folder map building
- File detection and analysis
- Match scores and decisions
- Move operations

## Project Structure

```
downloads-organizer/
├── config.py           # Configuration settings
├── folder_mapper.py     # Folder scanning and TF-IDF mapping
├── file_analyzer.py    # Text extraction from files
├── organizer.py        # Main watcher and file mover
├── test_organizer.py   # Test suite
├── requirements.txt    # Python dependencies
├── start_background.bat # Background launcher (with console)
├── start_silent.vbs    # Silent background launcher
├── organizer.log       # Runtime log (created on first run)
└── README.md           # This file
```
