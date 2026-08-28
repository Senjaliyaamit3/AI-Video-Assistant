# Actionableitems, decision, questions

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import os

def get_llm():
    return ChatMistralAI(model="mistral-small-latest", mistral_api_key=os.getenv("MISTRAL_API_KEY"),temperature=0.3)

def build_chain(system_prompt : str):
    llm = get_llm()
    return (RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) | 
            ChatPromptTemplate.from_messages([
            ("system",system_prompt),
            ("human","{text}"),
        ]))

def extract_action_items(transcript : str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From The meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Note specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )
    return chain.invoke(transcript)

def extract_key_decisions(transcript : str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list."
        "If none found say 'No key decisions found.'"
    )
    return chain.invoke(transcript)

def extract_questions(transcripts: str)-> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved question "
        "or topic needing follow-up. Format as a numbered list."
        "If none found say 'No open questions found.'"
    )
    return chain.invoke(transcripts)