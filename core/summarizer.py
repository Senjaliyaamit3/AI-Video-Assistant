from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from core.llm import get_llm, split_text

_parser = StrOutputParser()


def _run(system: str, human: str, **vars) -> str:
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    return (prompt | get_llm() | _parser).invoke(vars).strip()


def generate_title(transcript: str) -> str:
    """Short, descriptive title based on the start of the transcript."""
    title = _run(
        "You write short, descriptive titles. Reply with the title only, max 10 words, no quotes.",
        "Transcript excerpt:\n{text}",
        text=transcript[:4000],
    )
    return title.strip('"\' ')


def summarize(transcript: str) -> str:
    """Map-reduce summary so long videos don't overflow the model context."""
    chunks = split_text(transcript)

    if len(chunks) == 1:
        return _run(
            "You are an expert note-taker. Write a clear, concise summary in 1-2 short paragraphs "
            "followed by 4-6 bullet points of the main ideas.",
            "Transcript:\n{text}",
            text=chunks[0],
        )

    partials = [
        _run(
            "Summarize this part of a longer transcript in 4-6 sentences. Keep concrete facts.",
            "Transcript part:\n{text}",
            text=c,
        )
        for c in chunks
    ]

    return _run(
        "You are an expert note-taker. Combine these partial summaries into one coherent summary: "
        "1-2 short paragraphs followed by 4-6 bullet points of the main ideas.",
        "Partial summaries:\n{text}",
        text="\n\n".join(partials),
    )