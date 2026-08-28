import os
from yt_dlp import YoutubeDL

def process_input(source: str) -> list:
    """
    Downloads audio from a YouTube URL or local file path using 
    optimized player configurations and fallback handling.
    """
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    if "youtube.com" in source or "youtu.be" in source:
        ydl_opts = {
            'format': 'ba/b',
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
            ydl_opts['extractor_args'] = {'youtube': {'player_client': ['web_embedded']}}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                audio_path = os.path.join(output_dir, f"{info['id']}.mp3")
                return [audio_path]
    else:
        return [source]
