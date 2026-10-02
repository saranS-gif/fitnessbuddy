// ===============================================================
// FITBUDDY CLIENT CORE UTILITIES
// ===============================================================

async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    "Content-Type": "application/json"
  };

  const adminToken = localStorage.getItem("fitbuddy_admin_token");
  const userToken = localStorage.getItem("fitbuddy_token") || localStorage.getItem("token");
  const activeToken = adminToken || userToken;

  if (activeToken) {
    defaultHeaders["Authorization"] = `Bearer ${activeToken}`;
  }

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Unable to complete request at this time.");
  }

  return response.json();
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

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
