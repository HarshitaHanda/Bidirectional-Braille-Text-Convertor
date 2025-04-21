# requirements.txt
--find-links https://download.pytorch.org/whl/cpu/torch_stable.html

streamlit==1.29.0
pymupdf==1.23.8
transformers==4.36.2
torch==2.1.2+cpu
pdf2image==1.16.3
pytesseract==0.3.10
gtts==2.4.0
flashtext==2.7
python-dotenv==1.0.0

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
    'a': '⠁','b': '⠃','c': '⠉','d': '⠙','e': '⠑',
    'f': '⠋','g': '⠛','h': '⠓','i': '⠊','j': '⠚',
    'k': '⠅','l': '⠇','m': '⠍','n': '⠝','o': '⠕',
    'p': '⠏','q': '⠟','r': '⠗','s': '⠎','t': '⠞',
    'u': '⠥','v': '⠧','w': '⠺','x': '⠭','y': '⠽','z': '⠵',
    '0': '⠚','1': '⠁','2': '⠃','3': '⠉','4': '⠙',
    '5': '⠑','6': '⠋','7': '⠛','8': '⠓','9': '⠊',
    ' ': '⠀','.': '⠲',',': '⠂','?': '⠦','!': '⠖',
    "'": '⠄','-': '⠤','(': '⠐⠣',')': '⠐⠜',
    '#': '⠼','cap': '⠠'
}

CONTRACTIONS = {
    'the': '⠮','and': '⠯','for': '⠿','of': '⠷','with': '⠾',
    'will': '⠂','his': '⠦','was': '⠫','this': '⠇','have': '⠬'
}

MEDICAL_TERMS = ['diagnosis','prescription','symptoms','treatment','medication',
                 'dose','allergy','test results','prognosis','recommendation']

# ----------------------- Helper Functions -----------------------
def enhanced_braille_convert(text: str, use_contractions: bool = True) -> str:
    if use_contractions:
        for word, symbol in CONTRACTIONS.items():
            text = text.replace(word, symbol)
    result, prev = [], ''
    for ch in text:
        if ch.isdigit():
            if prev != '#': result.append(BRAILLE_MAP['#'])
            result.append(BRAILLE_MAP[ch])
        elif ch.isupper():
            result.append(BRAILLE_MAP['cap'])
            result.append(BRAILLE_MAP.get(ch.lower(), ch))
        else:
            result.append(BRAILLE_MAP.get(ch.lower(), ch))
        prev = ch
    return ''.join(result)


def extract_text_from_pdf(path: str, use_ocr: bool = False) -> str:
    if use_ocr:
        try:
            images = convert_from_path(path)
            return '\n'.join(pytesseract.image_to_string(img) for img in images)
        except Exception as e:
            st.error(f'OCR Error: {e}')
            return ''
    try:
        doc = fitz.open(path)
        text = '\n'.join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        st.error(f'PDF Error: {e}')
        return ''


def highlight_medical(text: str) -> str:
    for term in MEDICAL_TERMS:
        text = text.replace(term, f'**{term}**')
    return text


def generate_audio(text: str, lang: str = 'en') -> str:
    try:
        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        gTTS(text=text, lang=lang).save(tf.name)
        return tf.name
    except Exception as e:
        st.error(f'Audio Error: {e}')
        return ''

# ----------------------- Streamlit App -----------------------
st.set_page_config(page_title='MedBraille', page_icon='♿', layout='wide')

st.sidebar.header('Settings')
use_ocr = st.sidebar.checkbox('Enable OCR for scanned PDFs')
use_contractions = st.sidebar.checkbox('Use Braille Contractions', True)
audio_enabled = st.sidebar.checkbox('Generate Audio', True)
dark_mode = st.sidebar.checkbox('High Contrast Mode')

if dark_mode:
    st.markdown("""
    <style>
      .stApp { background-color:#1a1a1a; color:#e6e6e6; }
    </style>
    """, unsafe_allow_html=True)

st.title('📄 Medical Report to Braille Converter')
uploaded = st.file_uploader('Upload Medical PDF', type=['pdf'])

if uploaded:
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf.write(uploaded.read())
    temp_pdf.close()
    audio_file = ''
    try:
        with st.spinner('Processing...'):
            txt = extract_text_from_pdf(temp_pdf.name, use_ocr)
            if not txt:
                st.error('No text extracted')
                st.stop()
            highlighted = highlight_medical(txt)
            summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
            summary = summarizer(highlighted, max_length=300, min_length=100)[0]['summary_text']
            braille = enhanced_braille_convert(summary, use_contractions)
            if audio_enabled:
                audio_file = generate_audio(summary)
        c1, c2 = st.columns([2,1])
        with c1:
            st.subheader('Summary')
            st.write(summary)
        with c2:
            st.subheader('Braille')
            st.code(braille, language='plaintext')
            st.download_button('Download .brf', braille.encode('utf-8'), 'report.brf')
            if audio_file:
                st.subheader('Audio')
                st.audio(audio_file)
                with open(audio_file, 'rb') as f:
                    st.download_button('Download MP3', f.read(), 'summary.mp3')
    except Exception as e:
        st.error(f'Error: {e}')
    finally:
        os.remove(temp_pdf.name)
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)

with st.expander('How to Use'):
    st.markdown('1. Upload PDF\n2. Adjust settings\n3. Download outputs')

st.caption('Prototype—verify Braille accuracy yourself.')
