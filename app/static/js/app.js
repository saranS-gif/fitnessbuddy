// ===================================================
// FITBUDDY — CORE CLIENT UTILITIES
// ===================================================

function showToast(message, type = "info") {
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

async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    "Content-Type": "application/json"
  };

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    const errorMsg = data.message || "Request failed. Please try again.";
    throw new Error(errorMsg);
  }

  return data;
}

// Helpers for localStorage
function getStoredUserId() {
  return localStorage.getItem("fitbuddy_user_id");
}

function getStoredPlanId() {
  return localStorage.getItem("fitbuddy_plan_id");
}

function setStoredPlan(userId, planId, plan) {
  if (userId) localStorage.setItem("fitbuddy_user_id", userId);
  if (planId) localStorage.setItem("fitbuddy_plan_id", planId);
  if (plan) localStorage.setItem("fitbuddy_plan", JSON.stringify(plan));
}
