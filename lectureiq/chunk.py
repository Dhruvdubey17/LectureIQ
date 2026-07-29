"""Merge transcript segments into larger, timestamp-anchored chunks.

Embeddings need a paragraph of context, not a single caption line, so we pack
consecutive segments up to a word budget and keep the span's start and end time.
The kept start time is what the citation links back to.
"""
from .types import Segment


def chunk_segments(segments, max_words=160):
    chunks = []
    buf, words, start = [], 0, None
    for seg in segments:
        if start is None:
            start = seg.start
        buf.append(seg.text)
        words += len(seg.text.split())
        if words >= max_words:
            chunks.append(Segment(start, seg.end, " ".join(buf)))
            buf, words, start = [], 0, None
    if buf:
        chunks.append(Segment(start, segments[-1].end, " ".join(buf)))
    return chunks
