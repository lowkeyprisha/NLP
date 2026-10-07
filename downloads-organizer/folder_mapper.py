"""
Folder Mapper — Recursively scans directories and builds a mathematical
"map" of what kind of content belongs in each folder.

Uses TF-IDF vectorization on folder names + file names + file content
to create a searchable similarity space.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import config

logger = logging.getLogger(__name__)


@dataclass
class FolderProfile:
    """Represents a single folder and its learned content profile."""
    path: str
    name: str
    depth: int
    files: List[str] = field(default_factory=list)
    subfolders: List[str] = field(default_factory=list)
    text_content: str = ""  # Aggregated text from files in this folder
    tfidf_vector: Optional[np.ndarray] = None

    @property
    def relative_name(self) -> str:
        """Get a readable relative path for display."""
        return self.path


class FolderMapper:
    """
    Builds and maintains a map of all folders on the system.
    
    The map is represented as TF-IDF vectors, allowing fast
    cosine-similarity matching against new downloads.
    """

    def __init__(self):
        self.folders: Dict[str, FolderProfile] = {}
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.folder_matrix: Optional[np.ndarray] = None
        self.folder_paths: List[str] = []  # Indexed list for matrix lookup
        self._is_built = False

    def build_map(self, force: bool = False) -> None:
        """
        Scan all SCAN_ROOTS recursively and build the folder map.
        
        Args:
            force: If True, rebuild even if already built.
        """
        if self._is_built and not force:
            logger.debug("Folder map already built, skipping.")
            return

        logger.info("=" * 60)
        logger.info("Building folder map...")
        logger.info("=" * 60)

        self.folders.clear()
        self.folder_paths.clear()

        # Phase 1: Discover all folders
        for root in config.SCAN_ROOTS:
            if not os.path.exists(root):
                logger.warning(f"Scan root does not exist: {root}")
                continue
            self._scan_directory(root)

        logger.info(f"Discovered {len(self.folders)} folders total.")

        # Phase 2: Extract text content from files in each folder
        self._extract_folder_contents()

        # Phase 3: Build TF-IDF vectors
        self._build_vectors()

        self._is_built = True
        logger.info("Folder map built successfully.")
        self._print_summary()

    def _scan_directory(self, root: str) -> None:
        """Recursively scan a directory tree, creating FolderProfile entries."""
        root = os.path.normpath(root)

        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out excluded directories
            dirnames[:] = [
                d for d in dirnames
                if d not in config.EXCLUDE_DIRS and not d.startswith(".")
            ]

            # Skip the Downloads folder itself (we don't want to match against it)
            norm_path = os.path.normpath(dirpath)
            if norm_path == os.path.normpath(config.DOWNLOADS_DIR):
                dirnames[:] = []  # Don't descend into Downloads
                continue

            # Create profile for this folder
            folder_name = os.path.basename(dirpath)
            depth = dirpath.count(os.sep)

            profile = FolderProfile(
                path=norm_path,
                name=folder_name,
                depth=depth,
                files=filenames.copy(),
                subfolders=dirnames.copy(),
            )
            self.folders[norm_path] = profile
            self.folder_paths.append(norm_path)

    def _extract_folder_contents(self) -> None:
        """
        Extract text content from files in each folder.
        This gives the mapper a sense of what each folder 'is about'.
        """
        from file_analyzer import FileAnalyzer

        analyzer = FileAnalyzer()

        for path, profile in self.folders.items():
            text_parts = []

            # Add folder name as a strong signal
            text_parts.append(profile.name.replace("_", " ").replace("-", " "))

            # Add subfolder names as signals
            for sub in profile.subfolders:
                text_parts.append(sub.replace("_", " ").replace("-", " "))

            # Extract text from files (limit to avoid huge folders)
            for filename in profile.files[:50]:  # Cap at 50 files per folder
                ext = os.path.splitext(filename)[1].lower()

                if ext in config.TEXT_EXTENSIONS:
                    filepath = os.path.join(path, filename)
                    try:
                        text = analyzer.extract_text(filepath, max_chars=2000)
                        if text:
                            text_parts.append(text)
                    except Exception as e:
                        logger.debug(f"Could not extract from {filepath}: {e}")

                # Always add filename as a signal (cleaned)
                clean_name = os.path.splitext(filename)[0]
                clean_name = clean_name.replace("_", " ").replace("-", " ")
                text_parts.append(clean_name)

            profile.text_content = " ".join(text_parts)

    def _build_vectors(self) -> None:
        """Build TF-IDF vectors for all folders."""
        if not self.folders:
            logger.warning("No folders to vectorize.")
            return

        # Token pattern that captures words of 2+ characters
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),  # Unigrams + bigrams for better matching
            max_features=10000,
            token_pattern=r"(?u)\b[a-zA-Z]{2,}\b",  # Words with 2+ letters
        )

        # Build corpus: folder text content
        corpus = []
        valid_paths = []

        for path in self.folder_paths:
            profile = self.folders[path]
            if profile.text_content.strip():
                corpus.append(profile.text_content)
                valid_paths.append(path)

        if not corpus:
            logger.warning("No text content found in any folder.")
            return

        self.folder_matrix = self.vectorizer.fit_transform(corpus)
        self.folder_paths = valid_paths  # Update to only include valid ones

        # Store vectors in profiles
        for i, path in enumerate(self.folder_paths):
            self.folders[path].tfidf_vector = self.folder_matrix[i]

        logger.info(f"Built TF-IDF matrix: {self.folder_matrix.shape}")

    def find_best_match(self, query_text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find the best matching folders for a given query text.
        
        Args:
            query_text: The text to match against folder profiles.
            top_k: Number of top matches to return.
            
        Returns:
            List of (folder_path, similarity_score) tuples, sorted by score desc.
        """
        if not self._is_built or self.folder_matrix is None:
            logger.warning("Folder map not built yet. Call build_map() first.")
            return []

        # Vectorize the query
        query_vector = self.vectorizer.transform([query_text])

        # Compute cosine similarity against all folders
        similarities = cosine_similarity(query_vector, self.folder_matrix).flatten()

        # Get top-k matches
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            path = self.folder_paths[idx]
            results.append((path, score))

        return results

    def get_folder_display_path(self, path: str) -> str:
        """Get a shortened display path for logging."""
        try:
            # Show last 3-4 path components for readability
            parts = path.split(os.sep)
            if len(parts) > 4:
                return os.sep.join(["..."] + parts[-4:])
            return path
        except Exception:
            return path

    def _print_summary(self) -> None:
        """Print a summary of the discovered folder structure."""
        logger.info("-" * 60)
        logger.info("Folder Map Summary:")
        logger.info("-" * 60)

        # Show some example folders at different depths
        by_depth: Dict[int, List[str]] = {}
        for path, profile in self.folders.items():
            by_depth.setdefault(profile.depth, []).append(path)

        for depth in sorted(by_depth.keys())[:6]:
            folders_at_depth = by_depth[depth][:5]
            logger.info(f"  Depth {depth}: {len(by_depth[depth])} folders")
            for f in folders_at_depth:
                logger.info(f"    → {self.get_folder_display_path(f)}")

        logger.info("-" * 60)

    def refresh(self) -> None:
        """Rebuild the folder map (called periodically)."""
        logger.info("Refreshing folder map...")
        self._is_built = False
        self.build_map(force=True)
