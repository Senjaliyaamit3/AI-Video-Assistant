import os


# ============================================================
# FFmpeg configuration
# ============================================================

FFMPEG_DIR = (
    r"C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0-full_build\bin"
)

FFMPEG_PATH = os.path.join(
    FFMPEG_DIR,
    "ffmpeg.exe"
)

FFPROBE_PATH = os.path.join(
    FFMPEG_DIR,
    "ffprobe.exe"
)


# Add FFmpeg to PATH for this Python process
os.environ["PATH"] = (
    FFMPEG_DIR
    + os.pathsep
    + os.environ.get("PATH", "")
)


# Verify
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(
        f"FFmpeg not found: {FFMPEG_PATH}"
    )

if not os.path.exists(FFPROBE_PATH):
    raise FileNotFoundError(
        f"FFprobe not found: {FFPROBE_PATH}"
    )


# Import Whisper AFTER modifying PATH
import whisper


# ============================================================
# Whisper configuration
# ============================================================

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "tiny"
)

_model = None

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL","saaras:v2.5")

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


def transcribe_chunk(
    chunk_path: str,
    translate: bool = False
):

    model = load_model()

    task = (
        "translate"
        if translate
        else "transcribe"
    )

    result = model.transcribe(
        chunk_path,
        task=task
    )

    return result["text"]


def transcribe_all(
    chunks: list,
    translate: bool = False
) -> str:

    full_transcript = ""

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing "
            f"chunk {i + 1}/{len(chunks)}"
        )

        text = transcribe_chunk(
            chunk,
            translate=translate
        )

        full_transcript += (
            text.strip()
            + " "
        )

    print(
        "Transcription Completed"
    )

    return full_transcript.strip()