import fitz  # PyMuPDF
import docx
import pandas as pd
from pptx import Presentation
import pytesseract
from PIL import Image

def extract_txt(file_path: str) -> tuple[str, int]:
    """Returns (full_text, page_count). TXT has no real pages, so page_count = 1."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return text, 1


def extract_pdf(file_path: str) -> tuple[str, int]:
    """Returns (full_text, page_count), reading each page with PyMuPDF."""
    doc = fitz.open(file_path)
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    full_text = "\n\n".join(pages_text)
    page_count = doc.page_count
    doc.close()
    return full_text, page_count


def extract_docx(file_path: str) -> tuple[str, int]:
    """Returns (full_text, page_count). DOCX has no fixed 'pages' in the file
    itself, so we approximate page_count as 1 for now — can improve later."""
    document = docx.Document(file_path)
    paragraphs = [p.text for p in document.paragraphs]
    full_text = "\n".join(paragraphs)
    return full_text, 1


def extract_text(file_path: str, file_type: str) -> tuple[str, int]:
    extractors = {
        "txt": extract_txt,
        "pdf": extract_pdf,
        "docx": extract_docx,
        "csv": extract_csv,
        "xlsx": extract_xlsx,
        "pptx": extract_pptx,
        "png": extract_image,
        "jpg": extract_image,
        "jpeg": extract_image,
    }
    extractor = extractors.get(file_type)
    if extractor is None:
        raise ValueError(f"No extractor available for file type: {file_type}")
    return extractor(file_path)

def extract_csv(file_path: str) -> tuple[str, int]:
    """
    Converts a CSV into readable text. We represent each row as a line of
    "column: value" pairs, which embeds and searches much better than raw
    comma-separated values.
    """
    df = pd.read_csv(file_path)
    lines = []
    for _, row in df.iterrows():
        row_text = ", ".join(f"{col}: {row[col]}" for col in df.columns)
        lines.append(row_text)
    full_text = "\n".join(lines)
    return full_text, 1


def extract_xlsx(file_path: str) -> tuple[str, int]:
    """
    Reads every sheet in an Excel file, converts each to the same readable
    "column: value" text format as CSV, labeled by sheet name.
    """
    sheets = pd.read_excel(file_path, sheet_name=None)  # None = all sheets, returns a dict
    all_text = []

    for sheet_name, df in sheets.items():
        all_text.append(f"=== Sheet: {sheet_name} ===")
        for _, row in df.iterrows():
            row_text = ", ".join(f"{col}: {row[col]}" for col in df.columns)
            all_text.append(row_text)

    full_text = "\n".join(all_text)
    page_count = len(sheets)  # treat each sheet as a "page" for metadata purposes
    return full_text, page_count



def extract_pptx(file_path: str) -> tuple[str, int]:
    """
    Extracts text from every slide, including text boxes, titles, and
    bullet points. Tables and speaker notes could be added later if needed.
    """
    presentation = Presentation(file_path)
    slides_text = []

    for i, slide in enumerate(presentation.slides, start=1):
        slide_parts = [f"=== Slide {i} ==="]
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = "".join(run.text for run in paragraph.runs)
                    if text.strip():
                        slide_parts.append(text)
        slides_text.append("\n".join(slide_parts))

    full_text = "\n\n".join(slides_text)
    page_count = len(presentation.slides)
    return full_text, page_count



def extract_image(file_path: str) -> tuple[str, int]:
    """
    Runs OCR on an image file to extract any text it contains.
    Returns empty text (not an error) if no text is detected — some images
    genuinely have no readable text, which is a valid, non-failure outcome.
    """
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip(), 1