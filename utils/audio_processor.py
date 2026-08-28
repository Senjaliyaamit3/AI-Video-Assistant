import os
from yt_dlp import YoutubeDL

def process_input(source: str) -> list:
    """
    Downloads audio from a YouTube URL or local file path using 
    fully updated player clients and remote JavaScript challenge solvers.
    """
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    if "youtube.com" in source or "youtu.be" in source:
        ydl_opts = {
            # Use 'best' as a safety net fallback to avoid missing format errors
            'format': 'best/bestvideo+bestaudio/bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb', 'web']
                }
            },
            # Pulls external components to solve YouTube JS challenges automatically
            'remote_components': {'ejs': 'github'},
            'quiet': True,
            'no_warnings': False,  # Keep warnings visible to trace any issues in logs
            'ignoreerrors': False,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            audio_path = os.path.join(output_dir, f"{info['id']}.mp3")
            
        return [audio_path]
    else:
        # Fallback for local files
        return [source]
