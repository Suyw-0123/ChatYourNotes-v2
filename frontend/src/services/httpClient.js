import axios from "axios";

const apiBase = (import.meta.env.VITE_API_BASE ?? "http://localhost:8000").replace(/\/+$/, "");

export const httpClient = axios.create({
  baseURL: `${apiBase}/api`,
  timeout: 20000,
});
