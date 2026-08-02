from utils.pdf_reader import extract_text


def process_document(filepath):
    """
    Extract readable text from an uploaded document.

    Raises:
        ValueError: if the document contains no readable text.
    """

    text = extract_text(filepath)

    if not text.strip():
        raise ValueError(
            "This document contains no readable text."
        )

    return text