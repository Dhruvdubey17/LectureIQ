from lectureiq.rag import _timestamp, _youtube_link


def test_timestamp_formats_minutes_and_hours():
    assert _timestamp(157) == "2:37"
    assert _timestamp(9) == "0:09"
    assert _timestamp(3661) == "1:01:01"


def test_youtube_link_appends_time_param():
    # youtu.be short links have no query yet, watch?v= links already do.
    assert _youtube_link("https://youtu.be/abc", 90) == "https://youtu.be/abc?t=90"
    assert (
        _youtube_link("https://www.youtube.com/watch?v=abc", 90)
        == "https://www.youtube.com/watch?v=abc&t=90"
    )
