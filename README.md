# LectureIQ

Lecture intelligence. A semester of lectures is hours of unstructured audio.
LectureIQ turns that into answers you can trust: every answer cites the lecture
and the exact timestamp it came from, with a link straight to that moment.

```
YouTube URL -> transcript -> timestamped chunks -> ChromaDB -> LLM -> cited answer
```

## Stack

Python, LangChain, ChromaDB, FastAPI, Next.js, Whisper. Runs fully local and
free by default (Ollama + Chroma's built-in embeddings); swap in Groq or OpenAI
with one environment variable.

## Setup

```bash
~/.pyenv/versions/3.12.7/bin/python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Have [Ollama](https://ollama.com) running with the default model:

```bash
ollama pull llama3.2:3b
```

## Use

```bash
# Index a lecture from its YouTube captions (fast, no download).
lectureiq ingest "https://www.youtube.com/watch?v=aircAruvnKk"

# Ask a question. The answer cites lecture + timestamp with a deep link.
lectureiq ask "What is a neuron in this network?"
```

Transcribe raw audio instead of using captions (the real product path):

```bash
pip install -e ".[whisper]"
lectureiq ingest "<youtube-url>" --source whisper
```

Run the API:

```bash
lectureiq serve            # http://127.0.0.1:8000/docs
```

Note: YouTube may block direct audio downloads (HTTP 403) from some networks
without browser cookies. The captions source does not hit this. If the whisper
source 403s, pass cookies through yt-dlp (`--cookies-from-browser`) or point it
at local audio. Transcription itself always runs locally with faster-whisper.

## Config

Copy `.env.example` to `.env`. Everything is overridable by env var; the
important one is `LECTUREIQ_LLM` (`ollama` | `groq` | `openai`).
