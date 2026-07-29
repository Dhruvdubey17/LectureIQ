from lectureiq.chunk import chunk_segments
from lectureiq.types import Segment


def test_chunk_merges_to_word_budget_and_keeps_span():
    # 4 segments, 50 words each. With a 120-word budget the first chunk flushes
    # after 3 segments (150 words), leaving the 4th as its own chunk.
    segs = [Segment(i * 2.0, i * 2.0 + 2, "word " * 50) for i in range(4)]
    chunks = chunk_segments(segs, max_words=120)
    assert len(chunks) == 2
    assert chunks[0].start == 0.0
    assert chunks[0].end == segs[2].end
    assert len(chunks[1].text.split()) == 50


def test_single_short_segment_makes_one_chunk():
    chunks = chunk_segments([Segment(0, 1, "hi there")], max_words=160)
    assert len(chunks) == 1
    assert chunks[0].start == 0 and chunks[0].end == 1
