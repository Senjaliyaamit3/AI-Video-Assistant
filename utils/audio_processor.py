import os
import yt_dlp
from pydub import AudioSegment


# ============================================================
# Project Configuration
# ============================================================

# audio_processor.py is located at:
# D:\Video Agent\utils\audio_processor.py
#
# Therefore, project root is:
# D:\Video Agent\

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# Download Directory
# ============================================================

DOWNLOAD_DIR = os.path.join(
    PROJECT_DIR,
    "downloads"
)

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


# ============================================================
# YouTube Cookies
# ============================================================

# IMPORTANT:
# We use exported cookies instead of reading Chrome directly.
#
# File:
# D:\Video Agent\youtube_cookies.txt

COOKIE_FILE = os.path.join(
    PROJECT_DIR,
    "youtube_cookies.txt"
)


# ============================================================
# FFmpeg Configuration
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


# ============================================================
# Verify FFmpeg
# ============================================================

if not os.path.isfile(FFMPEG_PATH):

    raise FileNotFoundError(
        f"\nFFmpeg not found:\n"
        f"{FFMPEG_PATH}\n"
    )


if not os.path.isfile(FFPROBE_PATH):

    raise FileNotFoundError(
        f"\nFFprobe not found:\n"
        f"{FFPROBE_PATH}\n"
    )


# ============================================================
# Add FFmpeg to PATH
# ============================================================

os.environ["PATH"] = (
    FFMPEG_DIR
    + os.pathsep
    + os.environ.get("PATH", "")
)


# ============================================================
# Configure Pydub
# ============================================================

AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffmpeg = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH


# ============================================================
# Verify YouTube Cookie File
# ============================================================

def verify_cookie_file():

    if not os.path.isfile(COOKIE_FILE):

        raise FileNotFoundError(
            "\nYouTube cookie file not found.\n\n"
            "Expected location:\n"
            f"{COOKIE_FILE}\n\n"
            "Please export YouTube cookies and save them "
            "as youtube_cookies.txt inside the project folder."
        )

    print(
        f"\nYouTube cookies found:\n"
        f"{COOKIE_FILE}"
    )


# ============================================================
# YouTube → WAV
# ============================================================

