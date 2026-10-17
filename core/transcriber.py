import os

import whisper

from utils.ffmpeg_setup import ensure_ffmpeg


_model = None


def load_model():
    """Load Whisper once. Whisper itself shells out to ffmpeg, so verify it first."""

    global _model

    if _model is None:
        ensure_ffmpeg()

        name = os.getenv("WHISPER_MODEL", "base")
        print(f"Loading Whisper model: {name}")
        _model = whisper.load_model(name)
        print("Whisper model loaded successfully")

    return _model


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:

    model = load_model()
    language = language.lower()

    options = {"task": "transcribe", "fp16": False}

    if language == "english":
        options["language"] = "en"

    elif language == "hindi":
        options["language"] = "hi"

    elif language == "hinglish":
        # No dedicated Hinglish mode: auto-detect, and nudge towards Roman script
        options["initial_prompt"] = "Namaste, aaj hum is meeting mein project ke baare mein baat karenge."

    result = model.transcribe(chunk_path, **options)
    return result["text"]


def transcribe_all(chunks: list, language: str = "english") -> str:

    parts = []

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}")
        text = transcribe_chunk(chunk, language=language).strip()
        if text:
            parts.append(text)

    transcript = " ".join(parts).strip()

    if not transcript:
        raise ValueError("No speech was detected in the audio.")

    print("Transcription completed")
    return transcript