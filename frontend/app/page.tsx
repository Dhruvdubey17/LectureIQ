"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Citation = { index: number; title: string; timestamp: string; link: string };
type Answer = { answer: string; citations: Citation[] };

export default function Home() {
  const [url, setUrl] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState("");

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Answer | null>(null);

  async function ingest() {
    setIngesting(true);
    setIngestMsg("");
    try {
      const r = await fetch(`${API}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "ingest failed");
      setIngestMsg(`Indexed "${data.title}" into ${data.chunks} chunks.`);
    } catch (e) {
      setIngestMsg(`Error: ${(e as Error).message}`);
    } finally {
      setIngesting(false);
    }
  }

  async function ask() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "ask failed");
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="wrap">
      <header>
        <h1>LectureIQ</h1>
        <p className="tag">Answers that cite the lecture and the exact timestamp. Grounded, not made up.</p>
      </header>

      <section className="card">
        <h2>Add a lecture</h2>
        <div className="row">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a YouTube lecture URL"
          />
          <button onClick={ingest} disabled={!url || ingesting}>
            {ingesting ? "Indexing..." : "Ingest"}
          </button>
        </div>
        {ingestMsg && <p className="msg">{ingestMsg}</p>}
      </section>

      <section className="card">
        <h2>Ask a question</h2>
        <div className="row">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && question && !loading && ask()}
            placeholder="e.g. What does the activation of a neuron represent?"
          />
          <button onClick={ask} disabled={!question || loading}>
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {error && <p className="err">Error: {error}</p>}

        {result && (
          <div className="answer">
            <p className="text">{result.answer}</p>
            {result.citations.length > 0 && (
              <>
                <h3>Sources</h3>
                <ul className="cites">
                  {result.citations.map((c) => (
                    <li key={c.index}>
                      <a href={c.link} target="_blank" rel="noreferrer">
                        <span className="badge">[{c.index}]</span> {c.title}{" "}
                        <span className="ts">@ {c.timestamp}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
