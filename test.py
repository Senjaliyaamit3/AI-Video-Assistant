from utils.audio_processor import process_input
from core.transcriber import transcribe_all


source = "https://www.youtube.com/watch?v=J_d_Q3pTYcc"

chunks = process_input(source)

transcript = transcribe_all(chunks)

print("\n========== TRANSCRIPT ==========\n")
print(transcript)