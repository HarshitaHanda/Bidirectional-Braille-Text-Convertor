# # import streamlit as st
# # import re
# # from symspellpy import SymSpell, Verbosity
# # import pkg_resources
# # import fitz
# # import json
# # from textblob import TextBlob

# # # ----------------------- Braille Mappings -----------------------
# # braille_to_text = {
# #     '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
# #     '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
# #     '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
# #     '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
# #     '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
# #     '⠵': 'z',
# #     '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4', '⠼⠑': '5',
# #     '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8', '⠼⠊': '9', '⠼⠚': '0',
# #     '⠀': ' ', '⠂': ',', '⠲': '.', '⠦': '?', '⠤': '-',
# #     '⠖': '!', '⠴': ':', '⠰': '#', '⠔': '"', '⠣': ';',
# #     '⠷': '(', '⠾': ')', '⠡': '+', '⠯': '=',
# #     '⠮': '*', '⠢': '$', '⠶': '_'
# # }

# # text_to_braille = {v: k for k, v in braille_to_text.items()}
# # text_to_braille.update({
# #     '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
# #     '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚'
# # })

# # # ----------------------- Spell Checker -----------------------
# # sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# # dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
# # sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# # # ----------------------- Session State -----------------------
# # for var in ['input_text', 'output_text', 'user_dict', 'conversion_mode', 'keyboard_char', 'clear_flag']:
# #     if var not in st.session_state:
# #         st.session_state[var] = "" if var in ['input_text', 'output_text', 'keyboard_char'] else []

# # # ----------------------- Functions -----------------------
# # def auto_correct_sentence(text):
# #     words = re.findall(r'\w+|\s+|[^\w\s]', text)
# #     corrected = []
# #     for word in words:
# #         if word.strip():
# #             suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
# #             corrected.append(suggestions[0].term if suggestions else word)
# #         else:
# #             corrected.append(word)
# #     corrected_text = ''.join(corrected)
# #     blob = TextBlob(corrected_text)
# #     return str(blob.correct())

# # def braille_to_text_conversion(braille_str):
# #     raw = []
# #     i = 0
# #     while i < len(braille_str):
# #         if i + 1 < len(braille_str):
# #             two_char = braille_str[i:i+2]
# #             if two_char in braille_to_text:
# #                 raw.append(braille_to_text[two_char])
# #                 i += 2
# #                 continue
# #         raw.append(braille_to_text.get(braille_str[i], '?'))
# #         i += 1
# #     return auto_correct_sentence(''.join(raw))

# # def text_to_braille_conversion(text_str):
# #     braille_str = []
# #     text_str = text_str.lower()
# #     for char in text_str:
# #         braille_str.append(text_to_braille.get(char, '?'))
# #     return ''.join(braille_str)

# # def handle_pdf_upload():
# #     uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
# #     if uploaded_file is not None:
# #         with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
# #             text = ""
# #             for page in doc:
# #                 text += page.get_text()
# #             st.session_state.input_text = text

# # def update_dictionary(new_word):
# #     if new_word and new_word not in st.session_state.user_dict:
# #         st.session_state.user_dict.append(new_word)
# #         with open("user_dictionary.json", "w") as f:
# #             json.dump(st.session_state.user_dict, f)
# #         st.sidebar.success(f"'{new_word}' added to dictionary!")
# #     elif new_word in st.session_state.user_dict:
# #         st.sidebar.warning("Word already in dictionary!")

# # def show_braille_keyboard():
# #     st.subheader("Virtual Braille Keyboard")
# #     chars = [c for c in braille_to_text if c not in ("⠀", " ")]
# #     cols = st.columns(6)
# #     for i, char in enumerate(chars):
# #         with cols[i % 6]:
# #             if st.button(char, key=f"kb_{i}"):
# #                 st.session_state.input_text += char

# # # ----------------------- UI -----------------------
# # st.title("🔠 BrailleXpert")

# # with st.sidebar:
# #     st.header("Controls")
# #     st.session_state.conversion_mode = st.radio(
# #         "Conversion Mode",
# #         ("text_to_braille", "braille_to_text"),
# #         format_func=lambda x: "Text to Braille" if x == "text_to_braille" else "Braille to Text"
# #     )

# #     handle_pdf_upload()

# #     st.header("Dictionary Management")
# #     new_word = st.text_input("Add new word to dictionary")
# #     if st.button("Add to Dictionary"):
# #         update_dictionary(new_word)

# #     if st.button("Show Dictionary"):
# #         st.write("User Dictionary:", st.session_state.user_dict)

# # # Input Text
# # input_text = st.text_area("Input Text", height=150, value=st.session_state.input_text, key="input_area")
# # st.session_state.input_text = input_text  # Sync input_text with session state

# # # Buttons
# # col1, col2, col3 = st.columns([2, 2, 2])
# # with col1:
# #     if st.button("Convert"):
# #         if st.session_state.conversion_mode == "text_to_braille":
# #             st.session_state.output_text = text_to_braille_conversion(st.session_state.input_text)
# #         else:
# #             st.session_state.output_text = braille_to_text_conversion(st.session_state.input_text)
# # with col2:
# #     if st.button("Clear All"):
# #         st.session_state.input_text = ""
# #         st.session_state.output_text = ""
# # # Replace the existing "Copy Result" button code with this:
# # # In the button section:
# # with col3:
# #     if st.button("Copy Result"):
# #         if st.session_state.output_text:
# #             # Using Streamlit's own text area for easy copy/paste
# #             st.text_area("Output", value=st.session_state.output_text, height=150, key="output_area")
# #             st.success("Ready to copy!")
# #         else:
# #             st.warning("Nothing to copy!")


