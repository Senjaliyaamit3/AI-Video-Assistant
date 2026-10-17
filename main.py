from dotenv import load_dotenv

load_dotenv()

from utils.ffmpeg_setup import ensure_ffmpeg
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question


def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Video Assistant")
    ensure_ffmpeg()

    chunks = process_input(source)

    transcript = transcribe_all(chunks, language)
    print(f"Transcript preview: {transcript[:300]}")

    return {
        "title": generate_title(transcript),
        "transcript": transcript,
        "summary": summarize(transcript),
        "action_items": extract_action_items(transcript),
        "key_decisions": extract_key_decisions(transcript),
        "open_questions": extract_questions(transcript),
        "rag_chain": build_rag_chain(transcript),
    }


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hindi/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    print("\n" + "=" * 60)
    print(f"Title: {result['title']}")
    print(f"\nSummary:\n{result['summary']}")
    print(f"\nAction Items:\n{result['action_items']}")
    print(f"\nKey Decisions:\n{result['key_decisions']}")
    print(f"\nOpen Questions:\n{result['open_questions']}")
    print("=" * 60)

    print("\nChat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue
        print(f"\nAssistant: {ask_question(rag_chain, question)}\n")