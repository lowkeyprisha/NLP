"""
Test script — Verify the organizer works without watching the Downloads folder.
Simulates a download and checks if the correct folder is chosen.
"""

import os
import sys
import shutil
import tempfile
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from folder_mapper import FolderMapper
from file_analyzer import FileAnalyzer
import config


def create_test_environment():
    """
    Create a temporary test folder structure that mimics a real setup.
    Returns the temp directory path.
    """
    temp_dir = tempfile.mkdtemp(prefix="organizer_test_")

    # Create a structure like the user's real setup:
    # A:\5th sem material\flat\flat pvqs
    test_structure = [
        "5th sem material/flat/flat pvqs",
        "5th sem material/flat/flat notes",
        "5th sem material/flat/flat assignments",
        "5th sem material/operating systems/os notes",
        "5th sem material/operating systems/os previous year",
        "5th sem material/dbms/dbms notes",
        "5th sem material/dbms/dbms assignments",
        "Projects/Web Development/react projects",
        "Projects/Web Development/python scripts",
        "Projects/Machine Learning/datasets",
        "Projects/Machine Learning/models",
        "Documents/Resume and Cover Letters",
        "Documents/Tax Documents 2024",
        "Photos/Family Vacation 2024",
        "Photos/Screenshots",
    ]

    for folder in test_structure:
        path = os.path.join(temp_dir, folder)
        os.makedirs(path, exist_ok=True)

        # Create some dummy files in each folder
        folder_name = os.path.basename(path).lower()
        for i in range(3):
            dummy_file = os.path.join(path, f"{folder_name} file {i+1}.txt")
            with open(dummy_file, "w") as f:
                f.write(f"This is a {folder_name} document about {folder_name} topics. " * 10)

    return temp_dir


def test_matching():
    """Test the folder matching system."""
    print("\n" + "=" * 60)
    print("TEST: Smart Downloads Organizer")
    print("=" * 60 + "\n")

    # Create test environment
    temp_dir = create_test_environment()
    print(f"Created test environment at: {temp_dir}\n")

    # Override config to use test directory
    original_scan_roots = config.SCAN_ROOTS
    config.SCAN_ROOTS = [temp_dir]

    try:
        # Build folder map
        mapper = FolderMapper()
        mapper.build_map()

        # Initialize analyzer
        analyzer = FileAnalyzer()

        # Test cases: (filename, expected_folder_keyword)
        test_cases = [
            ("Chapter4_Memory_Management.pdf", "operating systems"),
            ("FLAT_Previous_Year_2023.pdf", "flat pvqs"),
            ("OS_Notes_Unit1.docx", "os notes"),
            ("DBMS_Assignment3.pdf", "dbms assignments"),
            ("React_Tutorial_Series.mp4", "react"),
            ("Machine_Learning_Dataset.csv", "datasets"),
            ("Resume_2024_Final.docx", "resume"),
            ("random_file_no_match.xyz", None),  # Should not match well
        ]

        print("\n" + "-" * 60)
        print("MATCHING TESTS")
        print("-" * 60 + "\n")

        passed = 0
        failed = 0

        for filename, expected_keyword in test_cases:
            # Create a dummy file to analyze
            test_file = os.path.join(temp_dir, filename)
            with open(test_file, "w") as f:
                # Write some content based on the filename
                content_words = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
                f.write(f"{content_words} " * 20)

            # Build query and find matches
            query = analyzer.build_query_text(test_file)
            matches = mapper.find_best_match(query, top_k=3)

            print(f"File: {filename}")
            if matches:
                best_path, best_score = matches[0]
                best_folder = os.path.basename(best_path)
                print(f"  Best match: {best_folder} (score: {best_score:.4f})")

                if expected_keyword:
                    if expected_keyword.lower() in best_path.lower():
                        print(f"  ✓ PASS — correctly matched to '{expected_keyword}'")
                        passed += 1
                    else:
                        print(f"  ✗ FAIL — expected '{expected_keyword}' in path")
                        failed += 1
                else:
                    if best_score < config.MOVE_THRESHOLD:
                        print(f"  ✓ PASS — correctly left in Downloads (low score)")
                        passed += 1
                    else:
                        print(f"  ? UNEXPECTED — matched to {best_folder} with score {best_score:.4f}")
                        failed += 1
            else:
                print(f"  No matches found")
                if expected_keyword is None:
                    print(f"  ✓ PASS — no match as expected")
                    passed += 1
                else:
                    print(f"  ✗ FAIL — expected match with '{expected_keyword}'")
                    failed += 1

            print()

            # Clean up test file
            os.remove(test_file)

        print("-" * 60)
        print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
        print("-" * 60)

    finally:
        # Restore config
        config.SCAN_ROOTS = original_scan_roots
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up test environment.")


if __name__ == "__main__":
    test_matching()
