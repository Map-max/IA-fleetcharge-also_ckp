"""Duas chains exigidas: conversa com memoria e LCEL estruturada."""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_classic.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import ChatOllama
from .memory_manager import build_memory, token_ids
from .prompts import SYSTEM_PROMPT, ANALYSIS_SYSTEM, ANALYSIS_HUMAN
from .schemas import AnaliseConsulta

MODEL = 'gemma4:cloud'
ROOT = Path(__file__).resolve().parents[1]


def build_llm():
    load_dotenv(ROOT / '.env', override=False)
    key = os.getenv('OLLAMA_API_KEY', '').strip()
    if not key or key == 'preencha_sua_chave':
        raise ValueError('Configure OLLAMA_API_KEY no arquivo .env local. Nao envie a chave no chat.')
    # Modelo literal exigido pelo professor. Sem fallback silencioso.
    return ChatOllama(model=MODEL, base_url='https://ollama.com', temperature=0,
                      num_predict=700, custom_get_token_ids=token_ids,
                      client_kwargs={'headers': {'Authorization': 'Bearer ' + key},
                                     'timeout': 120.0})


def build_chat(llm=None, limit=1200):
    llm = llm if llm is not None else build_llm()
    prompt = ChatPromptTemplate.from_messages([
        ('system', SYSTEM_PROMPT), MessagesPlaceholder('history'), ('human', '{input}')])
    return ConversationChain(llm=llm, memory=build_memory(llm, limit),
                              prompt=prompt, input_key='input', output_key='response',
                              verbose=False)


def build_structured(llm=None):
    llm = llm if llm is not None else build_llm()
    parser = PydanticOutputParser(pydantic_object=AnaliseConsulta)
    prompt = ChatPromptTemplate.from_messages([
        ('system', ANALYSIS_SYSTEM), ('human', ANALYSIS_HUMAN)]).partial(
            format_instructions=parser.get_format_instructions())
    return prompt | llm | parser
