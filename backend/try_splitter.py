import sys
from pathlib import Path

from app.rag.loader import DocumentLoadError, load_document
from app.rag.splitter import split_pages

# Make sure special characters from PDFs print safely on Windows.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = Path(sys.argv[1])
chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
chunk_overlap = int(sys.argv[3]) if len(sys.argv) > 3 else None

try:
    pages = load_document(path)
except DocumentLoadError as error:
    print(f"ERROR: {error}")
    sys.exit(1)

chunks = split_pages(
    pages,
    document_id="test-doc",
    document_name=path.name,
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)

lengths = [len(c.text) for c in chunks]
print(f"Pages with text: {len(pages)}")
print(f"Chunks created:  {len(chunks)}")
print(f"Shortest chunk:  {min(lengths)} characters")
print(f"Longest chunk:   {max(lengths)} characters")
print(f"Average chunk:   {sum(lengths) // len(lengths)} characters")

for chunk in chunks[2:5]:
    print(f"\n--- chunk_index={chunk.chunk_index}, page={chunk.page_number}, {len(chunk.text)} chars ---")
    print(chunk.text[:400])