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
# YouTube Cookie Configuration
# ============================================================

COOKIE_FILE = os.path.join(
    PROJECT_DIR,
    "youtube_cookies.txt"
)


def setup_cookie_file():
    """
    Setup YouTube cookies.

    Priority:

    1. Local youtube_cookies.txt
    2. Streamlit Secrets -> YOUTUBE_COOKIES

    The cookie file should NEVER be committed to GitHub.
    """

    # --------------------------------------------------------
    # 1. Local development
    # --------------------------------------------------------

    if os.path.isfile(COOKIE_FILE):

        print(
            "\nLocal YouTube cookie file found:"
        )

        print(
            COOKIE_FILE
        )

        return COOKIE_FILE


    # --------------------------------------------------------
    # 2. Streamlit Cloud
    # --------------------------------------------------------

    try:

        import streamlit as st

        cookies = st.secrets.get(
            "YOUTUBE_COOKIES",
            None
        )

        if cookies:

            with open(
                COOKIE_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    str(cookies)
                )

            print(
                "\nYouTube cookies loaded "
                "from Streamlit Secrets."
            )

            return COOKIE_FILE

    except Exception as error:

        print(
            "\nCould not load Streamlit Secrets:"
        )

        print(
            error
        )


    # --------------------------------------------------------
    # No cookies available
    # --------------------------------------------------------

    print(
        "\nNo YouTube cookie file configured."
    )

    return None


# ============================================================
# FFmpeg Configuration
# ============================================================

# FFmpeg must be available in the system PATH.
#
# Local Windows:
#     Install FFmpeg and add it to PATH.
#
# Streamlit Cloud:
#     packages.txt must contain:
#
#     ffmpeg
#
# Do NOT use a hard-coded Windows path.


FFMPEG_PATH = shutil.which(
    "ffmpeg"
)

FFPROBE_PATH = shutil.which(
    "ffprobe"
)


# ============================================================
# Verify FFmpeg
# ============================================================

if FFMPEG_PATH is None:

    raise FileNotFoundError(
        "\nFFmpeg not found.\n\n"
        "FFmpeg must be installed and available "
        "in the system PATH.\n\n"
        "For Streamlit Cloud, make sure packages.txt "
        "contains:\n\n"
        "ffmpeg\n"
    )


if FFPROBE_PATH is None:

    raise FileNotFoundError(
        "\nFFprobe not found.\n\n"
        "Make sure FFmpeg is installed correctly "
        "and ffprobe is available in PATH."
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

    cookie_file = setup_cookie_file()

    if cookie_file is None:

        print(
            "\nWARNING:"
        )

        print(
            "YouTube cookies are not configured."
        )

        print(
            "Public YouTube videos may still work."
        )

        return None


    if not os.path.isfile(
        cookie_file
    ):

        print(
            "\nWARNING:"
        )

        print(
            "YouTube cookie file could not be created."
        )

        return None


    print(
        "\nYouTube cookies ready:"
    )

    print(
        cookie_file
    )

    return cookie_file


# ============================================================
# YouTube → WAV
# ============================================================

def download_youtube_audio(
    url: str
) -> str:

    print(
        "\n" + "=" * 60
    )

    print(
        "Downloading YouTube audio..."
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    if not url:

        raise ValueError(
            "YouTube URL cannot be empty."
        )


    if not url.startswith(
        (
            "http://",
            "https://"
        )
    ):

        raise ValueError(
            "Invalid YouTube URL."
        )


    # --------------------------------------------------------
    # Setup cookies
    # --------------------------------------------------------

    cookie_file = verify_cookie_file()


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
        # Output
        # ====================================================

        "outtmpl": output_path,


        # ====================================================
        # Download only one video
        # ====================================================

        "noplaylist": True,


        # ====================================================
        # Anti-Bot & Client Configuration (Fixes 403 Forbidden)
        # ====================================================

        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },

        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },


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
    # Add cookies only if available
    # --------------------------------------------------------

    if cookie_file:

        ydl_opts[
            "cookiefile"
        ] = cookie_file


    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:

        print(
            "\nStarting yt-dlp..."
        )


        if cookie_file:

            print(
                f"\nCookie file:\n{cookie_file}"
            )

        else:

            print(
                "\nNo cookie file being used."
            )


        print(
            f"\nFFmpeg:\n{FFMPEG_PATH}"
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
            # WAV path
            # ------------------------------------------------

            wav_path = (
                os.path.splitext(
                    filename
                )[0]
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


    except Exception as error:

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
            f"Original error:\n{error}"
        ) from error


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
    # Verify input
    # --------------------------------------------------------

    if not os.path.isfile(
        input_path
    ):

        raise FileNotFoundError(
            f"\nAudio file not found:\n"
            f"{input_path}"
        )


    # --------------------------------------------------------
    # Output
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
    # Validate duration
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
    # Chunk duration
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
    # Validate source
    # ========================================================

    if not source:

        raise ValueError(
            "Input source cannot be empty."
        )


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
        # Convert non-WAV
        # ----------------------------------------------------

        if not wav_path.lower().endswith(
            ".wav"
        ):

            wav_path = convert_to_wav(
                wav_path
            )


    # ========================================================
    # Display audio
    # ========================================================

    print(
        "\nAudio file:"
    )

    print(
        wav_path
    )


    # ========================================================
    # Split audio
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
