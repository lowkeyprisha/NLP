"""
Smart Downloads Organizer — Main entry point.

Watches the Downloads folder, analyzes new files, and automatically
moves them to the best-matching folder based on the learned folder map.
"""

import os
import sys
import time
import shutil
import logging
import threading
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
from folder_mapper import FolderMapper
from file_analyzer import FileAnalyzer

# ── Logging Setup ──────────────────────────────────────────────────────────────

def setup_logging():
    """Configure logging to both file and console."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)


# ── Download Handler ──────────────────────────────────────────────────────────

class DownloadHandler(FileSystemEventHandler):
    """
    Watches the Downloads folder and processes new files.
    """

    def __init__(self, mapper: FolderMapper, analyzer: FileAnalyzer):
        self.mapper = mapper
        self.analyzer = analyzer
        self._processing = set()  # Track files being processed
        self._lock = threading.Lock()

    def on_created(self, event):
        """Called when a new file or directory is created."""
        if event.is_directory:
            return

        filepath = event.src_path

        # Ignore temporary download files
        if filepath.endswith((".crdownload", ".tmp", ".part", ".download")):
            return

        # Ignore our own log file
        if filepath == os.path.abspath(config.LOG_FILE):
            return

        # Wait for download to complete
        time.sleep(config.DOWNLOAD_SETTLE_TIME)

        # Check if file still exists (might have been a temp file)
        if not os.path.exists(filepath):
            return

        # Avoid double-processing
        with self._lock:
            if filepath in self._processing:
                return
            self._processing.add(filepath)

        try:
            self._process_file(filepath)
        finally:
            with self._lock:
                self._processing.discard(filepath)

    def on_moved(self, event):
        """Called when a file is moved into Downloads (e.g., from browser)."""
        if event.is_directory:
            return

        dest_path = event.dest_path
        if not os.path.exists(dest_path):
            return

        with self._lock:
            if dest_path in self._processing:
                return
            self._processing.add(dest_path)

        try:
            self._process_file(dest_path)
        finally:
            with self._lock:
                self._processing.discard(dest_path)

    def _process_file(self, filepath: str) -> None:
        """
        Analyze a downloaded file and move it to the best matching folder.
        """
        filename = os.path.basename(filepath)
        logger.info(f"New download detected: {filename}")

        # Build query text from the file
        query_text = self.analyzer.build_query_text(filepath)

        if not query_text.strip():
            logger.warning(f"  → Could not extract any features from: {filename}")
            logger.info(f"  → Leaving in Downloads (no content to match).")
            return

        # Find best matching folders
        matches = self.mapper.find_best_match(query_text, top_k=5)

        if not matches:
            logger.warning(f"  → No folder matches found for: {filename}")
            logger.info(f"  → Leaving in Downloads.")
            return

        # Log top matches
        logger.info(f"  Top matches:")
        for path, score in matches[:3]:
            display = self.mapper.get_folder_display_path(path)
            logger.info(f"    [{score:.4f}] {display}")

        # Check if best match exceeds threshold
        best_path, best_score = matches[0]

        if best_score >= config.MOVE_THRESHOLD:
            self._move_file(filepath, best_path, best_score)
        else:
            logger.info(f"  → Best match score {best_score:.4f} below threshold {config.MOVE_THRESHOLD}")
            logger.info(f"  → Leaving file in Downloads for manual organization.")

    def _move_file(self, filepath: str, dest_folder: str, score: float) -> None:
        """
        Move a file to the destination folder.
        Handles name collisions by appending a number.
        """
        filename = os.path.basename(filepath)
        dest_path = os.path.join(dest_folder, filename)

        # Handle name collision
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_folder, f"{base} ({counter}){ext}")
                counter += 1

        try:
            shutil.move(filepath, dest_path)
            logger.info(f"  ✓ MOVED to: {self.mapper.get_folder_display_path(dest_folder)}")
            logger.info(f"    Score: {score:.4f} | New path: {dest_path}")
        except Exception as e:
            logger.error(f"  ✗ Failed to move file: {e}")
            logger.info(f"  → File remains in Downloads.")


# ── Periodic Map Refresher ────────────────────────────────────────────────────

class MapRefresher(threading.Thread):
    """Periodically refreshes the folder map in the background."""

    def __init__(self, mapper: FolderMapper, interval: int):
        super().__init__(daemon=True)
        self.mapper = mapper
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(self.interval)
            if not self._stop_event.is_set():
                try:
                    self.mapper.refresh()
                except Exception as e:
                    logger.error(f"Error refreshing folder map: {e}")

    def stop(self):
        self._stop_event.set()


# ── Main Entry Point ──────────────────────────────────────────────────────────

def main():
    """Start the Smart Downloads Organizer."""
    setup_logging()

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       SMART DOWNLOADS ORGANIZER                             ║")
    print("║       Your self-learning file assistant                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    logger.info("Starting Smart Downloads Organizer...")
    logger.info(f"Watching: {config.DOWNLOADS_DIR}")
    logger.info(f"Scan roots: {config.SCAN_ROOTS}")
    logger.info(f"Move threshold: {config.MOVE_THRESHOLD}")
    print()

    # Initialize components
    mapper = FolderMapper()
    analyzer = FileAnalyzer()

    # Build initial folder map
    mapper.build_map()

    # Set up file watcher
    event_handler = DownloadHandler(mapper, analyzer)
    observer = Observer()
    observer.schedule(event_handler, config.DOWNLOADS_DIR, recursive=False)
    observer.start()

    # Set up periodic map refresher
    refresher = MapRefresher(mapper, config.MAP_REFRESH_INTERVAL)
    refresher.start()

    logger.info("Organizer is running. Press Ctrl+C to stop.")
    logger.info("Watching for new downloads...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        logger.info("Stopping organizer...")
        observer.stop()
        refresher.stop()
        observer.join()
        refresher.join()
        logger.info("Organizer stopped. Goodbye!")


if __name__ == "__main__":
    main()
