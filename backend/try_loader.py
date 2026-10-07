import sys
from pathlib import Path

from app.rag.loader import DocumentLoadError, load_document

path = Path(sys.argv[1])

try:
    pages = load_document(path)
    print(f"Loaded {len(pages)} page(s)")
    for page in pages[:3]:  # show only the first three pages
        print(f"--- Page {page.page_number} ---")
        print(page.text[:300])  # first 300 characters
except DocumentLoadError as error:
    print(f"ERROR: {error}")