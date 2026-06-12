import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
});

export async function fetchDashboardStats() {
  const { data } = await api.get("/dashboard/stats");
  return data;
}

export async function fetchCategoryBreakdown() {
  const { data } = await api.get("/analytics/category-breakdown");
  return data;
}

export async function fetchSentimentTrend() {
  const { data } = await api.get("/analytics/sentiment-trend");
  return data;
}

export async function fetchInbox() {
  const { data } = await api.get("/dashboard/inbox");
  return data;
}

export async function fetchAgentActivity() {
  const { data } = await api.get("/dashboard/agent-activity");
  return data;
}

export default api;
