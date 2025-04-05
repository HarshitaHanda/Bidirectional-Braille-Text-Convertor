import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
import fitz  # PyMuPDF for PDF extraction
import json  # For storing dictionary
import pyperclip  # For copying text to clipboard
from textblob import TextBlob  # Added missing import

# Corrected Braille mappings with proper number handling
braille_to_text = {
    # Letters
    '⠁': 'a', '⠃': 'b', '⠉': 'c', '⠙': 'd', '⠑': 'e',
    '⠋': 'f', '⠛': 'g', '⠓': 'h', '⠊': 'i', '⠚': 'j',
    '⠅': 'k', '⠇': 'l', '⠍': 'm', '⠝': 'n', '⠕': 'o',
    '⠏': 'p', '⠟': 'q', '⠗': 'r', '⠎': 's', '⠞': 't',
    '⠥': 'u', '⠧': 'v', '⠺': 'w', '⠭': 'x', '⠽': 'y',
    '⠵': 'z',
    
    # Numbers (with numeric prefix ⠼)
    '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4', '⠼⠑': '5',
    '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8', '⠼⠊': '9', '⠼⠚': '0',
    
    # Punctuation and symbols
    '⠀': ' ', '⠂': ',', '⠲': '.', '⠦': '?', '⠤': '-',
    '⠖': '!', '⠴': ':', '⠰': '#', '⠔': '"', '⠣': ';',
    '⠷': '(', '⠾': ')', '⠡': '+', '⠯': '=',
    '⠮': '*', '⠾': ']', '⠢': '$', '⠶': '_'
}

text_to_braille = {v: k for k, v in braille_to_text.items()}

# Spell Correction using SymSpell
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

# Auto-correction function
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
    """
    Converts Braille to text and applies sentence-level auto-correction.
    This version handles multi-character Braille sequences (for letters, numbers, and punctuation).
    """
    raw = []
    i = 0
    while i < len(braille_str):
        # Check for 2-character sequences first (e.g., numbers with the ⠼ prefix)
        if i + 1 < len(braille_str):
            two_char = braille_str[i:i+2]
            if two_char in braille_to_text:
                raw.append(braille_to_text[two_char])
                i += 2  # Move forward by 2
                continue
        # Handle single characters
        raw.append(braille_to_text.get(braille_str[i], '?'))  # Use '?' for unsupported characters
        i += 1
    # Convert to text and apply auto-correction (spelling & grammar)
    return auto_correct_sentence(''.join(raw))

def text_to_braille_conversion(text_str):
    """
    Converts English text to Braille.
    """
    braille_str = []
    text_str = text_str.lower()
    for char in text_str:
        # Handle numbers with prefix
        if char.isdigit():
            braille_str.append(text_to_braille.get(f'⠼{char}', '?'))  # Add numeric prefix ⠼
        else:
            braille_str.append(text_to_braille.get(char, '?'))  # Replace with '?' if not found
    return ''.join(braille_str)

# PDF extraction function
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Dictionary Management
class Dictionary:
    def __init__(self, filepath="user_dictionary.json"):
        self.filepath = filepath
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as file:
                self.words = json.load(file)
        except FileNotFoundError:
            self.words = []

    def save(self):
        with open(self.filepath, "w") as file:
            json.dump(self.words, file)

    def add(self, word):
        if word not in self.words:
            self.words.append(word)
            self.save()
        else:
            messagebox.showinfo("Info", "Word already in dictionary!")

    def get_all(self):
        return self.words

