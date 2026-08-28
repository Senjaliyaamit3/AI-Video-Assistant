import os
from yt_dlp import YoutubeDL

def process_input(source: str) -> list:
    """
    Downloads audio from a YouTube URL with resilient configuration 
    to bypass restrictions and format errors.
    """
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    if "youtube.com" in source or "youtu.be" in source:
        ydl_opts = {
            # Target any available audio or low-res fallback stream that won't trigger format blocks
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            },
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                audio_path = os.path.join(output_dir, f"{info['id']}.mp3")
                return [audio_path]
        except Exception as e:
            # Ultimate fallback: Force generic format extraction
            ydl_opts['format'] = 'worst'
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                audio_path = os.path.join(output_dir, f"{info['id']}.mp3")
                return [audio_path]
    else:
        return [source]
