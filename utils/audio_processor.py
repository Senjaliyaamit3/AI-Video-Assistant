import os
import shutil
import tempfile

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
# FFmpeg
# ============================================================

FFMPEG_PATH = shutil.which("ffmpeg")
FFPROBE_PATH = shutil.which("ffprobe")


if FFMPEG_PATH is None:
    raise FileNotFoundError(
        "FFmpeg not found. "
        "Make sure ffmpeg is present in packages.txt."
    )


if FFPROBE_PATH is None:
    raise FileNotFoundError(
        "FFprobe not found. "
        "Make sure ffmpeg is installed correctly."
    )


print(f"FFmpeg: {FFMPEG_PATH}")
print(f"FFprobe: {FFPROBE_PATH}")


# ============================================================
# Configure Pydub
# ============================================================

AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffmpeg = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH


# ============================================================
# YouTube Cookies
# ============================================================

def create_cookie_file():

    """
    Creates a temporary cookie file from Streamlit Secrets.

    Local:
        D:/Video Agent/youtube_cookies.txt

    Streamlit Cloud:
        st.secrets["YOUTUBE_COOKIES"]
    """

    # --------------------------------------------------------
    # Local cookie file
    # --------------------------------------------------------

    local_cookie_file = os.path.join(
        PROJECT_DIR,
        "youtube_cookies.txt"
    )

    if os.path.isfile(local_cookie_file):

        print(
            f"Using local cookies:\n"
            f"{local_cookie_file}"
        )

        return local_cookie_file


    # --------------------------------------------------------
    # Streamlit Cloud secrets
    # --------------------------------------------------------

    try:

        import streamlit as st

        cookies = st.secrets.get(
            "YOUTUBE_COOKIES",
            None
        )

    except Exception:

        cookies = None


    if cookies:

        temp_cookie = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8"
        )

        temp_cookie.write(
            cookies
        )

        temp_cookie.close()

        print(
            "Using YouTube cookies from "
            "Streamlit Secrets."
        )

        return temp_cookie.name


    # --------------------------------------------------------
    # No cookies
    # --------------------------------------------------------

    print(
        "No YouTube cookies found."
    )

    return None


# ============================================================
# YouTube → WAV
# ============================================================

def download_youtube_audio(
    url: str
) -> str:

    print("\n" + "=" * 60)
    print("Downloading YouTube audio...")
    print("=" * 60)

    cookie_file = create_cookie_file()


    # ========================================================
    # Output
    # ========================================================

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )


    # ========================================================
    # yt-dlp Options
    # ========================================================

    ydl_opts = {

        # ----------------------------------------------------
        # Best audio
        # ----------------------------------------------------

        "format": "bestaudio/best",


        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        "outtmpl": output_path,


        # ----------------------------------------------------
        # YouTube
        #
        # web_embedded currently avoids some PO-token
        # requirements.
        # ----------------------------------------------------

        "extractor_args": {
            "youtube": {
                "player_client": [
                    "web_embedded"
                ]
            }
        },


        # ----------------------------------------------------
        # EJS
        #
        # yt-dlp uses external JS challenge solving for
        # modern YouTube extraction.
        # ----------------------------------------------------

        "remote_components": {
            "ejs": [
                "github"
            ]
        },


        # ----------------------------------------------------
        # JavaScript runtime
        #
        # If Deno exists on the machine, yt-dlp can use it.
        # ----------------------------------------------------

        "js_runtimes": {
            "deno": {}
        },


        # ----------------------------------------------------
        # Cookies
        # ----------------------------------------------------

        "noplaylist": True,


        # ----------------------------------------------------
        # Audio conversion
        # ----------------------------------------------------

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav"
            }
        ],


        # ----------------------------------------------------
        # FFmpeg
        #
        # FFmpeg is already in PATH.
        # ----------------------------------------------------

        "ffmpeg_location": FFMPEG_PATH,


        # ----------------------------------------------------
        # Network
        # ----------------------------------------------------

        "socket_timeout": 30,

        "retries": 3,

        "fragment_retries": 3,


        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

        "quiet": False,

        "no_warnings": False,

        "ignoreerrors": False,
    }


    # ========================================================
    # Add cookies ONLY if available
    # ========================================================

    if cookie_file:

        ydl_opts["cookiefile"] = cookie_file


    # ========================================================
    # Download
    # ========================================================

    try:

        print(
            "\nStarting yt-dlp..."
        )

        print(
            f"URL:\n{url}"
        )

        print(
            f"FFmpeg:\n{FFMPEG_PATH}"
        )

        if cookie_file:

            print(
                "YouTube cookies: ENABLED"
            )

        else:

            print(
                "YouTube cookies: DISABLED"
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
                    "yt-dlp could not extract "
                    "video information."
                )


            # ------------------------------------------------
            # Filename
            # ------------------------------------------------

            filename = ydl.prepare_filename(
                info
            )


            # ------------------------------------------------
            # WAV filename
            # ------------------------------------------------

            wav_path = (
                os.path.splitext(
                    filename
                )[0]
                + ".wav"
            )


            # ------------------------------------------------
            # Verify
            # ------------------------------------------------

            if not os.path.isfile(
                wav_path
            ):

                raise FileNotFoundError(
                    "WAV file was not created.\n"
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
                f"WAV:\n{wav_path}"
            )


            return wav_path


    except Exception as e:

        print(
            "\nYouTube download failed:"
        )

        print(
            repr(e)
        )

        raise RuntimeError(
            "YouTube download failed.\n\n"
            f"Original error:\n{e}"
        ) from e


