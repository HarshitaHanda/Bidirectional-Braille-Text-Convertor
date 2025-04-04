import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import pyperclip  # For copying text to clipboard
import re
from symspellpy import SymSpell, Verbosity
from textblob import TextBlob
import pkg_resources

# Braille-Text Mappings (Unicode Braille characters)
braille_to_text = {
    # Letters
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
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def main():
    st.title("Braille Converter")

    # Select conversion mode
    mode = st.radio("Select Conversion Mode:", ["Text to Braille", "Braille to Text"])

    # Text input or braille input based on the mode
    input_text = st.text_area("Enter text or Braille:")
    
    # Conversion function
    def convert_text():
        if mode == "Text to Braille":
            result = text_to_braille_conversion(input_text)
        else:
            result = braille_to_text_conversion(input_text)
        return result

    # Display the conversion result
    st.text_area("Converted Result:", value=convert_text(), height=150)

    # PDF Upload
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf is not None:
        extracted_text = extract_text_from_pdf(uploaded_pdf)
        st.text_area("Extracted Text from PDF:", value=extracted_text, height=150)

    # Copy to Clipboard button
    if st.button("Copy Result to Clipboard"):
        pyperclip.copy(convert_text())
        st.success("Text copied to clipboard!")

if __name__ == "__main__":
    main()
