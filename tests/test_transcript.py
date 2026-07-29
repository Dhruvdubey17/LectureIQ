from lectureiq.transcript import _events_to_segments


def test_parse_joins_segs_and_computes_times():
    events = [
        {"tStartMs": 1000, "dDurationMs": 2000, "segs": [{"utf8": "hello "}, {"utf8": "world"}]},
    ]
    segs = _events_to_segments(events)
    assert len(segs) == 1
    assert segs[0].text == "hello world"
    assert segs[0].start == 1.0 and segs[0].end == 3.0


def test_parse_skips_empty_and_dedupes_scrolling_repeats():
    events = [
        {"segs": [{"utf8": "\n"}]},  # whitespace only -> skipped
        {"tStartMs": 0, "dDurationMs": 1000, "segs": [{"utf8": "a line"}]},
        {"tStartMs": 1000, "dDurationMs": 1000, "segs": [{"utf8": "a line"}]},  # repeat -> skipped
        {"tStartMs": 2000, "dDurationMs": 1000, "segs": [{"utf8": "next line"}]},
        {"foo": "bar"},  # no segs -> skipped
    ]
    segs = _events_to_segments(events)
    assert [s.text for s in segs] == ["a line", "next line"]
