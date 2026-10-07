from pathlib import Path

import pytest

from app.rag.loader import SUPPORTED_EXTENSIONS, DocumentLoadError, load_document


def make_pdf(path: Path, page_texts: list[str]) -> None:
    """Write a tiny but valid PDF with one text line per page.

    An empty string makes a blank page. Texts must not contain parentheses.
    This is a helper, not a test (its name does not start with 'test_').
    """
    count = len(page_texts)
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: (
            "<< /Type /Pages /Kids [%s] /Count %d >>"
            % (" ".join(f"{4 + 2 * i} 0 R" for i in range(count)), count)
        ).encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for i, text in enumerate(page_texts):
        page_id, content_id = 4 + 2 * i, 5 + 2 * i
        objects[page_id] = (
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 3 0 R >> >> >>"
        ).encode()
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode() if text else b""
        objects[content_id] = (
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        )

    # A PDF file is the objects, then a table (xref) saying where each one starts.
    data = b"%PDF-1.4\n"
    offsets = {}
    for number in sorted(objects):
        offsets[number] = len(data)
        data += f"{number} 0 obj\n".encode() + objects[number] + b"\nendobj\n"
    xref_start = len(data)
    data += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for number in sorted(objects):
        data += f"{offsets[number]:010d} 00000 n \n".encode()
    data += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n"
    ).encode()
    path.write_bytes(data)


# ---------- TXT files ----------


def test_txt_loads_as_one_page_numbered_1(tmp_path):
    file = tmp_path / "notes.txt"
    file.write_text("  Line one\nLine two  \n", encoding="utf-8")

    pages = load_document(file)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    # Outer whitespace is trimmed; the line break inside is kept.
    assert pages[0].text == "Line one\nLine two"


def test_file_extension_check_ignores_upper_case(tmp_path):
    file = tmp_path / "NOTES.TXT"
    file.write_text("hello", encoding="utf-8")

    assert load_document(file)[0].text == "hello"


@pytest.mark.parametrize("content", ["", "  \n\n \t"])
def test_empty_or_blank_txt_is_rejected(tmp_path, content):
    file = tmp_path / "empty.txt"
    file.write_text(content, encoding="utf-8")

    with pytest.raises(DocumentLoadError, match="empty"):
        load_document(file)


def test_txt_that_is_not_utf8_is_rejected_with_a_friendly_message(tmp_path):
    file = tmp_path / "bad.txt"
    file.write_bytes(b"\xff\xfe bad bytes \x80")

    with pytest.raises(DocumentLoadError, match="UTF-8") as error:
        load_document(file)

    # "raise ... from exc" keeps the technical cause for logs, while the
    # message the user sees stays simple.
    assert isinstance(error.value.__cause__, UnicodeDecodeError)


# ---------- unsupported types ----------


@pytest.mark.parametrize("extension", [".docx", ".png", ".py", ""])
def test_unsupported_extension_is_rejected(tmp_path, extension):
    # The file does not even need to exist: the extension is checked first.
    file = tmp_path / f"file{extension}"

    with pytest.raises(DocumentLoadError, match="Unsupported file type"):
        load_document(file)


def test_supported_extensions_are_exactly_pdf_and_txt():
    # The upload rules in the service and the frontend depend on this.
    assert SUPPORTED_EXTENSIONS == {".pdf", ".txt"}


# ---------- PDF files ----------


def test_pdf_pages_keep_their_text_and_numbers(tmp_path):
    file = tmp_path / "two.pdf"
    make_pdf(file, ["Hello page one", "Hello page two"])

    pages = load_document(file)

    assert [page.page_number for page in pages] == [1, 2]
    assert "Hello page one" in pages[0].text
    assert "Hello page two" in pages[1].text


def test_blank_pdf_page_is_skipped_but_numbering_is_kept(tmp_path):
    file = tmp_path / "gap.pdf"
    make_pdf(file, ["First page", "", "Third page"])

    pages = load_document(file)

    # Page 2 has no text so it is dropped, yet page 3 is still called page 3.
    # This keeps source citations ("page 3") correct.
    assert [page.page_number for page in pages] == [1, 3]


def test_pdf_with_no_text_is_rejected_as_possibly_scanned(tmp_path):
    file = tmp_path / "blank.pdf"
    make_pdf(file, ["", ""])

    with pytest.raises(DocumentLoadError, match="No text found"):
        load_document(file)


def test_corrupted_pdf_is_rejected_with_a_friendly_message(tmp_path):
    file = tmp_path / "junk.pdf"
    file.write_bytes(b"this is not a pdf")

    with pytest.raises(DocumentLoadError, match="Could not read this PDF") as error:
        load_document(file)

    assert error.value.__cause__ is not None  # technical cause kept for logs


def test_zero_byte_pdf_is_rejected(tmp_path):
    file = tmp_path / "zero.pdf"
    file.write_bytes(b"")

    with pytest.raises(DocumentLoadError, match="Could not read this PDF"):
        load_document(file)