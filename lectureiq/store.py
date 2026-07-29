"""ChromaDB-backed chunk store.

Uses Chroma's built-in embedding model (an ONNX MiniLM), so indexing and search
work offline with no torch and no extra setup. Swapping to a hosted embedding
model later is a one-function change here.
"""
import chromadb

from . import config


def _collection():
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return client.get_or_create_collection(config.COLLECTION)


def index_chunks(lecture, chunks):
    col = _collection()
    ids, docs, metas = [], [], []
    for i, ch in enumerate(chunks):
        ids.append(f"{lecture.video_id}-{i}")
        docs.append(ch.text)
        metas.append(
            {
                "video_id": lecture.video_id,
                "title": lecture.title,
                "url": lecture.url,
                "start": ch.start,
                "end": ch.end,
            }
        )
    # upsert so re-ingesting the same lecture refreshes it instead of duplicating.
    col.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def search(question, k=5):
    col = _collection()
    count = col.count()
    if count == 0:
        return []
    res = col.query(query_texts=[question], n_results=min(k, count))
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "meta": meta, "distance": dist})
    return hits
