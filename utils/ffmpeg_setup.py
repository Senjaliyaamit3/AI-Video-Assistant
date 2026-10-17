"""
Finds FFmpeg/FFprobe and makes sure they are on PATH for this process.

Order of lookup:
  1. Already on PATH
  2. FFMPEG_DIR environment variable (.env)
  3. Common Windows install locations (winget, chocolatey, C:\\ffmpeg ...)

On Linux / Streamlit Cloud, FFmpeg comes from packages.txt and is already on PATH.
"""

import glob
import os
import shutil

_EXE = ".exe" if os.name == "nt" else ""


def _candidate_dirs() -> list:
    dirs = []

    custom = os.getenv("FFMPEG_DIR")
    if custom:
        dirs.append(custom.strip().strip('"'))

    local = os.getenv("LOCALAPPDATA")
    if local:
        pattern = os.path.join(
            local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "**", "bin"
        )
        dirs.extend(glob.glob(pattern, recursive=True))
        dirs.append(os.path.join(local, "Microsoft", "WinGet", "Links"))

    dirs.extend(
        [
            r"C:\ffmpeg\bin",
            r"D:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\ProgramData\chocolatey\bin",
        ]
    )
    return dirs


def ensure_ffmpeg():
    """Return (ffmpeg_path, ffprobe_path). Raises FileNotFoundError if missing."""

    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        for folder in _candidate_dirs():
            if os.path.isfile(os.path.join(folder, "ffmpeg" + _EXE)) and os.path.isfile(
                os.path.join(folder, "ffprobe" + _EXE)
            ):
                os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
                break

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if not ffmpeg or not ffprobe:
        raise FileNotFoundError(
            "FFmpeg/FFprobe not found. Install it with "
            "'winget install Gyan.FFmpeg', then fully restart VS Code. "
            "Or set FFMPEG_DIR in your .env to the folder containing ffmpeg.exe. "
            "On Streamlit Cloud, put 'ffmpeg' in packages.txt."
        )

    return ffmpeg, ffprobe