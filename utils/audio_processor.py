import os
from yt_dlp import YoutubeDL

def process_input(source: str) -> list:
    """
    Downloads audio from a YouTube URL or local file path, 
    splits it into chunks, and returns the list of chunk file paths.
    """
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input is a YouTube URL
    if "youtube.com" in source or "youtu.be" in source:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            # FIX: Add extractor args to bypass "The page needs to be reloaded" error
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_safari', 'web_embedded', '-tv_downgraded']
                }
            },
            'quiet': True,
            'no_warnings': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=True)
            audio_path = os.path.join(output_dir, f"{info['id']}.mp3")
    else:
        # Handle local file paths
        audio_path = source

    # Split audio file into chunks for transcription if necessary
    # (Make sure your chunking implementation returns the list of chunk file paths)
    chunks = [audio_path] # Replace with your actual chunk splitting logic if applicable
    return chunks
