import os
import glob
from pathlib import Path
from yt_dlp import YoutubeDL


def is_youtube_url(source: str) -> bool:
    """
    Check whether the input is a YouTube URL.
    """
    source = source.lower()

    return (
        "youtube.com" in source
        or "youtu.be" in source
        or "www.youtube.com" in source
        or "m.youtube.com" in source
    )


def process_input(source: str) -> list:
    """
    Process YouTube URL or local file.

    For YouTube:
        - Downloads best available audio
        - Converts audio to MP3 using FFmpeg
        - Returns MP3 file path

    For local files:
        - Returns the original file path
    """

    # -----------------------------
    # Create temporary audio folder
    # -----------------------------
    output_dir = Path("temp_audio")
    output_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # YouTube URL
    # -----------------------------
    if is_youtube_url(source):

        ydl_opts = {

            # Download best available audio
            "format": "bestaudio/best",

            # Output filename
            "outtmpl": str(
                output_dir / "%(id)s.%(ext)s"
            ),

            # Do not download playlists
            "noplaylist": True,

            # Better error visibility while debugging
            "quiet": False,
            "no_warnings": False,

            # Network settings
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": 30,

            # Extract audio as MP3
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        try:

            with YoutubeDL(ydl_opts) as ydl:

                # Extract and download video information
                info = ydl.extract_info(
                    source,
                    download=True
                )

                # Safety check
                if info is None:
                    raise RuntimeError(
                        "Could not retrieve video information."
                    )

                # Final MP3 path
                video_id = info.get("id")

                if not video_id:
                    raise RuntimeError(
                        "Could not find YouTube video ID."
                    )

                audio_path = output_dir / f"{video_id}.mp3"

                # Check expected path
                if audio_path.exists():
                    return [str(audio_path)]

                # Fallback: search for generated MP3
                mp3_files = glob.glob(
                    str(output_dir / f"{video_id}*.mp3")
                )

                if mp3_files:
                    return [mp3_files[0]]

                raise FileNotFoundError(
                    f"Audio file was not created: {audio_path}"
                )

        except Exception as e:

            raise RuntimeError(
                f"Failed to download/process YouTube audio.\n\n"
                f"Original error: {str(e)}\n\n"
                f"Try updating yt-dlp using:\n"
                f"python -m pip install -U yt-dlp"
            )

    # -----------------------------
    # Local file
    # -----------------------------
    else:

        if not os.path.exists(source):
            raise FileNotFoundError(
                f"Local file not found: {source}"
            )

        return [source]
