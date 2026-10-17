from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from core.llm import get_llm, split_text

_parser = StrOutputParser()

NONE_TEXT = "None found."


def _run(system: str, human: str, **vars) -> str:
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    return (prompt | get_llm() | _parser).invoke(vars).strip()


def _extract(what: str, instructions: str, transcript: str) -> str:
    """Extract `what` from each chunk, then merge and de-duplicate if there were several."""
    system = (
        f"You extract {what} from a transcript. {instructions} "
        f"Reply as a markdown bullet list using '- '. If there are none, reply exactly: {NONE_TEXT}"
    )
    chunks = split_text(transcript, chunk_size=10000, overlap=400)
    results = [_run(system, "Transcript:\n{text}", text=c) for c in chunks]
    results = [r for r in results if r and NONE_TEXT not in r]

    if not results:
        return NONE_TEXT
    if len(results) == 1:
        return results[0]

    return _run(
        f"Merge these lists of {what} into one bullet list. Remove duplicates, keep it concise.",
        "Lists:\n{text}",
        text="\n\n".join(results),
    )


def extract_action_items(transcript: str) -> str:
    return _extract(
        "action items",
        "Include who is responsible and any deadline if mentioned.",
        transcript,
    )


def extract_key_decisions(transcript: str) -> str:
    return _extract(
        "key decisions or conclusions",
        "Only include things that were actually decided or concluded.",
        transcript,
    )


def extract_questions(transcript: str) -> str:
    return _extract(
        "open questions",
        "Include questions raised but left unanswered or unresolved.",
        transcript,
    )