"""Orchestrate one lecture: URL -> transcript -> chunks -> indexed in Chroma."""
from . import config, store
from .chunk import chunk_segments
from .transcript import get_transcript


def ingest(url, source="captions"):
    lecture, segments = get_transcript(url, source=source)
    chunks = chunk_segments(segments, max_words=config.CHUNK_WORDS)
    n = store.index_chunks(lecture, chunks)
    return {
        "video_id": lecture.video_id,
        "title": lecture.title,
        "segments": len(segments),
        "chunks": n,
    }
