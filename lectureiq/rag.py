"""Retrieval-augmented answering.

Retrieve the most relevant lecture chunks, then ask the LLM to answer strictly
from them and cite each claim. Every citation carries the lecture title and a
deep link to the exact timestamp, so any answer can be checked against the
source. That grounding is the whole point: no source, no claim.
"""
from langchain_core.messages import HumanMessage, SystemMessage

from . import store
from .llm import get_llm

SYSTEM = (
    "You are LectureIQ, a study assistant that answers strictly from lecture "
    "transcript excerpts. Use only the numbered excerpts provided. Cite the "
    "excerpts you rely on inline as [1], [2], and so on. If the excerpts do not "
    "contain the answer, say you do not know. Never use outside knowledge."
)


def _timestamp(seconds):
    seconds = int(seconds)
    h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _youtube_link(url, seconds):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}t={int(seconds)}"


def ask(question, k=5):
    hits = store.search(question, k)
    if not hits:
        return {"answer": "No lectures are indexed yet. Ingest one first.", "citations": []}

    blocks, citations = [], []
    for i, hit in enumerate(hits, 1):
        m = hit["meta"]
        ts = _timestamp(m["start"])
        blocks.append(f"[{i}] ({m['title']} @ {ts})\n{hit['text']}")
        citations.append(
            {
                "index": i,
                "title": m["title"],
                "timestamp": ts,
                "start": m["start"],
                "url": m["url"],
                "link": _youtube_link(m["url"], m["start"]),
            }
        )

    prompt = "Excerpts:\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}"
    try:
        resp = get_llm().invoke([SystemMessage(content=SYSTEM), HumanMessage(content=prompt)])
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc
    return {"answer": resp.content.strip(), "citations": citations}
