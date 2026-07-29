from dataclasses import dataclass


@dataclass
class Segment:
    """A span of transcript text with its start and end time in seconds.

    Reused for both raw caption lines and the merged chunks we index.
    """

    start: float
    end: float
    text: str


@dataclass
class Lecture:
    video_id: str
    title: str
    url: str
