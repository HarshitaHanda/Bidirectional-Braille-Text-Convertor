# requirements.txt
"""
streamlit==1.29.0
pymupdf==1.23.8
transformers==4.36.2
pdf2image==1.16.3
pytesseract==0.3.10
gtts==2.4.0
flashtext==2.7
python-dotenv==1.0.0
"""

import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
from flashtext import KeywordProcessor

# ----------------------- Enhanced Braille Mappings -----------------------
BRALLE_MAP = {
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
    
    # Punctuation
    ' ': '⠀',  # Braille space
    '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖',
    "'": '⠄', '-': '⠤', '(': '⠐⠣', ')': '⠐⠜',
    
    # Special symbols
    '#': '⠼',  # Number sign
    'cap': '⠠'  # Capital sign
}

# Common contractions (Grade 2 Braille)
CONTRACTIONS = {
    'the': '⠮',
    'and': '⠯',
    'for': '⠿',
    'of': '⠷',
    'with': '⠾',
    'will': '⠂',
    'his': '⠦',
    'was': '⠫',
    'this': '⠇',
    'have': '⠬'
}

MEDICAL_TERMS = ["diagnosis", "prescription", "symptoms", "treatment", 
                "medication", "dose", "allergy", "test results", 
                "prognosis", "recommendation"]

# ----------------------- Helper Functions -----------------------
def enhanced_braille_convert(text, use_contractions=True):
    """Convert text to Braille with basic contractions and number handling"""
    # Handle contractions first
    if use_contractions:
        for word, contraction in CONTRACTIONS.items():
            text = text.replace(word, contraction)
    
    # Process remaining characters
    braille = []
    prev_char = ''
    for char in text:
        # Handle numbers
        if char.isdigit():
            if prev_char != '#':
                braille.append(BRALLE_MAP['#'])
            braille.append(BRALLE_MAP[char])
        # Handle capitalization
        elif char.isupper():
            braille.append(BRALLE_MAP['cap'])
            braille.append(BRALLE_MAP[char.lower()])
        else:
            braille.append(BRALLE_MAP.get(char.lower(), char))
        prev_char = char
    
    return ''.join(braille)

def extract_text_from_pdf(pdf_path, use_ocr=False):
    """Extract text from PDF with OCR option"""
    if use_ocr:
        try:
            images = convert_from_path(pdf_path)
            return '\n'.join([pytesseract.image_to_string(img) for img in images])
        except Exception as e:
            st.error(f"OCR Error: {str(e)}")
            return ""
    
    doc = fitz.open(pdf_path)
    return '\n'.join([page.get_text() for page in doc])

def medical_highlight(text):
    """Highlight medical terms using FlashText"""
    processor = KeywordProcessor()
    processor.add_keywords_from_list(MEDICAL_TERMS)
    return processor.replace_keywords(text)

def generate_audio(text, lang='en'):
    """Generate audio file from text"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tf:
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(tf.name)
            return tf.name
        except Exception as e:
            st.error(f"Audio Error: {str(e)}")
            return None

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="MedBraille", page_icon="♿", layout="wide")

# Sidebar Controls
with st.sidebar:
    st.header("Settings")
    use_ocr = st.checkbox("Enable OCR (for scanned PDFs)")
    use_contractions = st.checkbox("Use Braille Contractions", True)
    audio_enabled = st.checkbox("Generate Audio Summary", True)
    dark_mode = st.checkbox("High Contrast Mode")

# Dark Mode CSS
if dark_mode:
    st.markdown("""
    <style>
        body {background-color: #1a1a1a; color: #e6e6e6;}
        .st-bb {background-color: #2d2d2d;}
        .st-at {background-color: #404040;}
        .st-ax {color: #ffff00;}
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Medical Report to Braille Converter")
st.markdown("Convert healthcare PDFs into accessible Braille and audio formats")

# Main File Uploader
uploaded_file = st.file_uploader("Upload Medical PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.getvalue())
        pdf_path = tmp_pdf.name
    
    with st.spinner("Processing document..."):
        try:
            # Text Extraction
            raw_text = extract_text_from_pdf(pdf_path, use_ocr)
            if not raw_text:
                st.error("Failed to extract text from document")
                st.stop()
            
            # Medical Highlighting
            highlighted_text = medical_highlight(raw_text)
            
            # Summarization
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            summary = summarizer(highlighted_text, max_length=300, min_length=100)[0]['summary_text']
            
            # Braille Conversion
            braille_output = enhanced_braille_convert(summary, use_contractions)
            
            # Generate Audio
            audio_file = generate_audio(summary) if audio_enabled else None

            # Display Results
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Medical Summary")
                st.markdown(f"```\n{summary}\n```")
                
            with col2:
                st.subheader("Braille Output")
                st.markdown(f"```braille\n{braille_output}\n```")
                st.download_button(
                    "Download Braille File",
                    braille_output,
                    file_name="medical_report.brf",
                    mime="text/plain"
                )
                
                if audio_file:
                    st.subheader("Audio Summary")
                    st.audio(audio_file)
                    with open(audio_file, "rb") as f:
                        st.download_button(
                            "Download Audio",
                            f,
                            file_name="medical_summary.mp3",
                            mime="audio/mpeg"
                        )
            
        except Exception as e:
            st.error(f"Processing Error: {str(e)}")
        finally:
            os.remove(pdf_path)
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)

# ----------------------- Instructions -----------------------
with st.expander("How to Use"):
    st.markdown("""
    1. Upload a medical PDF document
    2. Select processing options in the sidebar
    3. View/download Braille and audio outputs
    4. For scanned documents, enable OCR processing
    
    **Features:**
    - Basic Braille conversion with contractions
    - Medical term highlighting
    - PDF text extraction with OCR fallback
    - Audio summary generation
    - High contrast mode
    """)

st.markdown("---")
st.caption("Note: This is a prototype system. Always verify Braille accuracy with a certified transcriber.")