def download_youtube_audio(url: str) -> str:

    print("\n" + "=" * 60)
    print("Downloading YouTube audio...")
    print("=" * 60)

    # --------------------------------------------------------
    # Verify cookie file
    # --------------------------------------------------------

    verify_cookie_file()

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    # --------------------------------------------------------
    # yt-dlp Configuration
    # --------------------------------------------------------

    ydl_opts = {

        # ====================================================
        # Best available audio
        # ====================================================

        "format": "bestaudio/best",

        # ====================================================
        # IMPORTANT:
        # Use exported cookies.
        #
        # DO NOT use:
        # "cookiesfrombrowser": ("chrome",)
        #
        # This fixes:
        # "Could not copy Chrome cookie database"
        # ====================================================

        "cookiefile": COOKIE_FILE,

        # ====================================================
        # JavaScript runtime
        # ====================================================

        "js_runtimes": {
            "deno": {}
        },

        "extractor_args": {
            "youtube": {
                "player_client": ["default", "web_embedded"]
            }
        },

        # ====================================================
        # Output
        # ====================================================

        "outtmpl": output_path,

        # ====================================================
        # FFmpeg
        # ====================================================

        "ffmpeg_location": FFMPEG_DIR,

        # ====================================================
        # Download only one video
        # ====================================================

        "noplaylist": True,

        # ====================================================
        # Audio → WAV
        # ====================================================

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],

        # ====================================================
        # Download settings
        # ====================================================

        "quiet": False,

        "no_warnings": False,

        "retries": 3,

        "fragment_retries": 3,

        "ignoreerrors": False,
    }

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:

        print("\nStarting yt-dlp...")
        print(
            f"Cookie file: {COOKIE_FILE}"
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:

                raise RuntimeError(
                    "Could not extract YouTube video information."
                )

            # ------------------------------------------------
            # Get downloaded filename
            # ------------------------------------------------

            filename = ydl.prepare_filename(
                info
            )

            # ------------------------------------------------
            # Convert original extension to WAV
            # ------------------------------------------------

            wav_path = (
                os.path.splitext(filename)[0]
                + ".wav"
            )

            # ------------------------------------------------
            # Verify WAV exists
            # ------------------------------------------------

            if not os.path.exists(wav_path):

                raise FileNotFoundError(
                    "\nWAV file was not created.\n"
                    f"Expected:\n{wav_path}"
                )

            print("\n" + "=" * 60)
            print("YouTube download successful!")
            print("=" * 60)

            print(
                f"\nWAV file:\n"
                f"{wav_path}"
            )

            return wav_path

    except Exception as e:

        print("\n" + "=" * 60)
        print("YouTube download failed!")
        print("=" * 60)

        raise RuntimeError(
            "\nYouTube download failed.\n\n"
            "yt-dlp could not access this video.\n\n"
            f"Original error:\n{e}"
        ) from e


# ============================================================
# Convert Audio → WAV
# ============================================================

def convert_to_wav(
    input_path: str
) -> str:

    print(
        f"\nConverting audio to WAV:\n"
        f"{input_path}"
    )

    # --------------------------------------------------------
    # Verify input file
    # --------------------------------------------------------

    if not os.path.isfile(input_path):

        raise FileNotFoundError(
            f"\nAudio file not found:\n"
            f"{input_path}"
        )

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    output_path = (
        os.path.splitext(
            input_path
        )[0]
        + "_converted.wav"
    )

    try:

        # ----------------------------------------------------
        # Load audio
        # ----------------------------------------------------

        audio = AudioSegment.from_file(
            input_path
        )

        # ----------------------------------------------------
        # Export WAV
        # ----------------------------------------------------

        audio.export(
            output_path,
            format="wav"
        )

    except Exception as error:

        raise RuntimeError(
            f"\nAudio conversion failed:\n"
            f"{error}"
        ) from error

    print(
        f"\nConversion successful:\n"
        f"{output_path}"
    )

    return output_path


# ============================================================
# Split Audio Into Chunks
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    print(
        "\n" + "=" * 60
    )

    print(
        f"Chunking audio into "
        f"{chunk_minutes}-minute pieces..."
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Verify WAV
    # --------------------------------------------------------

    if not os.path.isfile(wav_path):

        raise FileNotFoundError(
            f"\nWAV file not found:\n"
            f"{wav_path}"
        )

    # --------------------------------------------------------
    # Validate chunk duration
    # --------------------------------------------------------

    if chunk_minutes <= 0:

        raise ValueError(
            "chunk_minutes must be greater than 0."
        )

    # --------------------------------------------------------
    # Load WAV
    # --------------------------------------------------------

    try:

        audio = AudioSegment.from_wav(
            wav_path
        )

    except Exception as error:

        raise RuntimeError(
            f"\nCould not open WAV file:\n"
            f"{error}"
        ) from error

    # --------------------------------------------------------
    # Chunk duration in milliseconds
    # --------------------------------------------------------

    chunk_ms = (
        chunk_minutes
        * 60
        * 1000
    )

    chunks = []

    # --------------------------------------------------------
    # Base path
    # --------------------------------------------------------

    base_path = os.path.splitext(
        wav_path
    )[0]

    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    for i, start in enumerate(
        range(
            0,
            len(audio),
            chunk_ms
        )
    ):

        end = start + chunk_ms

        chunk = audio[
            start:end
        ]

        chunk_path = (
            f"{base_path}"
            f"_chunk_{i + 1}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(
            chunk_path
        )

        print(
            f"Created chunk "
            f"{i + 1}: "
            f"{chunk_path}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        f"\nTotal chunks created: "
        f"{len(chunks)}"
    )

    return chunks


# ============================================================
# Main Input Processor
# ============================================================

def process_input(
    source: str,
    chunk_minutes: int = 10
) -> list:

    # ========================================================
    # YouTube URL
    # ========================================================

    if source.startswith(
        (
            "http://",
            "https://"
        )
    ):

        print(
            "\nDetected YouTube URL."
        )

        wav_path = (
            download_youtube_audio(
                source
            )
        )

    # ========================================================
    # Local Audio
    # ========================================================

    else:

        print(
            "\nUsing local audio file."
        )

        wav_path = source

        # ----------------------------------------------------
        # Verify local file
        # ----------------------------------------------------

        if not os.path.isfile(
            wav_path
        ):

            raise FileNotFoundError(
                f"\nAudio file not found:\n"
                f"{wav_path}"
            )

        # ----------------------------------------------------
        # Convert non-WAV audio
        # ----------------------------------------------------

        if not wav_path.lower().endswith(
            ".wav"
        ):

            wav_path = convert_to_wav(
                wav_path
            )

    # ========================================================
    # Display audio path
    # ========================================================

    print(
        "\nAudio file:"
    )

    print(
        wav_path
    )

    # ========================================================
    # Split Audio
    # ========================================================

    chunks = chunk_audio(
        wav_path,
        chunk_minutes=chunk_minutes
    )

    # ========================================================
    # Completed
    # ========================================================

    print(
        "\nAudio processing completed."
    )

    print(
        f"Total chunks: {len(chunks)}"
    )

    return chunks