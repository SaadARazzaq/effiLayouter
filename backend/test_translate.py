import subprocess
import sys

# Ensure spaCy model is installed
def install_spacy_model(model="en_core_web_lg"):
    try:
        import spacy
        spacy.load(model)
    except OSError:
        print(f"Downloading spaCy model '{model}'...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
    except ImportError:
        print("spaCy is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model])

# Run installer before use
install_spacy_model()

import spacy
nlp = spacy.load("en_core_web_lg")

def is_name(text: str) -> bool:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.text.lower() == text.lower():
            return True
    return False


# ---- Test cases ----
print(is_name("saad abdur razzaq"))   # True
print(is_name("michael coffee"))      # True
print(is_name("apple"))               # True
print(is_name("this is a test"))      # False
print(is_name("effixly"))      # True
print(is_name("efficia"))      # True