import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function QAConsole({ selectedDocument, history, onAsk, isAsking, disabled }) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(3);

  const handleSubmit = (event) => {
    event.preventDefault();
    onAsk({ question, topK });
    setQuestion("");
  };

  return (
    <div className="qa-console">
      <header className="panel-header">
        <div>
          <h2>問答面板</h2>
          {selectedDocument ? (
            <p className="description">
              目前焦點：<span className="mono">{selectedDocument.original_filename}</span>
            </p>
          ) : (
            <p className="description">無選取文件，會從全部內容檢索。</p>
          )}
        </div>
      </header>

      <div className="qa-history">
        {history.length === 0 ? (
          <p className="empty-state">提出問題後，系統會顯示回答與對應片段。</p>
        ) : (
          history.map((item) => (
            <article key={item.id} className="qa-item">
              <h3>Q：{item.question}</h3>
              {item.status === "answered" ? (
                <div className="qa-answer">
                  <ReactMarkdown
                    className="qa-answer-markdown"
                    remarkPlugins={[remarkGfm]}
                  >
                    {item.answer}
                  </ReactMarkdown>
                  {item.matches?.length ? (
                    <details>
                      <summary>檢索片段（Top {item.matches.length}）</summary>
                      <ol>
                        {item.matches.map((match, index) => (
                          <li key={match.id ?? index}>
                            <p className="match-content">{match.content}</p>
                            <p className="match-meta">
                              來源文件：{match.document_id ?? "未知"}｜分塊：{match.chunk_index ?? "-"}
                            </p>
                          </li>
                        ))}
                      </ol>
                    </details>
                  ) : null}
                </div>
              ) : (
                <p className="pending">產生回答中...</p>
              )}
            </article>
          ))
        )}
      </div>

      <form className="qa-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="請輸入想詢問的問題"
          rows={3}
          disabled={disabled || isAsking}
        />

        <div className="qa-controls">
          <label>
            Top K：
            <input
              type="number"
              min={1}
              max={10}
              value={topK}
              onChange={(event) => {
                const value = Number(event.target.value);
                if (Number.isNaN(value)) {
                  setTopK(3);
                } else {
                  setTopK(Math.min(Math.max(1, value), 10));
                }
              }}
              disabled={isAsking}
            />
          </label>
          <button type="submit" disabled={disabled || isAsking}>
            {isAsking ? "生成中..." : "送出問題"}
          </button>
        </div>
      </form>
    </div>
  );
}
