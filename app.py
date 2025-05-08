import streamlit as st
import re
from symspellpy import SymSpell
import pkg_resources

# Braille-Text Mappings (Unicode Braille characters)
braille_to_text = {
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
    '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
    '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
    '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
    '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
    '⠵': 'z', ' ': ' ', '⠀': ' '  # Adding Braille space
}

text_to_braille = {v: k for k, v in braille_to_text.items()}

# Initialize SymSpell for spell correction
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Enhanced Auto-Correction for Full Sentences
def auto_correct_sentence(text):
    """
    Applies auto-correction at the sentence level, preserving punctuation and spaces.
    """
    words = re.findall(r'\w+|\s+|[^\w\s]', text)  # Tokenize words while keeping punctuation and spaces
    corrected_words = []

    for word in words:
        if word.strip():  # Only process actual words, leave spaces/punctuation as they are
            suggestions = sym_spell.lookup(word, symspellpy.Verbosity.CLOSEST, max_edit_distance=2)
            corrected_word = suggestions[0].term if suggestions else word
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)  # Preserve spaces and punctuation

    return ''.join(corrected_words)  # Reassemble sentence with corrections

# Conversion Functions
def braille_to_text_conversion(braille_str):
    """
    Converts Braille to text and applies sentence-level auto-correction.
    """
    text = ''.join([braille_to_text.get(c, '?') for c in braille_str])
    return auto_correct_sentence(text)  # Apply AI-based auto-correction

def text_to_braille_conversion(text_str):
    """
    Converts English text to Braille.
    """
    return ''.join([text_to_braille.get(c.lower(), '?') for c in text_str])

# Streamlit UI
st.title("Braille Text Converter")

st.markdown("This app converts **Text to Braille** and **Braille to Text**. You can also correct common spelling errors automatically.")

# Input for Mode Selection
mode = st.radio("Choose Mode", ["Text to Braille", "Braille to Text"])

# Text input
input_text = st.text_area("Enter text or Braille", height=150)

if mode == "Text to Braille":
    if st.button("Convert to Braille"):
        result = text_to_braille_conversion(input_text)
        st.write("Converted Braille:", result)
        
elif mode == "Braille to Text":
    if st.button("Convert to Text"):
        result = braille_to_text_conversion(input_text)
        st.write("Converted Text:", result)

# Downloadable Converted Output
if result:
    st.download_button(
        label="Download Output",
        data=result,
        file_name="braille_output.txt",
        mime="text/plain"
    )
