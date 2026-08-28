import os
import whisper


# ============================================================
# FFmpeg Configuration
# ============================================================

# Streamlit Cloud installs FFmpeg using packages.txt:
#
# packages.txt
# ------------
# ffmpeg
#
# Therefore we don't use a Windows-specific path here.

FFMPEG_PATH = "ffmpeg"
FFPROBE_PATH = "ffprobe"


# ============================================================
# Add FFmpeg to PATH
# ============================================================

# Linux / Streamlit Cloud already has ffmpeg in PATH.
# This also works if ffmpeg is installed locally.

os.environ["PATH"] = (
    os.path.dirname(FFMPEG_PATH)
    + os.pathsep
    + os.environ.get("PATH", "")
) if os.path.dirname(FFMPEG_PATH) else os.environ.get(
    "PATH",
    ""
)


# ============================================================
# Verify FFmpeg
# ============================================================

def verify_ffmpeg():

    ffmpeg_exists = os.system(
        "ffmpeg -version > /dev/null 2>&1"
    ) == 0

    ffprobe_exists = os.system(
        "ffprobe -version > /dev/null 2>&1"
    ) == 0

    if not ffmpeg_exists:

        raise FileNotFoundError(
            "FFmpeg was not found. "
            "Make sure packages.txt contains: ffmpeg"
        )

    if not ffprobe_exists:

        raise FileNotFoundError(
            "FFprobe was not found. "
            "Make sure FFmpeg is installed correctly."
        )


verify_ffmpeg()


# ============================================================
# Whisper Configuration
# ============================================================

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "tiny"
)

_model = None


# ============================================================
# Sarvam AI Configuration
# ============================================================

SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

SARVAM_STT_TRANSLATE_URL = (
    "https://api.sarvam.ai/speech-to-text-translate"
)

SARVAM_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v2.5"
)


# ============================================================
# Load Whisper Model
# ============================================================

def load_model():

    global _model

    if _model is None:

        print(
            f"Loading Whisper model: "
            f"{WHISPER_MODEL}"
        )

        _model = whisper.load_model(
            WHISPER_MODEL
        )

        print(
            "Whisper model loaded successfully"
        )

    return _model


# ============================================================
# Transcribe One Chunk
# ============================================================

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
):

    model = load_model()

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    if language.lower() == "english":

        result = model.transcribe(
            chunk_path,
            language="en",
            task="transcribe"
        )

    # --------------------------------------------------------
    # Hindi
    # --------------------------------------------------------

    elif language.lower() == "hindi":

        result = model.transcribe(
            chunk_path,
            language="hi",
            task="transcribe"
        )

    # --------------------------------------------------------
    # Hinglish
    # --------------------------------------------------------

    elif language.lower() == "hinglish":

        # Whisper doesn't have a separate Hinglish mode.
        # Auto-detection is better for mixed Hindi + English.

        result = model.transcribe(
            chunk_path,
            task="transcribe"
        )

    # --------------------------------------------------------
    # Unknown language
    # --------------------------------------------------------

    else:

        result = model.transcribe(
            chunk_path,
            task="transcribe"
        )

    return result["text"]


# ============================================================
# Transcribe All Chunks
# ============================================================

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = ""

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing "
            f"chunk {i + 1}/{len(chunks)}"
        )

        text = transcribe_chunk(
            chunk,
            language=language
        )

        full_transcript += (
            text.strip()
            + " "
        )

    print(
        "Transcription Completed"
    )

    return full_transcript.strip()