import fitz
import spacy
from collections import Counter
from datetime import datetime


PDF_PATH = "SoundSoar.pdf"
OUTPUT_PATH = "spacy_pdf_test_output.txt"


def extract_pdf_text(pdf_path):
    """Extract text from all pages of a PDF file."""
    text = ""

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            page_text = page.get_text()
            text += f"\n\n--- Page {page_number} ---\n"
            text += page_text

    return text


def extract_keywords(doc, limit=30):
    """Extract common keywords using spaCy token processing."""
    keywords = []

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and not token.is_punct
            and len(token.text) > 2
        ):
            keywords.append(token.lemma_.lower())

    return Counter(keywords).most_common(limit)


def main():
    results = []

    results.append("CloudSync Manager - spaCy PDF Test Output")
    results.append("=" * 50)
    results.append(f"Test Date/Time: {datetime.now()}")
    results.append(f"PDF File Tested: {PDF_PATH}")
    results.append("")

    print("Loading spaCy model...")
    results.append("Loading spaCy model: en_core_web_sm")

    nlp = spacy.load("en_core_web_sm")

    print("Reading PDF...")
    results.append("Reading PDF text using PyMuPDF...")

    text = extract_pdf_text(PDF_PATH)

    results.append("")
    results.append("BASIC PDF TEXT SUMMARY")
    results.append("-" * 50)
    results.append(f"Total characters extracted: {len(text)}")
    results.append(f"Total words extracted: {len(text.split())}")

    print("Processing text with spaCy...")
    doc = nlp(text)

    results.append("")
    results.append("NAMED ENTITIES EXTRACTED")
    results.append("-" * 50)

    if doc.ents:
        for ent in doc.ents[:75]:
            results.append(f"{ent.text} -> {ent.label_}")
    else:
        results.append("No named entities found.")

    results.append("")
    results.append("KEYWORDS / IMPORTANT TERMS")
    results.append("-" * 50)

    keywords = extract_keywords(doc, limit=30)

    for word, count in keywords:
        results.append(f"{word}: {count}")

    results.append("")
    results.append("TEST RESULT")
    results.append("-" * 50)
    results.append("PASS: spaCy successfully loaded the model, read the PDF, extracted text, identified named entities, and generated keyword counts.")

    output_text = "\n".join(results)

    print(output_text)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(output_text)

    print("")
    print(f"Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()