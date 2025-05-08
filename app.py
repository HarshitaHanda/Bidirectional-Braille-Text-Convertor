import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from sklearn.preprocessing import LabelEncoder

# ----------------------- Braille to English Mapping -----------------------
braille_dict = {
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
    '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
    '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
    '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
    '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y', '⠵': 'z',
    ' ': ' '
}

# ----------------------- Prepare Dataset -----------------------
braille_chars = list(braille_dict.keys())
english_chars = [braille_dict[b] for b in braille_chars]

# Encode input and output
input_encoder = LabelEncoder()
output_encoder = LabelEncoder()

X = input_encoder.fit_transform(braille_chars)
y = output_encoder.fit_transform(english_chars)

X = np.array(X).reshape(-1, 1)
y = tf.keras.utils.to_categorical(y, num_classes=len(set(y)))

# ----------------------- Define RNN-LSTM Model -----------------------
model = Sequential()
model.add(Embedding(input_dim=len(input_encoder.classes_), output_dim=8, input_length=1))
model.add(LSTM(32, return_sequences=False))
model.add(Dense(len(set(output_encoder.classes_)), activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# Train the model
model.fit(X, y, epochs=300, verbose=0)

# ----------------------- Inference Function -----------------------
def predict_braille(braille_input):
    result = ''
    for ch in braille_input:
        if ch not in braille_dict:
            result += '?'
            continue
        encoded = input_encoder.transform([ch])
        pred = model.predict(np.array(encoded).reshape(1, 1), verbose=0)
        predicted_idx = np.argmax(pred, axis=1)
        predicted_char = output_encoder.inverse_transform(predicted_idx)[0]
        result += predicted_char
    return result

# ----------------------- Streamlit UI -----------------------
st.title("🔠 Braille to English Conversion")

st.sidebar.header("Settings")
user_input = st.sidebar.text_area("Enter Braille (Unicode format, e.g., ⠓⠑⠇⠇⠕):")

# Prediction section
if user_input:
    st.subheader("Predicted English Text:")
    output_text = predict_braille(user_input)
    st.write(output_text)

# Display instructions and Braille dictionary
st.sidebar.write("""
### Braille to English Conversion
This app converts Braille characters into English text using a trained deep learning model.
- Enter Braille text in the left sidebar.
- The predicted English translation will be displayed in the main area.
""")
st.sidebar.write("### Braille Mapping Example:")
st.sidebar.write(braille_dict)

# ----------------------- Error Handling -----------------------
if user_input == "":
    st.warning("Please enter Braille text to see the prediction!")
