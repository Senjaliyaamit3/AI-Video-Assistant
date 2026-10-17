import os
import shutil

import yt_dlp
from pydub import AudioSegment

from utils.ffmpeg_setup import ensure_ffmpeg


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(PROJECT_DIR, "downloads")
COOKIE_FILE = os.path.join(PROJECT_DIR, "youtube_cookies.txt")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _setup_ffmpeg() -> str:
    ffmpeg, ffprobe = ensure_ffmpeg()

    AudioSegment.converter = ffmpeg
    AudioSegment.ffmpeg = ffmpeg
    AudioSegment.ffprobe = ffprobe

    return ffmpeg


def download_youtube_audio(url: str) -> str:
import glob
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


# ============================================================
# CHECK YOUTUBE URL
# ============================================================

def is_youtube_url(source: str) -> bool:
    """
    Returns True if the provided source is a YouTube URL.
    """

    source = source.strip().lower()

    youtube_domains = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    ]

    return any(domain in source for domain in youtube_domains)


# ============================================================
# PROCESS INPUT
# ============================================================

def process_input(source: str) -> list:
    """
    Process a YouTube URL or local audio/video file.

    Parameters
    ----------
    source : str
        YouTube URL or local file path.

    Returns
    -------
    list
        A list containing the final audio file path.
    """

    ffmpeg = _setup_ffmpeg()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "ffmpeg_location": os.path.dirname(ffmpeg),
    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not source or not source.strip():
        raise ValueError("Please provide a YouTube URL or file path.")

    source = source.strip()

    # --------------------------------------------------------
    # Local file
    # --------------------------------------------------------

    if not is_youtube_url(source):

        if not os.path.exists(source):
            raise FileNotFoundError(
                f"Local file not found: {source}"
            )

        return [source]

    # --------------------------------------------------------
    # Create temporary directory
    # --------------------------------------------------------

    output_dir = Path("temp_audio")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # yt-dlp configuration
    # --------------------------------------------------------

    ydl_opts = {

        # Download best available audio
        "format": "bestaudio/best",

        # Output file template
        "outtmpl": str(
            output_dir / "%(id)s.%(ext)s"
        ),

        # Download only one video
        "noplaylist": True,

        # Retry configuration
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 5,

        # Network timeout
        "socket_timeout": 30,

        # Force IPv4
        "source_address": "0.0.0.0",

        # Do not overwrite existing files
        "overwrites": False,

        # Convert downloaded audio to MP3
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": ["-ar", "16000", "-ac", "1"],
        "extractor_args": {
            "youtube": {"player_client": ["default", "web_embedded"]}
        },
        "quiet": False,
        "no_warnings": False,
        "retries": 3,
        "fragment_retries": 3,
        "ignoreerrors": False,
        "socket_timeout": 30,
    }

    if os.path.isfile(COOKIE_FILE):
        ydl_opts["cookiefile"] = COOKIE_FILE
        print(f"Using cookies: {COOKIE_FILE}")
    else:
        print("No youtube_cookies.txt found - continuing without cookies.")

    runtimes = {name: {} for name in ("deno", "node") if shutil.which(name)}
    if runtimes:
        ydl_opts["js_runtimes"] = runtimes

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                raise RuntimeError("Could not extract YouTube video information.")

            if "entries" in info and info["entries"]:
                info = info["entries"][0]

            wav_path = os.path.join(DOWNLOAD_DIR, f"{info['id']}.wav")

            if not os.path.exists(wav_path):
                raise FileNotFoundError(f"WAV file was not created: {wav_path}")

            print(f"\nWAV file: {wav_path}")
            return wav_path

    except Exception as e:
        raise RuntimeError(f"YouTube download failed: {e}") from e


