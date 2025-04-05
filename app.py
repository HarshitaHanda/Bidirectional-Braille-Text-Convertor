import streamlit as st
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
import fitz
import json
from textblob import TextBlob

# ----------------------- Braille Mappings -----------------------
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
    '⠮': '*', '⠢': '$', '⠶': '_'
}

text_to_braille = {v: k for k, v in braille_to_text.items()}
text_to_braille.update({
    '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
    '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚'
})

# ----------------------- Spell Checker -----------------------
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# ----------------------- Session State -----------------------
for var in ['input_text', 'output_text', 'user_dict', 'conversion_mode', 'keyboard_char', 'clear_flag']:
    if var not in st.session_state:
        st.session_state[var] = "" if var in ['input_text', 'output_text', 'keyboard_char'] else []

# ----------------------- Functions -----------------------
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

def update_dictionary(new_word):
    if new_word and new_word not in st.session_state.user_dict:
        st.session_state.user_dict.append(new_word)
        with open("user_dictionary.json", "w") as f:
            json.dump(st.session_state.user_dict, f)
        st.sidebar.success(f"'{new_word}' added to dictionary!")
    elif new_word in st.session_state.user_dict:
        st.sidebar.warning("Word already in dictionary!")

def show_braille_keyboard():
    st.subheader("Virtual Braille Keyboard")
    chars = [c for c in braille_to_text if c not in ("⠀", " ")]
    cols = st.columns(6)
    for i, char in enumerate(chars):
        with cols[i % 6]:
            if st.button(char, key=f"kb_{i}"):
                st.session_state.input_text += char

# ----------------------- UI -----------------------
st.title("🔠 Enhanced Braille Converter")

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

# Input Text
input_text = st.text_area("Input Text", height=150, value=st.session_state.input_text, key="input_area")
st.session_state.input_text = input_text  # Sync input_text with session state

# Buttons
col1, col2, col3 = st.columns([2, 2, 2])
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
        if st.session_state.output_text:
            # Using Streamlit's own text area for easy copy/paste
            st.text_area("Output", value=st.session_state.output_text, height=150, key="output_area")
            st.success("Ready to copy!")
        else:
            st.warning("Nothing to copy!")

# Conversion Output
if st.session_state.output_text:
    st.subheader("Conversion Result")
    # Using a unique key for the output text area
    st.text_area("Output", value=st.session_state.output_text, height=150, key="output_area_unique")

# Virtual Braille Keyboard
show_braille_keyboard()

# Styling
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
