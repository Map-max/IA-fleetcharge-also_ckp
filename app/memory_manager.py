"""TokenBuffer: historico limitado sem resumir ou inventar fatos."""
from functools import lru_cache
import tiktoken
from langchain_classic.memory import ConversationTokenBufferMemory


@lru_cache(maxsize=1)
def encoding():
    # Proxy de tokens; nao e o tokenizer nativo do Gemma.
    return tiktoken.get_encoding('cl100k_base')


def token_ids(text):
    return encoding().encode(text, disallowed_special=())


def count_tokens(text):
    return len(token_ids(text))


def build_memory(llm, limit=1200):
    if not 800 <= limit <= 1500:
        raise ValueError('A memoria deve ficar entre 800 e 1500 tokens estimados.')
    return ConversationTokenBufferMemory(llm=llm, max_token_limit=limit,
                                          memory_key='history', input_key='input',
                                          output_key='response', return_messages=True)
