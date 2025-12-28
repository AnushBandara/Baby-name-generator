from fastapi import FastAPI, Form, HTTPException
import uvicorn
import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# Paths & model loading
# ----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH_MALE = os.path.join(
    BASE_DIR, "Models", "baby_name_male_lstm_v1.keras"
)
MODEL_PATH_FEMALE = os.path.join(
    BASE_DIR, "Models", "baby_name_female_lstm_v1.keras"
)

MALE_MODEL = tf.keras.models.load_model(MODEL_PATH_MALE)
FEMALE_MODEL = tf.keras.models.load_model(MODEL_PATH_FEMALE)

# Map gender to model for cleaner routing
MODEL_MAP = {
    "male": MALE_MODEL,
    "female": FEMALE_MODEL,
}

# ----------------------------
# Token config (must match training)
# ----------------------------

letter_tokens = {
    "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10,
    "k": 11, "l": 12, "m": 13, "n": 14, "o": 15, "p": 16, "q": 17, "r": 18, "s": 19,
    "t": 20, "u": 21, "v": 22, "w": 23, "x": 24, "y": 25, "z": 26, "<end>": 27
}

PAD_ID = 0
END_ID = letter_tokens["<end>"]
index_to_char = {idx: ch for ch, idx in letter_tokens.items()}


# Convert a word to a sequence of ints + <end> token
def word_to_sequence(word: str):
    return [letter_tokens[char] for char in word if char in letter_tokens] + [END_ID]


# ----------------------------
# Name generator function
# ----------------------------

def name_generator(
    first_letters: str,
    min_length: int,
    max_length: int,
    model,
    max_sequence_len: int = 16,
) -> str:
    name = first_letters.lower()

    while len(name) < max_length:
        # Convert name into token ids (drop auto-added <end>)
        token_list = word_to_sequence(name)[:-1]

        token_list = pad_sequences(
            [token_list],
            maxlen=max_sequence_len - 1,
            padding="pre",
            value=PAD_ID,
        )

        preds = model.predict(token_list, verbose=0)[0]

        # Before min_length: force a non-END, non-PAD character
        if len(name) < min_length:
            sorted_ids = np.argsort(preds)[::-1]  # highest prob first
            next_id = None
            for idx in sorted_ids:
                if idx not in (PAD_ID, END_ID):
                    next_id = int(idx)
                    break
            if next_id is None:
                break
        else:
            # After min_length: allow END/PAD to terminate
            next_id = int(np.argmax(preds))
            if next_id in (PAD_ID, END_ID):
                break

        next_char = index_to_char[next_id]
        name += next_char

    return name.capitalize()


# ----------------------------
# FastAPI app + CORS
# ----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins (localhost + Netlify, etc.)
    allow_credentials=False,    # must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Baby name generator API!"}


@app.post("/names/")
async def generate_name(
    letters: str = Form(...),
    gender: str = Form(...),
    max_length: int = Form(10),
    min_length: int = Form(3),
):
    # Clean and validate letters
    letters = letters.strip().lower()
    letters = "".join(ch for ch in letters if ch in letter_tokens and ch != "<end>")

    if not letters:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one valid letter (a-z).",
        )

    # Ensure min_length respects seed length
    if min_length < len(letters):
        min_length = len(letters)

    if min_length > max_length:
        raise HTTPException(
            status_code=400,
            detail="min_length cannot be greater than max_length.",
        )

    gender_key = gender.lower()
    if gender_key not in MODEL_MAP:
        raise HTTPException(status_code=400, detail="Invalid gender specified")

    model = MODEL_MAP[gender_key]

    generated_name = name_generator(
        first_letters=letters,
        min_length=min_length,
        max_length=max_length,
        model=model,
        max_sequence_len=16,  # must match training setting
    )

    return {"name": generated_name}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)