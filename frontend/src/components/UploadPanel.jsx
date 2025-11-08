import { useRef, useState } from "react";

export default function UploadPanel({ onUpload, isUploading }) {
  const fileInputRef = useRef(null);
  const [selectedName, setSelectedName] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    setSelectedName(file ? file.name : "");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      alert("請先選擇一個 PDF 檔案。");
      return;
    }
    try {
      await onUpload(file);
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      setSelectedName("");
    }
  };

  return (
    <form className="upload-panel" onSubmit={handleSubmit}>
      <header>
        <h2>上傳 PDF</h2>
        <p>文件會依流程自動轉文字、摘要並寫入向量資料庫。</p>
      </header>

      <div className="upload-field">
        <label className="file-input">
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <span>{selectedName || "選擇 PDF 檔案"}</span>
        </label>
        <button type="submit" disabled={isUploading}>
          {isUploading ? "處理中..." : "開始上傳"}
        </button>
      </div>

      <p className="hint">支援單一 PDF 上傳，建議容量 &lt; 15MB 以縮短處理時間。</p>
    </form>
  );
}
