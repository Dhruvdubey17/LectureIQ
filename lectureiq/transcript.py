"""Turn a YouTube URL into timestamped transcript segments.

Two sources, one output shape (a Lecture plus a list of Segments):

- captions: pull YouTube's own timestamped captions. Fast, no model, no audio
  download. This is the loop we use for testing.
- whisper: download the audio and transcribe it locally with faster-whisper.
  This is the real product path for arbitrary lecture audio.

Everything downstream (chunk, embed, retrieve, answer) is identical either way.
"""
import json
import urllib.request

from .types import Lecture, Segment


def get_transcript(url, source="captions"):
    if source == "captions":
        return _from_captions(url)
    if source == "whisper":
        return _from_whisper(url)
    raise ValueError(f"unknown transcript source: {source!r}")


def _extract_info(url):
    import yt_dlp

    opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:  # yt-dlp raises many private error types
        raise RuntimeError(f"could not read video info for {url}: {exc}") from exc
    lecture = Lecture(info["id"], info.get("title", info["id"]), info.get("webpage_url", url))
    return lecture, info


def _events_to_segments(events):
    """Parse YouTube json3 caption events into timestamped segments.

    Each event carries segs (text pieces) plus tStartMs/dDurationMs. Auto-captions
    repeat the previous line as they scroll, so exact repeats are dropped.
    """
    segments = []
    for ev in events:
        if "segs" not in ev:
            continue
        text = "".join(s.get("utf8", "") for s in ev["segs"]).strip()
        if not text:
            continue
        if segments and segments[-1].text == text:  # ponytail: prev-line dedup
            continue
        start = ev.get("tStartMs", 0) / 1000.0
        end = start + ev.get("dDurationMs", 0) / 1000.0
        segments.append(Segment(start, end, text))
    return segments


def _from_captions(url):
    lecture, info = _extract_info(url)
    tracks = (info.get("subtitles") or {}).get("en") or (info.get("automatic_captions") or {}).get("en")
    if not tracks:
        raise RuntimeError(f"no English captions for {url}; try source='whisper'")

    track = next((t for t in tracks if t.get("ext") == "json3"), tracks[0])
    try:
        with urllib.request.urlopen(track["url"]) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"could not fetch caption track for {url}: {exc}") from exc

    segments = _events_to_segments(data.get("events", []))
    if not segments:
        raise RuntimeError(f"caption track for {url} was empty")
    return lecture, segments


def _from_whisper(url):
    from faster_whisper import WhisperModel

    from . import config

    lecture, _ = _extract_info(url)
    config.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    existing = list(config.AUDIO_DIR.glob(f"{lecture.video_id}.*"))
    if existing:
        audio_path = existing[0]
    else:
        import yt_dlp

        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": str(config.AUDIO_DIR / f"{lecture.video_id}.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as exc:
            raise RuntimeError(f"could not download audio for {url}: {exc}") from exc
        written = list(config.AUDIO_DIR.glob(f"{lecture.video_id}.*"))
        if not written:
            raise RuntimeError(f"audio download produced no file for {url}")
        audio_path = written[0]

    model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(audio_path), vad_filter=True)
    segments = [Segment(s.start, s.end, s.text.strip()) for s in segs if s.text.strip()]
    if not segments:
        raise RuntimeError(f"whisper produced no text for {url}")
    return lecture, segments