# ============================================================
# Convert Audio → WAV
# ============================================================

def convert_to_wav(
    input_path: str
) -> str:

    if not os.path.isfile(
        input_path
    ):

        raise FileNotFoundError(
            f"Audio file not found:\n"
            f"{input_path}"
        )


    output_path = (
        os.path.splitext(
            input_path
        )[0]
        + "_converted.wav"
    )


    try:

        audio = AudioSegment.from_file(
            input_path
        )

        audio.export(
            output_path,
            format="wav"
        )


    except Exception as error:

        raise RuntimeError(
            f"Audio conversion failed:\n"
            f"{error}"
        ) from error


    return output_path


# ============================================================
# Split Audio
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    if not os.path.isfile(
        wav_path
    ):

        raise FileNotFoundError(
            f"WAV file not found:\n"
            f"{wav_path}"
        )


    if chunk_minutes <= 0:

        raise ValueError(
            "chunk_minutes must be greater than 0."
        )


    try:

        audio = AudioSegment.from_wav(
            wav_path
        )

    except Exception as error:

        raise RuntimeError(
            f"Could not open WAV file:\n"
            f"{error}"
        ) from error


    chunk_ms = (
        chunk_minutes
        * 60
        * 1000
    )


    chunks = []


    base_path = os.path.splitext(
        wav_path
    )[0]


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
            f"Created chunk {i + 1}: "
            f"{chunk_path}"
        )


    print(
        f"Total chunks: {len(chunks)}"
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
    # YouTube
    # ========================================================

    if source.startswith(
        (
            "http://",
            "https://"
        )
    ):

        print(
            "Detected YouTube URL."
        )


        wav_path = download_youtube_audio(
            source
        )


    # ========================================================
    # Local Audio
    # ========================================================

    else:

        print(
            "Using local audio file."
        )


        wav_path = source


        if not os.path.isfile(
            wav_path
        ):

            raise FileNotFoundError(
                f"Audio file not found:\n"
                f"{wav_path}"
            )


        if not wav_path.lower().endswith(
            ".wav"
        ):

            wav_path = convert_to_wav(
                wav_path
            )


    # ========================================================
    # Chunk
    # ========================================================

    chunks = chunk_audio(
        wav_path,
        chunk_minutes
    )


    print(
        "Audio processing completed."
    )


    return chunks
