"""Provider-swappable chat model.

Default is local Ollama (free, no key). Set LECTUREIQ_LLM=groq or openai to
switch to a hosted model. SDK imports are lazy so you only need the package for
the provider you actually use.
"""
from . import config


def get_llm():
    provider = config.LLM_PROVIDER
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=config.OLLAMA_MODEL, temperature=0)
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=config.GROQ_MODEL, temperature=0)
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=config.OPENAI_MODEL, temperature=0)
    raise ValueError(f"unknown LECTUREIQ_LLM provider: {provider!r}")
