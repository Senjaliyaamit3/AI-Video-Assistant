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

    print("\n" + "=" * 60)
    print("Downloading YouTube audio...")
    print("=" * 60)

    ffmpeg = _setup_ffmpeg()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "ffmpeg_location": os.path.dirname(ffmpeg),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
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