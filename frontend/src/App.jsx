import { useCallback, useEffect, useMemo, useState } from "react";
import UploadPanel from "./components/UploadPanel.jsx";
import DocumentList from "./components/DocumentList.jsx";
import QAConsole from "./components/QAConsole.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import { listDocuments, uploadDocument, deleteDocument } from "./services/documentApi";
import { askQuestion } from "./services/qaApi";

const initialBanner = { message: "", tone: "info" };

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [qaHistory, setQaHistory] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [banner, setBanner] = useState(initialBanner);

  useEffect(() => {
    async function fetchDocuments() {
      setIsLoadingDocuments(true);
      try {
        const data = await listDocuments();
        const items = data.items ?? [];
        setDocuments(items);
        if (items.length > 0) {
          setSelectedDocumentId(items[0].document_id);
        }
      } catch (error) {
        console.error("Failed to load documents", error);
        setBanner({
          message: "無法載入文件列表，請稍後再試。",
          tone: "error",
        });
      } finally {
        setIsLoadingDocuments(false);
      }
    }

    fetchDocuments();
  }, []);

  const selectedDocument = useMemo(
    () => documents.find((doc) => doc.document_id === selectedDocumentId) ?? null,
    [documents, selectedDocumentId]
  );

  const handleUpload = useCallback(
    async (file) => {
      setUploading(true);
      try {
        const document = await uploadDocument(file);
        setDocuments((prev) => [document, ...prev.filter((item) => item.document_id !== document.document_id)]);
        setSelectedDocumentId(document.document_id);
        setQaHistory([]);
        setBanner({ message: "文件已成功上傳並處理。", tone: "success" });
      } catch (error) {
        console.error("Failed to upload document", error);
        const message = error.response?.data?.error ?? "上傳文件失敗，請確認檔案並重試。";
        setBanner({ message, tone: "error" });
      } finally {
        setUploading(false);
      }
    },
    []
  );

  const handleDelete = useCallback(
    async (documentId) => {
      setDeletingId(documentId);
      try {
        await deleteDocument(documentId);
        setDocuments((prev) => prev.filter((doc) => doc.document_id !== documentId));
        if (selectedDocumentId === documentId) {
          setSelectedDocumentId(null);
          setQaHistory([]);
        }
        setBanner({ message: "文件已刪除。", tone: "success" });
      } catch (error) {
        console.error("Failed to delete document", error);
        const message = error.response?.data?.error ?? "刪除文件失敗，請稍後再試。";
        setBanner({ message, tone: "error" });
      } finally {
        setDeletingId(null);
      }
    },
    [selectedDocumentId]
  );

  const handleSelectDocument = useCallback((documentId) => {
    setSelectedDocumentId(documentId);
    setQaHistory([]);
  }, []);

  const handleAskQuestion = useCallback(
    async ({ question, topK }) => {
      if (!question.trim()) {
        setBanner({ message: "請先輸入問題。", tone: "error" });
        return;
      }

      if (documents.length === 0) {
        setBanner({ message: "請先上傳至少一份 PDF。", tone: "error" });
        return;
      }

      const safeTopK = Number.isFinite(topK) && topK > 0 ? Math.min(Math.floor(topK), 10) : 3;

      const entryId = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}`;
      const newEntry = {
        id: entryId,
        question,
        status: "pending",
        matches: [],
      };
      setQaHistory((prev) => [...prev, newEntry]);
      setIsAsking(true);

      try {
        const response = await askQuestion({
          question,
          documentId: selectedDocumentId ?? undefined,
          topK: safeTopK,
        });

        setQaHistory((prev) =>
          prev.map((item) =>
            item.id === entryId
              ? {
                  ...item,
                  status: "answered",
                  answer: response.answer,
                  matches: response.matches ?? [],
                }
              : item
          )
        );
      } catch (error) {
        console.error("Failed to get answer", error);
        const message = error.response?.data?.error ?? "生成回答失敗，請稍後再試。";
        setBanner({ message, tone: "error" });
        setQaHistory((prev) => prev.filter((item) => item.id !== entryId));
      } finally {
        setIsAsking(false);
      }
    },
    [documents.length, selectedDocumentId]
  );

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>ChatYourNotes</h1>
          <p className="subtitle">依據流程圖打造的 PDF 知識助理</p>
        </div>
      </header>

      <main className="layout-grid">
        <section className="panel">
          <UploadPanel onUpload={handleUpload} isUploading={uploading} />
        </section>

        <section className="panel">
          <DocumentList
            documents={documents}
            selectedId={selectedDocumentId}
            onSelect={handleSelectDocument}
            onDelete={handleDelete}
            isLoading={isLoadingDocuments}
            deletingId={deletingId}
          />
        </section>

        <section className="panel qa-panel">
          <QAConsole
            selectedDocument={selectedDocument}
            history={qaHistory}
            onAsk={handleAskQuestion}
            isAsking={isAsking}
            disabled={documents.length === 0}
          />
        </section>
      </main>

      <StatusBanner
        message={banner.message}
        tone={banner.tone}
        onDismiss={() => setBanner(initialBanner)}
      />
    </div>
  );
}
