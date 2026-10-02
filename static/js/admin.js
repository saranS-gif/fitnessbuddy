// ===============================================================
// FITBUDDY ADMIN CONSOLE CONTROLLER
// ===============================================================

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("admin-stats-row")) {
    loadAdminDashboard();
  }
  if (document.getElementById("user-dossier-root")) {
    loadUserDossier();
  }
});

async function handleAdminLogin() {
  const u = document.getElementById("admin-username").value.trim();
  const p = document.getElementById("admin-password").value.trim();

  try {
    const res = await apiRequest("/api/admin/login", {
      method: "POST",
      body: JSON.stringify({ username: u, password: p })
    });
    localStorage.setItem("fitbuddy_admin_token", res.access_token);
    showToast("Logged in as Administrator", "success");
    window.location.href = "/admin/dashboard";
  } catch (err) {
    showToast("Admin authentication failed: " + err.message, "error");
  }
}

async function loadAdminDashboard() {
  const token = localStorage.getItem("fitbuddy_admin_token");
  if (!token) {
    window.location.href = "/admin/login";
    return;
  }

  try {
    // 1. Fetch real DB stats
    const stats = await apiRequest("/api/admin/stats", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    document.getElementById("stat-users").textContent = stats.total_users;
    document.getElementById("stat-plans-gen").textContent = stats.plans_generated;
    document.getElementById("stat-plans-upd").textContent = stats.plans_updated;
    document.getElementById("stat-feedback").textContent = stats.feedback_submitted;

    // 2. Fetch Users
    const users = await apiRequest("/api/admin/users", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    const tbody = document.getElementById("admin-users-tbody");
    if (!tbody) return;

    if (users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No registered athletes yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = users.map(u => `
      <tr>
        <td><strong>${u.name}</strong></td>
        <td>${u.age} yrs (${u.weight}kg)</td>
        <td><span class="badge badge-emerald">${u.goal}</span></td>
        <td>${u.intensity}</td>
        <td>${new Date(u.created_at).toLocaleDateString()}</td>
        <td><span class="badge ${u.plan_status.includes('Updated') ? 'badge-blue' : 'badge-gray'}">${u.plan_status}</span></td>
        <td style="display: flex; gap: 0.5rem;">
          <a href="/admin/user-detail?id=${u.id}" class="btn btn-secondary btn-sm">Inspect</a>
          <button class="btn btn-outline btn-sm" style="color: var(--danger); border-color: var(--danger);" onclick="deleteUser(${u.id})">Delete</button>
        </td>
      </tr>
    `).join("");

  } catch (err) {
    showToast("Admin session expired or unauthorized.", "error");
    window.location.href = "/admin/login";
  }
}

async function deleteUser(userId) {
  if (!confirm(`Are you sure you want to delete user #${userId}? All plans and feedback will be cascade removed.`)) return;

  const token = localStorage.getItem("fitbuddy_admin_token");
  try {
    await apiRequest(`/api/admin/users/${userId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${token}` }
    });
    showToast(`User #${userId} deleted successfully.`, "success");
    loadAdminDashboard();
  } catch (err) {
    showToast("Error deleting user: " + err.message, "error");
  }
}

async function loadUserDossier() {
  const urlParams = new URLSearchParams(window.location.search);
  const userId = urlParams.get("id");
  if (!userId) {
    window.location.href = "/admin/dashboard";
    return;
  }

  const token = localStorage.getItem("fitbuddy_admin_token");
  try {
    const data = await apiRequest(`/api/admin/users/${userId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    const user = data.user;
    document.getElementById("dossier-name").textContent = user.name;
    document.getElementById("dossier-meta").textContent = `ID #${user.id} • Registered ${new Date(user.created_at).toLocaleDateString()}`;

    document.getElementById("dossier-profile-grid").innerHTML = `
      <div><strong>Age:</strong> ${user.age}</div>
      <div><strong>Weight:</strong> ${user.weight} kg</div>
      <div><strong>Goal:</strong> ${user.goal}</div>
      <div><strong>Intensity:</strong> ${user.intensity}</div>
      <div><strong>Level:</strong> ${user.experience}</div>
      <div><strong>Location:</strong> ${user.workout_location}</div>
    `;

    // Feedbacks list
    const fbList = document.getElementById("dossier-feedbacks");
    if (data.feedbacks && data.feedbacks.length > 0) {
      fbList.innerHTML = data.feedbacks.map(f => `
        <div style="background: var(--surface-alt); padding: 0.75rem 1rem; border-radius: var(--radius-sm); margin-bottom: 0.5rem; font-size: 0.9rem;">
          "${f.feedback_text}"
          <span style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">Submitted ${new Date(f.created_at).toLocaleString()}</span>
        </div>
      `).join("");
    } else {
      fbList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No feedback submitted yet.</p>`;
    }

    // Plans list
    const plansList = document.getElementById("dossier-plans");
    if (data.plans && data.plans.length > 0) {
      plansList.innerHTML = data.plans.map(p => `
        <div class="card" style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong>Plan #${p.id}</strong>
            <span class="badge ${p.has_updated_plan ? 'badge-emerald' : 'badge-gray'}">
              ${p.has_updated_plan ? 'Calibrated Post-Feedback' : 'Baseline Original'}
            </span>
          </div>
          <div style="font-size: 0.85rem; color: var(--text-secondary);">
            Revisions on record: ${(p.history || []).length}
          </div>
        </div>
      `).join("");
    } else {
      plansList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No plans created yet.</p>`;
    }

  } catch (err) {
    showToast("Could not load user dossier.", "error");
  }
}
