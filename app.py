import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import json  # For storing dictionary
import pyperclip  # For copying text to clipboard
from textblob import TextBlob  # Grammar and spell correction
from symspellpy import SymSpell, Verbosity
import pkg_resources
import re

# Corrected Braille mappings with proper number handling
braille_to_text = {
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
    '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
    '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
    '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
    '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
    '⠵': 'z',

    # Numbers (with numeric prefix ⠼)
    '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4', '⠼⠑': '5',
    '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8', '⠼⠊': '9', '⠼⠚': '0',

    # Punctuation and symbols
    '⠀': ' ', '⠂': ',', '⠲': '.', '⠦': '?', '⠤': '-',
    '⠖': '!', '⠴': ':', '⠰': '#', '⠔': '"', '⠣': ';',
    '⠷': '(', '⠾': ')', '⠡': '+', '⠯': '=',
    '⠮': '*', '⠾': ']', '⠢': '$', '⠶': '_'
}

text_to_braille = {v: k for k, v in braille_to_text.items()}

# Spell Correction using SymSpell
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Auto-correction function
def auto_correct_sentence(text):
    words = re.findall(r'\w+|\s+|[^\w\s]', text)
    corrected = []
    for word in words:
        if word.strip():
            suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
            corrected.append(suggestions[0].term if suggestions else word)
        else:
            corrected.append(word)
    corrected_text = ''.join(corrected)
    blob = TextBlob(corrected_text)
    return str(blob.correct())

def braille_to_text_conversion(braille_str):
    """
    Converts Braille to text and applies sentence-level auto-correction.
    This version handles multi-character Braille sequences (for letters, numbers, and punctuation).
    """
    raw = []
    i = 0
    while i < len(braille_str):
        # Check for 2-character sequences first (e.g., numbers with the ⠼ prefix)
        if i + 1 < len(braille_str):
            two_char = braille_str[i:i+2]
            if two_char in braille_to_text:
                raw.append(braille_to_text[two_char])
                i += 2  # Move forward by 2
                continue
        # Handle single characters
        raw.append(braille_to_text.get(braille_str[i], '?'))  # Use '?' for unsupported characters
        i += 1
    # Convert to text and apply auto-correction (spelling & grammar)
    return auto_correct_sentence(''.join(raw))

def text_to_braille_conversion(text_str):
    """
    Converts English text to Braille.
    """
    braille_str = []
    text_str = text_str.lower()
    for char in text_str:
        # Handle numbers with prefix
        if char.isdigit():
            braille_str.append(text_to_braille.get(f'⠼{char}', '?'))  # Add numeric prefix ⠼
        else:
            braille_str.append(text_to_braille.get(char, '?'))  # Replace with '?' if not found
    return ''.join(braille_str)

# PDF extraction function
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Streamlit UI
def main():
    st.title("Braille Converter")

    # Mode selection
    mode = st.radio("Choose Conversion Mode", ("Text to Braille", "Braille to Text"))

    # File upload
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])

    if uploaded_pdf is not None:
        # Process the uploaded PDF
        extracted_text = extract_text_from_pdf(uploaded_pdf)
        st.text_area("Extracted Text", extracted_text, height=150)

        if mode == "Braille to Text":
            # Convert the Braille extracted from the PDF to text
            braille_converted_text = braille_to_text_conversion(extracted_text)
            st.text_area("Converted Text", braille_converted_text, height=150)
        else:
            # Convert text to Braille
            text_converted_braille = text_to_braille_conversion(extracted_text)
            st.text_area("Converted Braille", text_converted_braille, height=150)

    else:
        st.warning("Upload a PDF file to proceed with conversion.")

    # Add option to copy text to clipboard
    if st.button("Copy to Clipboard"):
        pyperclip.copy(st.session_state.get('converted_text', ''))
        st.success("Text copied to clipboard!")

# Run the Streamlit app
if __name__ == "__main__":
    main()
