// api.js — single place that talks to the FastAPI backend.
import axios from "axios";

const BASE_URL = "http://localhost:8000";

const client = axios.create({ baseURL: BASE_URL });

// --- Structured form (REST) ---
export const createInteraction = (data) =>
  client.post("/interactions", data).then((r) => r.data);

export const fetchInteractions = () =>
  client.get("/interactions").then((r) => r.data);

export const updateInteraction = (id, data) =>
  client.put(`/interactions/${id}`, data).then((r) => r.data);

export const deleteInteraction = (id) =>
  client.delete(`/interactions/${id}`).then((r) => r.data);

// --- Conversational (LangGraph agent) ---
export const sendChatMessage = (message) =>
  client.post("/chat", { message }).then((r) => r.data);
