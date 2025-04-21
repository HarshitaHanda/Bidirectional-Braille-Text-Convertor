# requirements.txt should include:
# streamlit==1.29.0
# pymupdf==1.23.8
# transformers==4.36.2
# torch==2.1.2
# pdf2image==1.16.3
# pytesseract==0.3.10
# gtts==2.4.0
# flashtext==2.7
# python-dotenv==1.0.0

import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
import torch
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
from flashtext import KeywordProcessor

# ----------------------- Enhanced Braille Mappings -----------------------
BRAILLE_MAP = {
    # Alphabet
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    # Numbers
    '0': '⠚', '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙',
    '5': '⠑', '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊',
    # Punctuation & space
    ' ': '⠀', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖',
    "'": '⠄', '-': '⠤', '(': '⠐⠣', ')': '⠐⠜',
    '#': '⠼',  # Number sign
    'cap': '⠠'  # Capital sign
}

# Grade 2 Braille contractions
CONTRACTIONS = {
    'the': '⠮', 'and': '⠯', 'for': '⠿', 'of': '⠷', 'with': '⠾',
    'will': '⠂', 'his': '⠦', 'was': '⠫', 'this': '⠇', 'have': '⠬'
}

MEDICAL_TERMS = [
    "diagnosis", "prescription", "symptoms", "treatment", "medication",
    "dose", "allergy", "test results", "prognosis", "recommendation"
]

# ----------------------- Helper Functions -----------------------
def enhanced_braille_convert(text: str, use_contractions: bool = True) -> str:
    """Convert text to Braille with contractions and number handling"""
    if use_contractions:
        # apply contractions first (word-level)
        for word, contraction in CONTRACTIONS.items():
            text = text.replace(word, contraction)

    braille_chars = []
    prev = ''
    for ch in text:
        if ch.isdigit():
            # prepend number sign if needed
            if prev != '#':
                braille_chars.append(BRAILLE_MAP['#'])
            braille_chars.append(BRAILLE_MAP[ch])
        elif ch.isupper():
            braille_chars.append(BRAILLE_MAP['cap'])
            braille_chars.append(BRAILLE_MAP.get(ch.lower(), ch))
        else:
            braille_chars.append(BRAILLE_MAP.get(ch, ch))
        prev = ch
    return ''.join(braille_chars)


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> str:
    """Extract text from PDF, optionally using OCR for scanned pages"""
    if use_ocr:
        try:
            images = convert_from_path(pdf_path)
            text = []
            for img in images:
                text.append(pytesseract.image_to_string(img))
            return '\n'.join(text)
        except Exception as e:
            st.error(f"OCR Error: {e}")
            return ''
    try:
        doc = fitz.open(pdf_path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return '\n'.join(pages)
    except Exception as e:
        st.error(f"PDF Read Error: {e}")
        return ''


def medical_highlight(text: str) -> str:
    """Highlight medical terms (or mark them)"""
    processor = KeywordProcessor()
    processor.add_keywords_from_list(MEDICAL_TERMS)
    # wrap found terms in brackets for visibility
    for term in MEDICAL_TERMS:
        text = text.replace(term, f"**{term}**")
    return text


def generate_audio(text: str, lang: str = 'en') -> str:
    """Generate audio file from text using gTTS"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tf:
            tts = gTTS(text=text, lang=lang)
            tts.save(tf.name)
            return tf.name
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return ''

# ----------------------- Streamlit App -----------------------
st.set_page_config(page_title="MedBraille", page_icon="♿", layout="wide")

st.title("📄 Medical Report to Braille Converter")
st.markdown("Convert healthcare PDFs into accessible Braille and audio formats")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    use_ocr = st.checkbox("Enable OCR (scanned PDFs)")
    use_contractions = st.checkbox("Use Braille Contractions", value=True)
    audio_enabled = st.checkbox("Generate Audio Summary", value=True)
    dark_mode = st.checkbox("High Contrast Mode")

# Dark mode CSS
if dark_mode:
    st.markdown(
        """
        <style>
            body { background-color: #1a1a1a; color: #e6e6e6; }
            .stApp { background-color: #1a1a1a; }
        </style>
        """, unsafe_allow_html=True
    )

# File uploader
uploaded = st.file_uploader("Upload Medical PDF", type=['pdf'])
if uploaded:
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(uploaded.getvalue())
        pdf_path = tmp.name

    audio_file = ''
    try:
        with st.spinner("Processing..."):
            text = extract_text_from_pdf(pdf_path, use_ocr)
            if not text:
                st.error("Failed to extract text.")
                st.stop()

            highlighted = medical_highlight(text)

            # Summarize
            summarizer = pipeline(
                "summarization", model="facebook/bart-large-cnn"
            )
            summary = summarizer(highlighted, max_length=300, min_length=100)[0]['summary_text']

            # Convert to Braille
            braille = enhanced_braille_convert(summary, use_contractions)

            # Generate audio if needed
            if audio_enabled:
                audio_file = generate_audio(summary)

        # Display results
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Summary")
            st.write(summary)
        with col2:
            st.subheader("Braille Output")
            st.code(braille, language='braille')
            st.download_button(
                "Download .brf", braille.encode('utf-8'),
                file_name='report.brf', mime='text/plain'
            )
            if audio_enabled and audio_file:
                st.subheader("Audio Summary")
                st.audio(audio_file)
                with open(audio_file, 'rb') as f:
                    st.download_button(
                        "Download Audio", f.read(),
                        file_name='summary.mp3', mime='audio/mpeg'
                    )
    except Exception as e:
        st.error(f"Processing Error: {e}")
    finally:
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)

# Instructions
with st.expander("How to Use"):
    st.markdown(
        """
        1. Upload a medical PDF document.
        2. Adjust settings in the sidebar (OCR, contractions, audio, contrast).
        3. View and download the Braille (.brf) and audio outputs.
        """
    )

st.caption("Prototype: verify Braille with a certified transcriber.")
