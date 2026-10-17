import uuid
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings

from core.llm import get_llm, split_text

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You answer questions about a video/meeting transcript using the context below.\n"
            "- Base your answer on the context. You may make reasonable inferences from what "
            "the speaker says (for example, if the speaker says they are in front of elephants, "
            "you can infer they are at a zoo), but do not invent facts that are not supported "
            "by the context.\n"
            "- If the answer is truly not in the context, say: "
            "\"I couldn't find that information in the transcript.\"\n"
            "- Keep answers short and clear.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)


@lru_cache(maxsize=1)
def _get_embeddings() -> HuggingFaceEmbeddings:
    """Load the embedding model once per process."""
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def _format_docs(docs) -> str:
    return "\n\n".join(d.page_content for d in docs)


def build_rag_chain(transcript: str):
    """Embed the transcript into an in-memory Chroma store and return an LCEL chain."""
    chunks = split_text(transcript, chunk_size=1000, overlap=150)
    if not chunks:
        raise ValueError("Transcript is empty, nothing to index.")

    # Unique collection name so a previous video's chunks never leak into this one
    store = Chroma.from_texts(
        chunks,
        embedding=_get_embeddings(),
        collection_name=f"meeting_{uuid.uuid4().hex}",
    )
    retriever = store.as_retriever(search_kwargs={"k": 4})

    return (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | _PROMPT
        | get_llm()
        | StrOutputParser()
    )


def ask_question(rag_chain, question: str) -> str:
    return rag_chain.invoke(question).strip()