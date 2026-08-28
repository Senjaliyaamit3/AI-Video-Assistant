import os
import shutil
import yt_dlp
from pydub import AudioSegment


# ============================================================
# Project Configuration
# ============================================================

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

COOKIE_FILE = os.path.join(
    PROJECT_DIR,
    "youtube_cookies.txt"
)


# ============================================================
# FFmpeg Configuration
# ============================================================

# FFmpeg must be available in the system PATH.
#
# Windows:
#   Your locally installed FFmpeg should be in PATH.
#
# Streamlit Cloud:
#   FFmpeg is installed using packages.txt:
#
#       ffmpeg
#
# Do NOT use a hard-coded Windows path.

FFMPEG_PATH = shutil.which("ffmpeg")
FFPROBE_PATH = shutil.which("ffprobe")


# ============================================================
# Verify FFmpeg
# ============================================================

if FFMPEG_PATH is None:

    raise FileNotFoundError(
        "\nFFmpeg not found.\n\n"
        "Make sure FFmpeg is installed and available "
        "in the system PATH.\n\n"
        "For Streamlit Cloud, create packages.txt "
        "with:\n\n"
        "ffmpeg\n"
    )


if FFPROBE_PATH is None:

    raise FileNotFoundError(
        "\nFFprobe not found.\n\n"
        "Make sure FFmpeg is installed correctly "
        "and ffprobe is available in PATH.\n"
    )


print(
    f"\nFFmpeg found:\n{FFMPEG_PATH}"
)

print(
    f"\nFFprobe found:\n{FFPROBE_PATH}"
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
    """
    Verify that the exported YouTube cookie file exists.

    IMPORTANT:
    Do NOT upload youtube_cookies.txt to GitHub.
    """

    if not os.path.isfile(COOKIE_FILE):

        raise FileNotFoundError(
            "\nYouTube cookie file not found.\n\n"
            f"Expected location:\n{COOKIE_FILE}\n\n"
            "Please export your YouTube cookies and "
            "save them as youtube_cookies.txt."
        )

    print(
        f"\nYouTube cookies found:\n"
        f"{COOKIE_FILE}"
    )


# ============================================================
# YouTube → WAV
# ============================================================

def download_youtube_audio(
    url: str
) -> str:

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
        # YouTube cookies
        # ====================================================

        "cookiefile": COOKIE_FILE,

        # ====================================================
        # JavaScript Runtime
        # ====================================================

        "js_runtimes": {
            "deno": {}
        },

        # ====================================================
        # Remote EJS components
        #
        # Required by newer yt-dlp versions for
        # YouTube JavaScript challenge solving.
        # ====================================================

        "remote_components": {
            "ejs": ["github"]
        },

        # ====================================================
        # YouTube extractor configuration
        # ====================================================

        "extractor_args": {
            "youtube": {
                "player_client": [
                    "default",
                    "web_embedded"
                ]
            }
        },

        # ====================================================
        # Output
        # ====================================================

        "outtmpl": output_path,

        # ====================================================
        # IMPORTANT:
        # Do NOT use:
        #
        # "ffmpeg_location": FFMPEG_DIR
        #
        # FFmpeg is already available through PATH.
        # ====================================================

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

        # ====================================================
        # Network timeout
        # ====================================================

        "socket_timeout": 30,
    }

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:

        print(
            "\nStarting yt-dlp..."
        )

        print(
            f"Cookie file:\n{COOKIE_FILE}"
        )

        print(
            f"FFmpeg:\n{FFMPEG_PATH}"
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:

                raise RuntimeError(
                    "Could not extract YouTube "
                    "video information."
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
            # Verify WAV
            # ------------------------------------------------

            if not os.path.exists(
                wav_path
            ):

                raise FileNotFoundError(
                    "\nWAV file was not created.\n\n"
                    f"Expected:\n{wav_path}"
                )

            print(
                "\n" + "=" * 60
            )

            print(
                "YouTube download successful!"
            )

            print(
                "=" * 60
            )

            print(
                f"\nWAV file:\n{wav_path}"
            )

            return wav_path

    except Exception as e:

        print(
            "\n" + "=" * 60
        )

        print(
            "YouTube download failed!"
        )

        print(
            "=" * 60
        )

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

    if not os.path.isfile(
        input_path
    ):

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

    if not os.path.isfile(
        wav_path
    ):

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
