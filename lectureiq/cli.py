import argparse
import json

from dotenv import load_dotenv


def main():
    load_dotenv()
    p = argparse.ArgumentParser(prog="lectureiq")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="index a YouTube lecture")
    pi.add_argument("url")
    pi.add_argument("--source", choices=["captions", "whisper"], default="captions")

    pa = sub.add_parser("ask", help="ask a question over indexed lectures")
    pa.add_argument("question")
    pa.add_argument("-k", type=int, default=None)

    ps = sub.add_parser("serve", help="run the FastAPI service")
    ps.add_argument("--host", default="127.0.0.1")
    ps.add_argument("--port", type=int, default=8000)

    args = p.parse_args()

    if args.cmd == "ingest":
        from .ingest import ingest

        print(json.dumps(ingest(args.url, source=args.source), indent=2))
    elif args.cmd == "ask":
        from . import config
        from .rag import ask

        out = ask(args.question, k=args.k or config.TOP_K)
        print(out["answer"])
        if out["citations"]:
            print("\nSources:")
            for c in out["citations"]:
                print(f"  [{c['index']}] {c['title']} @ {c['timestamp']}  {c['link']}")
    elif args.cmd == "serve":
        import uvicorn

        uvicorn.run("lectureiq.api:app", host=args.host, port=args.port)
