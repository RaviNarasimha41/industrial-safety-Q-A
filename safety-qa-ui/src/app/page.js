"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import axios from "axios";

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState([]);
  const [showBatch, setShowBatch] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const highlightTerms = (answer, question) => {
    const terms = question.split(" ").filter(t => t.length > 2);
    let highlighted = answer;
    terms.forEach(term => {
      const regex = new RegExp(`(${term})`, "gi");
      highlighted = highlighted.replace(
        regex,
        `<span class="bg-yellow-200 font-semibold">$1</span>`
      );
    });
    return highlighted;
  };

  const addReaction = (index, emoji) => {
    setMessages(prev => {
      const updated = [...prev];
      updated[index].reaction = emoji;
      return updated;
    });
  };

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setMessages(prev => [...prev, { type: "user", text: query }]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/ask", {
        q: query,
        k: 3,
        mode: "hybrid",
      });

      const answerText = res.data.answer || "No answer found";
      const highlightedAnswer = highlightTerms(answerText, query);
      const contexts = res.data.contexts || [];

      setMessages(prev => [
        ...prev,
        { type: "bot", text: highlightedAnswer, sources: contexts, reaction: null },
      ]);

      setEvaluation(prev => [
        ...prev,
        {
          question: query,
          answer: answerText,
          reranker: res.data.reranker_used || "hybrid",
          abstained: res.data.abstained ? "Yes" : "No",
          reason: res.data.reason || "-",
          contexts: contexts.map(c => ({
            chunk_id: c.chunk_id,
            source_title: c.source_title,
            source_url: c.source_url,
            text: c.text,
            final_score: c.final_score?.toFixed(2) || "-"
          })),
          manualAsk: true,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { type: "bot", text: "Error fetching answer.", sources: [] },
      ]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  const handleRunBatch = async () => {
    try {
      setShowBatch(true);
      const res = await fetch("/eight_questions.json");
      const questions = await res.json();

      for (const q of questions) {
        const batchRes = await axios.post("http://127.0.0.1:8000/ask", {
          q: q.question,
          k: 3,
          mode: "hybrid",
        });

        setEvaluation(prev => [
          ...prev,
          {
            question: q.question,
            answer: batchRes.data.answer || "No answer found",
            reranker: batchRes.data.reranker_used || "hybrid",
            abstained: batchRes.data.abstained ? "Yes" : "No",
            reason: batchRes.data.reason || "-",
            contexts: batchRes.data.contexts.map(c => ({
              chunk_id: c.chunk_id,
              source_title: c.source_title,
              source_url: c.source_url,
              text: c.text,
              final_score: c.final_score?.toFixed(2) || "-"
            })),
            manualAsk: false,
          },
        ]);
      }
    } catch (err) {
      console.error("Error running batch evaluation:", err);
    }
  };

  const evalRows = useMemo(
    () => evaluation.filter(e => e.manualAsk || showBatch),
    [evaluation, showBatch]
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <h1 className="text-3xl font-bold mb-6 text-gray-800 text-center">
        Industrial Safety Q&A
      </h1>

      {/* Chat messages */}
      <div className="w-full max-w-4xl flex flex-col gap-4 mb-4 p-4 bg-white rounded-2xl shadow-xl overflow-y-auto"
           style={{ maxHeight: "50vh" }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"} `}>
            <div className={`px-4 py-2 rounded-2xl max-w-full sm:max-w-[70%] break-words 
              ${msg.type === "user" ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"}`}>
              <div dangerouslySetInnerHTML={{ __html: msg.text }} />
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 text-sm text-gray-700">
                  <strong>Sources:</strong>
                  <ul className="list-disc ml-5">
                    {msg.sources.map((s, i) => (
                      <li key={i}>
                        <a href={s.source_url} target="_blank" className="text-blue-600 hover:underline">
                          {s.source_title}
                        </a> | Score: {s.final_score}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {msg.type === "bot" && (
                <div className="mt-2 flex gap-2 text-lg flex-wrap">
                  {["👍", "👎", "❤️"].map(emoji => (
                    <button key={emoji} onClick={() => addReaction(idx, emoji)}>
                      {msg.reaction === emoji ? <span className="animate-bounce">{emoji}</span> : emoji}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-black px-4 py-2 rounded-2xl max-w-[50%]">
              Loading...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="w-full max-w-4xl flex flex-col sm:flex-row gap-2 mt-2">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask your question"
          className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          onKeyDown={e => e.key === "Enter" && handleAsk()}
        />
        <div className="flex gap-2 mt-2 sm:mt-0">
          <button
            onClick={handleAsk}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors"
          >
            Ask
          </button>
          <button
            onClick={handleRunBatch}
            className="bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition-colors"
          >
            Run 8-Question Evaluation
          </button>
        </div>
      </div>

      {/* Evaluation Table */}
      {evalRows.length > 0 && (
        <div className="w-full max-w-full sm:max-w-5xl mt-8 p-4 bg-white rounded-2xl shadow-xl overflow-x-auto">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            Evaluation Results (Baseline vs Hybrid)
          </h2>
          <table className="min-w-full border-collapse border border-gray-300 text-black">
            <thead>
              <tr className="bg-gray-100 text-black">
                <th className="border border-gray-300 px-4 py-2 text-left">Question</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Answer</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Reranker</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Abstained</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Reason</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Contexts</th>
              </tr>
            </thead>
            <tbody>
              {evalRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2">{row.question}</td>
                  <td className="border border-gray-300 px-4 py-2">{row.answer}</td>
                  <td className="border border-gray-300 px-4 py-2">{row.reranker}</td>
                  <td className="border border-gray-300 px-4 py-2">{row.abstained}</td>
                  <td className="border border-gray-300 px-4 py-2">{row.reason}</td>
                  <td className="border border-gray-300 px-4 py-2">
                    {row.contexts.map((c, i) => (
                      <div key={i} className="mb-1">
                        <a href={c.source_url} target="_blank" className="text-blue-600 hover:underline">{c.source_title}</a> | Score: {c.final_score}
                      </div>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
