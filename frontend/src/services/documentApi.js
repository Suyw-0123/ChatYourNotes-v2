import { httpClient } from "./httpClient";

export async function listDocuments() {
  const response = await httpClient.get("/documents");
  return response.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await httpClient.post("/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteDocument(documentId) {
  const response = await httpClient.delete(`/documents/${documentId}`);
  return response.data;
}