# # # Conversion Output
# # if st.session_state.output_text:
# #     st.subheader("Conversion Result")
# #     st.text_area("Output", value=st.session_state.output_text, height=150, key="output_area")
# #     # Using a unique key for the output text area
# # # Change the output text area to have a fixed ID
   
# # # Virtual Braille Keyboard
# # show_braille_keyboard()

# # # Styling
# # st.markdown("""
# # <style>
# #     .stTextArea textarea {
# #         background-color: #f0f8ff;
# #     }
# #     .stButton button {
# #         width: 100%;
# #         transition: all 0.3s ease;
# #     }
# #     .stButton button:hover {
# #         transform: scale(1.05);
# #     }
# # </style>
# # """, unsafe_allow_html=True)
























# # requirements.txt
# # streamlit
# # pymupdf
# # transformers
# # symspellpy
# # torch

# import streamlit as st
# import fitz  # PyMuPDF
# from transformers import pipeline
# import tempfile
# import os

# # ----------------------- Braille Mappings -----------------------
# braille_to_text = {
#     '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
#     '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
#     '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
#     '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
#     '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
#     '⠵': 'z',' ':' ','⠀':' ','?':'?'
# }

# text_to_braille = {v:k for k,v in braille_to_text.items()}

# # ----------------------- Helper Functions -----------------------
# def extract_text_from_pdf(pdf_path):
#     """Extract text from PDF using PyMuPDF"""
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text

# def summarize_text(text):
#     """Summarize text using Transformers pipeline"""
#     summarizer = pipeline("summarization")
#     return summarizer(text, max_length=200, min_length=50, do_sample=False)[0]['summary_text']

# def convert_to_braille(text):
#     """Convert text to simple braille mapping"""
#     return ''.join([text_to_braille.get(char.lower(), char) for char in text])

# # ----------------------- Streamlit UI -----------------------
# st.title("Healthcare Report to Braille Converter")
# st.markdown("Upload your healthcare PDF to get a Braille summary")

# uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# if uploaded_file is not None:
#     # Save uploaded file to temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(uploaded_file.getvalue())
#         tmp_path = tmp_file.name

#     # Process PDF
#     with st.spinner("Processing your document..."):
#         try:
#             # Extract text
#             raw_text = extract_text_from_pdf(tmp_path)
            
#             # Summarize
#             summary = summarize_text(raw_text)
            
#             # Convert to Braille
#             braille_output = convert_to_braille(summary)
            
#             # Display results
#             st.subheader("Report Summary")
#             st.write(summary)
            
#             st.subheader("Braille Output")
#             st.code(braille_output)
            
#             # Download button for Braille
#             st.download_button(
#                 label="Download Braille File",
#                 data=braille_output,
#                 file_name="healthcare_braille.txt",
#                 mime="text/plain"
#             )
            
#         except Exception as e:
#             st.error(f"Error processing file: {str(e)}")
#         finally:
#             os.unlink(tmp_path)  # Clean up temp file

# # ----------------------- Sidebar Info -----------------------
# st.sidebar.header("About")
# st.sidebar.info(
#     "This application converts healthcare PDF reports into summarized Braille documents "
#     "for visually impaired users. The system:\n"
#     "1. Extracts text from PDF\n"
#     "2. Generates a summary using AI\n"
#     "3. Converts the summary to Braille\n\n"
#     "Note: This is a prototype using basic Braille mapping. For production use, "
#     "consider using the liblouis library for full Braille specification support."
# )









# requirements.txt
"""
# streamlit==1.29.0
# pymupdf==1.23.8
# transformers==4.36.2
# torch==2.1.2
# python-louis==3.27.0
# pdf2image==1.16.3
# pytesseract==0.3.10
# gtts==2.4.0
# flashtext==2.7
# """

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
                st.subheader("🖇️ Braille Output")
                st.markdown(f"```braille\n{braille_output}\n```")
                
                # Braille Download
                st.download_button(
                    label="⬇️ Download Braille File",
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
                        label="⬇️ Download Audio",
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
    **Features:**
    - PDF text extraction (including scanned docs)
    - AI-powered medical summarization
    - Grade 2 Braille conversion
    - Audio summary generation
    - Key medical term highlighting
    - High contrast mode

    **System Requirements:**
    - Tesseract OCR installed
    - liblouis tables available
    """)

    st.markdown("---")
    st.markdown("⚠️ **Important Notes:**\n"
                "- Always verify Braille accuracy before clinical use\n"
                "- Protected Health Information (PHI) is processed temporarily\n"
                "- Consult original documents for critical decisions")

# ----------------------- System Checks -----------------------
try:
    louis.translateString(["en-ueb-g2.ctb"], "test")[0]
except Exception as e:
    st.error("Braille system not configured properly. Install liblouis and Braille tables.")
