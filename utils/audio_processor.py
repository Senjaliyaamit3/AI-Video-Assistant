import os
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