def convert_to_wav(input_path: str) -> str:

    _setup_ffmpeg()

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")
    except Exception as error:
        raise RuntimeError(f"Audio conversion failed: {error}") from error

    print(f"Conversion successful: {output_path}")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    _setup_ffmpeg()

    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    if chunk_minutes <= 0:
        raise ValueError("chunk_minutes must be greater than 0.")

    try:
        audio = AudioSegment.from_file(wav_path)
    except Exception as error:
        raise RuntimeError(f"Could not open audio file: {error}") from error

    if len(audio) == 0:
        raise ValueError("The audio file is empty.")

    chunk_ms = chunk_minutes * 60 * 1000
    base_path = os.path.splitext(wav_path)[0]
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{base_path}_chunk_{i + 1}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
        print(f"Created chunk {i + 1}: {chunk_path}")

    print(f"Total chunks created: {len(chunks)}")
    return chunks


def process_input(source: str, chunk_minutes: int = 10) -> list:

    source = source.strip().strip('"')

    if source.startswith(("http://", "https://")):
        print("Detected URL.")
        wav_path = download_youtube_audio(source)

    else:
        print("Using local file.")

        if not os.path.isfile(source):
            raise FileNotFoundError(f"File not found: {source}")

        wav_path = source

        if not wav_path.lower().endswith(".wav"):
            wav_path = convert_to_wav(wav_path)

    chunks = chunk_audio(wav_path, chunk_minutes=chunk_minutes)

    print(f"Audio processing completed. Total chunks: {len(chunks)}")
    return chunks

        # Debugging
        "quiet": False,
        "no_warnings": False,
    }

    # --------------------------------------------------------
    # Download YouTube audio
    # --------------------------------------------------------

    try:

        with YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                source,
                download=True
            )

            if info is None:
                raise RuntimeError(
                    "Unable to retrieve YouTube video information."
                )

            # ------------------------------------------------
            # Handle playlist response safely
            # ------------------------------------------------

            if "entries" in info:

                entries = info.get("entries")

                if not entries:
                    raise RuntimeError(
                        "No videos found in YouTube response."
                    )

                info = entries[0]

            # ------------------------------------------------
            # Get video ID
            # ------------------------------------------------

            video_id = info.get("id")

            if not video_id:
                raise RuntimeError(
                    "Could not determine YouTube video ID."
                )

            # ------------------------------------------------
            # Expected MP3 path
            # ------------------------------------------------

            audio_path = output_dir / f"{video_id}.mp3"

            # Wait/check final file
            if audio_path.exists():
                return [str(audio_path)]

            # ------------------------------------------------
            # Fallback: search for MP3 file
            # ------------------------------------------------

            mp3_files = glob.glob(
                str(output_dir / f"{video_id}*.mp3")
            )

            if mp3_files:
                return [mp3_files[0]]

            # ------------------------------------------------
            # Search for any audio file as fallback
            # ------------------------------------------------

            possible_files = []

            extensions = [
                "*.mp3",
                "*.m4a",
                "*.webm",
                "*.wav",
                "*.aac",
                "*.opus",
            ]

            for extension in extensions:

                files = glob.glob(
                    str(output_dir / f"{video_id}*{extension}")
                )

                possible_files.extend(files)

            if possible_files:
                return [possible_files[0]]

            raise FileNotFoundError(
                "Audio file was not created after download."
            )

    # --------------------------------------------------------
    # yt-dlp specific error
    # --------------------------------------------------------

    except DownloadError as e:

        error_message = str(e)

        if "HTTP Error 403" in error_message or "Forbidden" in error_message:

            raise RuntimeError(
                "YouTube blocked the download request (HTTP 403 Forbidden).\n\n"
                "This can happen when YouTube blocks requests from the "
                "cloud server. Please try another video or update yt-dlp."
            )

        raise RuntimeError(
            f"YouTube download failed:\n{error_message}"
        )

    # --------------------------------------------------------
    # General error
    # --------------------------------------------------------

    except Exception as e:

        raise RuntimeError(
            f"Failed to download/process YouTube audio.\n\n"
            f"Original error: {str(e)}"
        )
