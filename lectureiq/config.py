"""Runtime settings, all overridable by environment variables.

Kept flat on purpose: this is a small project, so a config module beats a
settings framework.
"""
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("LECTUREIQ_DATA", "data"))
CHROMA_DIR = str(DATA_DIR / "chroma")
AUDIO_DIR = DATA_DIR / "audio"
COLLECTION = "lectures"

LLM_PROVIDER = os.getenv("LECTUREIQ_LLM", "ollama")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# How many words to pack into one indexed chunk, and how many chunks to retrieve.
CHUNK_WORDS = int(os.getenv("LECTUREIQ_CHUNK_WORDS", "160"))
TOP_K = int(os.getenv("LECTUREIQ_TOP_K", "5"))