# GUI Application
class BrailleConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enhanced Braille Converter")
        self.geometry("900x650")
        self.create_widgets()
        self.dictionary = Dictionary()

    def create_widgets(self):
        # Heading label
        self.heading = ttk.Label(self, text="Braille Converter", font=("Arial", 24, "bold"), foreground="#007acc")
        self.heading.pack(pady=10)

        # Mode selection
        self.mode_var = tk.StringVar(value="text_to_braille")
        ttk.Label(self, text="Conversion Mode:", font=("Arial", 14)).pack(pady=5)
        mode_frame = ttk.Frame(self)
        mode_frame.pack(pady=5)

        ttk.Radiobutton(mode_frame, text="Text to Braille", variable=self.mode_var, value="text_to_braille").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Braille to Text", variable=self.mode_var, value="braille_to_text").pack(side=tk.LEFT, padx=10)

        # Input field
        self.input_text = tk.Text(self, height=5, wrap=tk.WORD, font=("Arial", 12), bd=2, relief="solid", bg="#f0f8ff", width=50)
        self.input_text.pack(pady=10)

        # Conversion button
        ttk.Button(self, text="Convert", command=self.perform_conversion, style="TButton").pack(pady=5)

        # Result display
        self.result_text = tk.Text(self, height=5, wrap=tk.WORD, font=("Arial", 12), state=tk.DISABLED, bg="#e0f7fa", width=50)
        self.result_text.pack(pady=10)

        # Buttons in horizontal layout
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Upload PDF", command=self.upload_pdf).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Virtual Braille Keyboard", command=self.show_braille_keyboard).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Toggle Theme", command=self.toggle_theme).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Dictionary", command=self.show_dictionary).pack(side=tk.LEFT, padx=10)

        # Copy Button at the bottom-right corner of the result text box
        self.copy_button = ttk.Button(self, text="Copy", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.BOTTOM, anchor="se", pady=10)

    def perform_conversion(self):
        input_content = self.input_text.get("1.0", tk.END).strip()
        mode = self.mode_var.get()

        if mode == "text_to_braille":
            result = text_to_braille_conversion(input_content)
        else:
            result = braille_to_text_conversion(input_content)

        self.show_result(result)

    def show_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def upload_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            extracted_text = extract_text_from_pdf(pdf_path)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, extracted_text)
            self.perform_conversion()

    def show_braille_keyboard(self):
        kb = tk.Toplevel(self)
        kb.title("Braille Keyboard")
        chars = [c for c in braille_to_text if c not in ("⠀", " ")]

        for idx, char in enumerate(chars):
            btn = ttk.Button(kb, text=char, width=3, command=lambda c=char: self.insert_character(c))
            btn.grid(row=idx // 6, column=idx % 6, padx=2, pady=2)

    def insert_character(self, char):
        self.input_text.insert(tk.END, char)
        self.perform_conversion()

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)

    def toggle_theme(self):
        current_bg = self.cget("bg")
        if current_bg == "#f5f5f5":  # Light theme
            self.configure(bg="#333333")
            self.input_text.config(bg="#555555", fg="white")
            self.result_text.config(bg="#444444", fg="white")
            self.configure_theme_buttons("dark")
        else:  # Dark theme
            self.configure(bg="#f5f5f5")
            self.input_text.config(bg="#f5f5f5", fg="black")
            self.result_text.config(bg="#e0f7fa", fg="black")
            self.configure_theme_buttons("light")

    def configure_theme_buttons(self, theme):
        buttons = self.winfo_children()
        for button in buttons:
            if isinstance(button, ttk.Button):
                if theme == "dark":
                    button.config(style="Dark.TButton")
                else:
                    button.config(style="TButton")

    def show_dictionary(self):
        dictionary_window = tk.Toplevel(self)
        dictionary_window.title("Dictionary")
        
        word_list = self.dictionary.get_all()
        listbox = tk.Listbox(dictionary_window, width=40, height=10)
        listbox.pack(padx=20, pady=20)

        for word in word_list:
            listbox.insert(tk.END, word)

        ttk.Label(dictionary_window, text="Add New Word:", font=("Arial", 12)).pack(pady=5)
        new_word_entry = ttk.Entry(dictionary_window, width=20)
        new_word_entry.pack(pady=5)
        ttk.Button(dictionary_window, text="Add", command=lambda: self.add_word(new_word_entry.get(), dictionary_window)).pack(pady=5)

    def add_word(self, word, window):
        if word:
            self.dictionary.add(word)
            messagebox.showinfo("Success", f"'{word}' added to dictionary!")
            window.destroy()

    def copy_to_clipboard(self):
        result_content = self.result_text.get("1.0", tk.END).strip()
        pyperclip.copy(result_content)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

if __name__ == "__main__":
    app = BrailleConverterApp()
    app.mainloop()
