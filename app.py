# requirements.txt
"""
streamlit==1.29.0
pymupdf==1.23.8
transformers==4.36.2
torch==2.1.2
python-louis==3.27.0
pdf2image==1.16.3
pytesseract==0.3.10
gtts==2.4.0
flashtext==2.7
"""

import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
import tempfile
import os
import louis
from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
from flashtext import KeywordProcessor

# ----------------------- Configuration -----------------------
MEDICAL_TERMS = ["cancer", "diabetes", "hypertension", "covid", "allergy",
                 "cholesterol", "diagnosis", "symptom", "treatment", "dose"]

# ----------------------- Helper Functions -----------------------
def extract_text_from_pdf(pdf_path, is_scanned=False):
    """Extract text from PDF with OCR fallback"""
    if is_scanned:
        try:
            images = convert_from_path(pdf_path)
            text = "\n".join([pytesseract.image_to_string(img) for img in images])
            return text
        except Exception as e:
            st.error(f"OCR Error: {str(e)}")
            return ""
    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def summarize_text(text):
    """Summarize text using medical-optimized model"""
    try:
        summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")
        return summarizer(text, max_length=300, min_length=100, do_sample=False)[0]['summary_text']
    except Exception as e:
        st.error(f"Summarization Error: {str(e)}")
        return text[:500]  # Fallback to first 500 chars

def convert_to_braille(text):
    """Convert text to Grade 2 Braille using liblouis"""
    try:
        return louis.translateString(["en-ueb-g2.ctb"], text)[0]
    except Exception as e:
        st.error(f"Braille Conversion Error: {str(e)}")
        return ""

def highlight_medical_terms(text):
    """Highlight key medical terms in summary"""
    processor = KeywordProcessor()
    processor.add_keywords_from_list(MEDICAL_TERMS)
    return processor.replace_keywords(text)

def text_to_speech(text, filename="summary.mp3"):
    """Generate audio version of summary"""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        return filename
    except Exception as e:
        st.error(f"Audio Generation Error: {str(e)}")
        return None

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="MedBraille", page_icon="♿")

# Dark Mode Toggle
with st.sidebar:
    st.header("Accessibility Settings")
    dark_mode = st.checkbox("High Contrast Mode")

if dark_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #1a1a1a; color: #ffff00; }
        .st-bb { background-color: #2d2d2d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 MedBraille - Healthcare Accessibility Converter")
st.markdown("### Transform medical reports into accessible formats")

# File Upload Section
with st.expander("Upload Your Medical Report", expanded=True):
    uploaded_file = st.file_uploader("Choose PDF file", type="pdf")
    is_scanned = st.checkbox("Scanned Document (OCR required)")

if uploaded_file is not None:
    # Save uploaded file to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Processing Pipeline
    with st.spinner("🔍 Processing document..."):
        try:
            # Step 1: Text Extraction
            raw_text = extract_text_from_pdf(tmp_path, is_scanned)
            if not raw_text:
                st.error("Failed to extract text from document")
                os.unlink(tmp_path)
                st.stop()

            # Step 2: Summarization
            summary = summarize_text(raw_text)
            
            # Step 3: Medical Highlighting
            highlighted_summary = highlight_medical_terms(summary)
            
            # Step 4: Braille Conversion
            braille_output = convert_to_braille(summary)
            
            # Step 5: Audio Generation
            audio_file = text_to_speech(summary)

            # Display Results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Medical Summary")
                st.markdown(f"<div style='border-left: 5px solid #4CAF50; padding: 1rem;'>{highlighted_summary}</div>", 
                           unsafe_allow_html=True)

            with col2:
                st.subheader("🖇 Braille Output")
                st.markdown(f"braille\n{braille_output}\n")
                
                # Braille Download
                st.download_button(
                    label="⬇ Download Braille File",
                    data=braille_output,
                    file_name="medical_report.brf",
                    mime="text/plain"
                )

            # Audio Player
            if audio_file:
                st.subheader("🔊 Audio Summary")
                st.audio(audio_file)
                with open(audio_file, "rb") as f:
                    st.download_button(
                        label="⬇ Download Audio",
                        data=f,
                        file_name="medical_summary.mp3",
                        mime="audio/mpeg"
                    )

        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
        finally:
            os.unlink(tmp_path)
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)

# ----------------------- Sidebar Info -----------------------
with st.sidebar:
    st.header("About MedBraille")
    st.markdown("""
    *Features:*
    - PDF text extraction (including scanned docs)
    - AI-powered medical summarization
    - Grade 2 Braille conversion
    - Audio summary generation
    - Key medical term highlighting
    - High contrast mode

    *System Requirements:*
    - Tesseract OCR installed
    - liblouis tables available
    """)

    st.markdown("---")
    st.markdown("⚠ *Important Notes:*\n"
                "- Always verify Braille accuracy before clinical use\n"
                "- Protected Health Information (PHI) is processed temporarily\n"
                "- Consult original documents for critical decisions")

# ----------------------- System Checks -----------------------
try:
    louis.translateString(["en-ueb-g2.ctb"], "test")[0]
except Exception as e:
    st.error("Braille system not configured properly. Install liblouis and Braille tables.")
