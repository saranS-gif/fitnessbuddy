import './style.css';

// ===================================================
// FITBUDDY — CLIENT CORE MODULE (VITE)
// ===================================================

const DEFAULT_API_URL = "https://fitnessbuddy-lhi3.onrender.com";
const isLocalFastAPI =
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") &&
  window.location.port === "8000";

export const API_BASE_URL =
  window.FITBUDDY_API_URL ||
  localStorage.getItem("fitbuddy_api_url") ||
  (isLocalFastAPI ? "" : DEFAULT_API_URL);

export function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

export async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    "Content-Type": "application/json",
  };

  const adminToken = localStorage.getItem("fitbuddy_admin_token");
  const userToken = localStorage.getItem("fitbuddy_token") || localStorage.getItem("token");
  const activeToken = adminToken || userToken;

  if (activeToken) {
    defaultHeaders["Authorization"] = `Bearer ${activeToken}`;
  }

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL.replace(/\/+$/, "")}${endpoint.startsWith("/") ? endpoint : "/" + endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    const errorMsg = data.message || data.detail || "Request failed. Please try again.";
    throw new Error(errorMsg);
  }

  return data;
}

// Make helpers available globally for any legacy scripts
window.apiRequest = apiRequest;
window.showToast = showToast;
window.API_BASE_URL = API_BASE_URL;

console.log("[FitBuddy] Frontend loaded. Backend API:", API_BASE_URL);
