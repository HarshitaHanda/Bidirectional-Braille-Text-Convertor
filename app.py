import streamlit as st
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
import fitz  # PyMuPDF
import json
import pyperclip
from textblob import TextBlob

# Initialize Braille mappings and spell checker
braille_to_text = {
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
    '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
    '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
    '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
    '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
    '⠵': 'z',
    '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4', '⠼⠑': '5',
    '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8', '⠼⠊': '9', '⠼⠚': '0',
    '⠀': ' ', '⠂': ',', '⠲': '.', '⠦': '?', '⠤': '-',
    '⠖': '!', '⠴': ':', '⠰': '#', '⠔': '"', '⠣': ';',
    '⠷': '(', '⠾': ')', '⠡': '+', '⠯': '=',
    '⠮': '*', '⠾': ']', '⠢': '$', '⠶': '_'
}

text_to_braille = {v: k for k, v in braille_to_text.items()}

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Session state initialization
if 'output_text' not in st.session_state:
    st.session_state.output_text = ""
if 'user_dict' not in st.session_state:
    try:
        with open("user_dictionary.json", "r") as f:
            st.session_state.user_dict = json.load(f)
    except:
        st.session_state.user_dict = []
if 'conversion_mode' not in st.session_state:
    st.session_state.conversion_mode = "text_to_braille"

# Helper functions
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
    raw = []
    i = 0
    while i < len(braille_str):
        if i + 1 < len(braille_str):
            two_char = braille_str[i:i+2]
            if two_char in braille_to_text:
                raw.append(braille_to_text[two_char])
                i += 2
                continue
        raw.append(braille_to_text.get(braille_str[i], '?'))
        i += 1
    return auto_correct_sentence(''.join(raw))

def text_to_braille_conversion(text_str):
    braille_str = []
    text_str = text_str.lower()
    for char in text_str:
        if char.isdigit():
            braille_str.append(text_to_braille.get(f'⠼{char}', '?'))
        else:
            braille_str.append(text_to_braille.get(char, '?'))
    return ''.join(braille_str)

def handle_pdf_upload():
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            st.session_state.input_text = text

def show_braille_keyboard():
    st.subheader("Virtual Braille Keyboard")
    chars = [c for c in braille_to_text if c not in ("⠀", " ")]
    cols = st.columns(6)
    for i, char in enumerate(chars):
        with cols[i % 6]:
            if st.button(char, key=f"kb_{i}"):
                if 'input_text' not in st.session_state:
                    st.session_state.input_text = ""
                st.session_state.input_text += char

def update_dictionary(new_word):
    if new_word and new_word not in st.session_state.user_dict:
        st.session_state.user_dict.append(new_word)
        with open("user_dictionary.json", "w") as f:
            json.dump(st.session_state.user_dict, f)
        st.sidebar.success(f"'{new_word}' added to dictionary!")
    elif new_word in st.session_state.user_dict:
        st.sidebar.warning("Word already in dictionary!")

# UI Layout
st.title("Enhanced Braille Converter")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    st.session_state.conversion_mode = st.radio(
        "Conversion Mode",
        ("text_to_braille", "braille_to_text"),
        format_func=lambda x: "Text to Braille" if x == "text_to_braille" else "Braille to Text"
    )
    
    handle_pdf_upload()
    
    st.header("Dictionary Management")
    new_word = st.text_input("Add new word to dictionary")
    if st.button("Add to Dictionary"):
        update_dictionary(new_word)
    
    if st.button("Show Dictionary"):
        st.write("User Dictionary:", st.session_state.user_dict)

# Main content
input_text = st.text_area(
    "Input Text", 
    height=150,
    key="input_text"
)

col1, col2, col3 = st.columns([2,2,2])
with col1:
    if st.button("Convert"):
        if st.session_state.conversion_mode == "text_to_braille":
            st.session_state.output_text = text_to_braille_conversion(st.session_state.input_text)
        else:
            st.session_state.output_text = braille_to_text_conversion(st.session_state.input_text)
with col2:
    if st.button("Clear All"):
        st.session_state.input_text = ""
        st.session_state.output_text = ""
with col3:
    if st.button("Copy Result"):
        pyperclip.copy(st.session_state.output_text)
        st.success("Copied to clipboard!")

show_braille_keyboard()

if st.session_state.output_text:
    st.subheader("Conversion Result")
    st.text_area("Output", value=st.session_state.output_text, height=150, key="output_area")

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextArea textarea {
        background-color: #f0f8ff;
    }
    .stButton button {
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)
