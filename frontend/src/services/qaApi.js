import { httpClient } from "./httpClient";

export async function askQuestion({ question, documentId, topK }) {
  const payload = { question };

  if (documentId) {
    payload.document_id = documentId;
  }
  if (typeof topK === "number" && Number.isFinite(topK)) {
    payload.top_k = topK;
  }

  const response = await httpClient.post("/qa", payload);
  return response.data;
}
