import { httpClient } from "./httpClient";

export async function fetchNotes() {
  const response = await httpClient.get("/notes");
  return response.data;
}

export async function createNote(payload) {
  const response = await httpClient.post("/notes", payload);
  return response.data;
}

export async function deleteNote(noteId) {
  const response = await httpClient.delete(`/notes/${noteId}`);
  return response.data;
}
