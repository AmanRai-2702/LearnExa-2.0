from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


class DocumentLoadError(Exception):
    """Raised when a document cannot be read. The message is safe to show to users."""


@dataclass
class PageText:
    """The text of one page, plus its page number (starting at 1)."""

    page_number: int
    text: str


def load_pdf(path: Path) -> list[PageText]:
    """Extract text from each page of a PDF."""
    try:
        reader = PdfReader(str(path))
        pages: list[PageText] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:  # skip pages with no text (blank or image-only)
                pages.append(PageText(page_number=page_number, text=text))
    except Exception as exc:
        raise DocumentLoadError(
            "Could not read this PDF. It may be corrupted or password-protected."
        ) from exc

    if not pages:
        raise DocumentLoadError(
            "No text found in this PDF. It may be a scanned document made of images."
        )
    return pages


def load_txt(path: Path) -> list[PageText]:
    """Read a plain text file. A TXT file has no pages, so we call it page 1."""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise DocumentLoadError(
            "Could not read this text file. Please save it as UTF-8."
        ) from exc

    if not text:
        raise DocumentLoadError("This text file is empty.")
    return [PageText(page_number=1, text=text)]


def load_document(path: Path) -> list[PageText]:
    """Choose the right loader based on the file extension."""
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentLoadError(
            f"Unsupported file type '{extension}'. Please upload a PDF or TXT file."
        )

    if extension == ".pdf":
        return load_pdf(path)
    return load_txt(path)