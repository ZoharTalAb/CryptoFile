import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getStoredToken() {
  return (
    localStorage.getItem("cryptofile_token") ??
    sessionStorage.getItem("cryptofile_token")
  );
}

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getStoredToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});