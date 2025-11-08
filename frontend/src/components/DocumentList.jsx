export default function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDelete,
  isLoading,
  deletingId,
}) {
  return (
    <div className="document-list">
      <header className="panel-header">
        <div>
          <h2>文件總覽</h2>
          <p className="description">可瀏覽摘要、切換焦點或移除舊文件。</p>
        </div>
        {isLoading && <span className="status">載入中...</span>}
      </header>

      {documents.length === 0 && !isLoading ? (
        <p className="empty-state">尚未上傳任何文件。</p>
      ) : (
        <ul>
          {documents.map((doc) => {
            const isSelected = doc.document_id === selectedId;
            const isDeleting = deletingId === doc.document_id;
            return (
              <li key={doc.document_id} className={isSelected ? "selected" : ""}>
                <div className="document-meta">
                  <div className="document-names">
                    <strong>{doc.original_filename}</strong>
                    <span className="time">{formatTime(doc.uploaded_at)}</span>
                  </div>
                  <p className="summary-preview">{doc.summary_preview || "尚無摘要"}</p>
                  <div className="document-actions">
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => onSelect(doc.document_id)}
                      disabled={isSelected}
                    >
                      {isSelected ? "已選取" : "切換"}
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => onDelete(doc.document_id)}
                      disabled={isDeleting}
                    >
                      {isDeleting ? "刪除中..." : "刪除"}
                    </button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function formatTime(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  return date.toLocaleString();
}
