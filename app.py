# requirements.txt
"""
streamlit==1.29.0
pymupdf==1.23.8
transformers==4.36.2
torch==2.1.0  # Add PyTorch as the backend
pdf2image==1.16.3
pytesseract==0.3.10
gtts==2.4.0
flashtext==2.7
python-dotenv==1.0.0
"""

import streamlit as st
import fitz  # PyMuPDF
try:
    from transformers import pipeline
    transformers_available = True
except ImportError:
    transformers_available = False
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
from flashtext import KeywordProcessor

# [Keep all your braille mappings and helper functions the same...]

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="MedBraille", page_icon="♿", layout="wide")

# Sidebar Controls
with st.sidebar:
    st.header("Settings")
    use_ocr = st.checkbox("Enable OCR (for scanned PDFs)")
    use_contractions = st.checkbox("Use Braille Contractions", True)
    audio_enabled = st.checkbox("Generate Audio Summary", True)
    dark_mode = st.checkbox("High Contrast Mode")
    if not transformers_available:
        st.warning("Summarization disabled - required packages not installed")

# [Keep your dark mode CSS the same...]

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
            
            # Summarization (only if transformers available)
            if transformers_available:
                try:
                    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                    summary = summarizer(highlighted_text, max_length=300, min_length=100)[0]['summary_text']
                except Exception as e:
                    st.warning(f"Summarization failed: {str(e)}")
                    summary = highlighted_text[:500] + "..."  # Fallback to first 500 chars
            else:
                summary = highlighted_text[:500] + "..."  # Fallback to first 500 chars
                st.warning("Showing partial text (summarization unavailable)")
            
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
                
                if audio_file and os.path.exists(audio_file):  # Fixed this check
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
            if 'audio_file' in locals() and audio_file and os.path.exists(audio_file):
                os.remove(audio_file)

# [Keep the rest of your code the same...]
