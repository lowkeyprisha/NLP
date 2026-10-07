"""
File Analyzer — Extracts text and features from downloaded files
for matching against the folder map.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FileAnalyzer:
    """Extracts meaningful text from various file types."""

    def __init__(self):
        self._pdf_reader = None
        self._docx_reader = None
        self._pptx_reader = None
        self._openpyxl_reader = None

    def extract_text(self, filepath: str, max_chars: int = 5000) -> Optional[str]:
        """
        Extract text content from a file.
        
        Args:
            filepath: Path to the file.
            max_chars: Maximum characters to extract.
            
        Returns:
            Extracted text string, or None if extraction failed.
        """
        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext == ".pdf":
                return self._extract_pdf(filepath, max_chars)
            elif ext == ".docx":
                return self._extract_docx(filepath, max_chars)
            elif ext == ".doc":
                return self._extract_doc(filepath, max_chars)
            elif ext == ".pptx":
                return self._extract_pptx(filepath, max_chars)
            elif ext == ".xlsx":
                return self._extract_xlsx(filepath, max_chars)
            elif ext in (".txt", ".md", ".rtf", ".csv"):
                return self._extract_plain_text(filepath, max_chars)
            elif ext in (".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs",
                        ".html", ".css", ".json", ".xml", ".yaml", ".yml"):
                return self._extract_plain_text(filepath, max_chars)
            elif ext == ".epub":
                return self._extract_epub(filepath, max_chars)
            else:
                # For binary files (videos, images, etc.), return None
                # The filename alone will be used for matching
                return None
        except Exception as e:
            logger.debug(f"Text extraction failed for {filepath}: {e}")
            return None

    def _extract_pdf(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from PDF files."""
        if self._pdf_reader is None:
            try:
                from PyPDF2 import PdfReader
                self._pdf_reader = PdfReader
            except ImportError:
                logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
                return None

        reader = self._pdf_reader(filepath)
        text_parts = []

        # Extract from first few pages (most relevant for identification)
        for i, page in enumerate(reader.pages[:5]):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception:
                continue

        full_text = " ".join(text_parts)
        return full_text[:max_chars] if full_text else None

    def _extract_docx(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from DOCX files."""
        if self._docx_reader is None:
            try:
                import docx
                self._docx_reader = docx
            except ImportError:
                logger.warning("python-docx not installed. Install with: pip install python-docx")
                return None

        doc = self._docx_reader.Document(filepath)
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = " ".join(text_parts)
        return full_text[:max_chars] if full_text else None

    def _extract_doc(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from old .doc files (best effort)."""
        try:
            # Try antiword or textract as fallback
            import subprocess
            result = subprocess.run(
                ["antiword", filepath],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout[:max_chars]
        except Exception:
            pass
        return None

    def _extract_pptx(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from PPTX files."""
        if self._pptx_reader is None:
            try:
                from pptx import Presentation
                self._pptx_reader = Presentation
            except ImportError:
                logger.warning("python-pptx not installed. Install with: pip install python-pptx")
                return None

        prs = self._pptx_reader(filepath)
        text_parts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_parts.append(shape.text)
        full_text = " ".join(text_parts)
        return full_text[:max_chars] if full_text else None

    def _extract_xlsx(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from XLSX files."""
        if self._openpyxl_reader is None:
            try:
                import openpyxl
                self._openpyxl_reader = openpyxl
            except ImportError:
                logger.warning("openpyxl not installed. Install with: pip install openpyxl")
                return None

        wb = self._openpyxl_reader.load_workbook(filepath, read_only=True, data_only=True)
        text_parts = []
        for sheet in wb.sheetnames[:3]:  # First 3 sheets
            ws = wb[sheet]
            text_parts.append(sheet)  # Sheet name is a signal
            for row in ws.iter_rows(max_row=20, values_only=True):
                for cell in row:
                    if cell and isinstance(cell, str):
                        text_parts.append(cell)
        wb.close()
        full_text = " ".join(text_parts)
        return full_text[:max_chars] if full_text else None

    def _extract_plain_text(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from plain text files."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_chars)
        except Exception:
            return None

    def _extract_epub(self, filepath: str, max_chars: int) -> Optional[str]:
        """Extract text from EPUB files (basic)."""
        try:
            import zipfile
            from xml.etree import ElementTree as ET

            text_parts = []
            with zipfile.ZipFile(filepath, "r") as z:
                for name in z.namelist():
                    if name.endswith((".xhtml", ".html", ".htm")):
                        try:
                            content = z.read(name).decode("utf-8", errors="ignore")
                            # Strip HTML tags crudely
                            root = ET.fromstring(content)
                            text = " ".join(root.itertext())
                            text_parts.append(text)
                        except Exception:
                            continue
            full_text = " ".join(text_parts)
            return full_text[:max_chars] if full_text else None
        except Exception:
            return None

    def build_query_text(self, filepath: str) -> str:
        """
        Build a query text string from a file for matching.
        Combines filename + extracted content.
        
        Args:
            filepath: Path to the downloaded file.
            
        Returns:
            Combined query text for TF-IDF matching.
        """
        parts = []

        # 1. Filename (cleaned and weighted heavily by repetition)
        filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(filename)[0]
        # Clean: replace separators with spaces
        clean_name = name_without_ext.replace("_", " ").replace("-", " ").replace(".", " ")
        # Add filename 3 times to weight it heavily
        parts.extend([clean_name] * 3)

        # 2. File content (if extractable)
        content = self.extract_text(filepath, max_chars=3000)
        if content:
            parts.append(content)

        # 3. Parent folder name (sometimes downloads come in subfolders)
        parent = os.path.basename(os.path.dirname(filepath))
        if parent and parent != os.path.basename(config.DOWNLOADS_DIR):
            clean_parent = parent.replace("_", " ").replace("-", " ")
            parts.append(clean_parent)

        return " ".join(parts)
