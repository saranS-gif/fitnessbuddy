// ===================================================
// FITBUDDY — DASHBOARD & WORKOUT CONTROLLER
// ===================================================

let currentPlanId = null;
let currentUserId = null;
let currentPlanData = null;
let completedDaysList = [];

document.addEventListener("DOMContentLoaded", async () => {
  currentUserId = getStoredUserId();
  currentPlanId = getStoredPlanId();

  if (!currentPlanId && !currentUserId) {
    showEmptyState();
    return;
  }

  await loadDashboardData();
});

async function loadDashboardData() {
  try {
    // 1. Fetch user info if available
    if (currentUserId) {
      try {
        const user = await apiRequest(`/api/users/${currentUserId}`);
        renderUserHeader(user);
      } catch (e) {
        console.warn("Could not load user profile:", e);
      }
    }

    // 2. Fetch plan info
    if (currentPlanId) {
      const planRes = await apiRequest(`/api/plan/${currentPlanId}`);
      currentPlanData = planRes.active_plan;
      completedDaysList = planRes.completed_days || [];
      renderWorkoutPlan(currentPlanData, completedDaysList);
    } else {
      showEmptyState();
    }
  } catch (err) {
    showEmptyState(err.message);
  }
}

function renderUserHeader(user) {
  const greetingEl = document.getElementById("user-greeting");
  if (greetingEl) {
    greetingEl.textContent = `Welcome, ${user.name} 👋`;
  }

  const badgesEl = document.getElementById("user-badges");
  if (badgesEl) {
    badgesEl.innerHTML = `
      <span class="badge" style="background:#ecfdf5;color:#059669;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">🎯 ${user.goal}</span>
      <span class="badge" style="background:#eff6ff;color:#2563eb;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">⚖️ ${user.weight} kg</span>
      <span class="badge" style="background:#fef3c7;color:#d97706;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">📏 ${user.height} cm</span>
      <span class="badge" style="background:#f3e8ff;color:#9333ea;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">⚡ ${user.intensity}</span>
      <span class="badge" style="background:#f1f5f9;color:#475569;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">🏆 ${user.experience}</span>
      <span class="badge" style="background:#f1f5f9;color:#475569;padding:0.3rem 0.8rem;border-radius:9999px;font-weight:600;font-size:0.85rem;">🏠 ${user.location}</span>
    `;
  }
}

function renderWorkoutPlan(plan, completedDays = []) {
  const container = document.getElementById("workout-week-container");
  if (!container) return;

  if (!plan || !plan.days || plan.days.length === 0) {
    showEmptyState();
    return;
  }

  // Summary & Weekly Goal
  const summaryEl = document.getElementById("plan-summary");
  if (summaryEl && plan.summary) {
    summaryEl.textContent = plan.summary;
  }
  const goalEl = document.getElementById("plan-weekly-goal");
  if (goalEl && plan.weekly_goal) {
    goalEl.textContent = `Weekly Goal: ${plan.weekly_goal}`;
  }

  // Render 7 Days
  container.innerHTML = "";
  plan.days.forEach(dayObj => {
    const isRest = dayObj.type === "Rest" || (dayObj.exercises && dayObj.exercises.length === 0);
    const isCompleted = completedDays.includes(dayObj.day);

    const card = document.createElement("div");
    card.className = `day-card ${isRest ? 'rest-day' : ''}`;

    let exercisesHtml = "";
    (dayObj.exercises || []).forEach(ex => {
      exercisesHtml += `
        <div class="exercise-item">
          <div class="exercise-name">${ex.name}</div>
          <div class="exercise-meta">
            <span><strong>Sets:</strong> ${ex.sets}</span>
            <span><strong>Reps:</strong> ${ex.reps}</span>
            <span><strong>Rest:</strong> ${ex.rest_seconds}s</span>
          </div>
          ${ex.instructions ? `<div class="exercise-instructions">${ex.instructions}</div>` : ''}
        </div>
      `;
    });

    const warmupHtml = (dayObj.warmup && dayObj.warmup.length > 0)
      ? `<div class="routine-phase"><div class="phase-label">Warm-Up</div><ul class="phase-list">${dayObj.warmup.map(w => `<li>${w}</li>`).join('')}</ul></div>`
      : '';

    const cooldownHtml = (dayObj.cooldown && dayObj.cooldown.length > 0)
      ? `<div class="routine-phase"><div class="phase-label">Cool-Down</div><ul class="phase-list">${dayObj.cooldown.map(c => `<li>${c}</li>`).join('')}</ul></div>`
      : '';

    const recoveryHtml = dayObj.recovery
      ? `<div class="routine-phase"><div class="phase-label">Recovery Guidance</div><p style="color:var(--text-muted);font-size:0.85rem;">${dayObj.recovery}</p></div>`
      : '';

    card.innerHTML = `
      <div class="day-header">
        <span class="day-name">${dayObj.day}</span>
        <span class="day-badge ${isRest ? 'rest' : 'workout'}">${isRest ? 'Rest Day' : 'Workout'}</span>
      </div>
      <div class="day-focus">${dayObj.focus || 'Training Session'}</div>
      
      <div style="flex-grow:1;">
        ${exercisesHtml}
        ${warmupHtml}
        ${cooldownHtml}
        ${recoveryHtml}
      </div>

      <div class="day-complete-btn">
        <button class="btn btn-sm ${isCompleted ? 'btn-secondary' : 'btn-outline'}" 
                onclick="toggleDayCompletion('${dayObj.day}', ${!isCompleted})">
          ${isCompleted ? '✓ Completed' : 'Mark as Complete'}
        </button>
      </div>
    `;

    container.appendChild(card);
  });

  // Render Nutrition Guidance
  if (plan.nutrition) {
    const nut = plan.nutrition;
    const nutCard = document.getElementById("nutrition-section");
    if (nutCard) {
      nutCard.style.display = "block";
      document.getElementById("nut-calories").textContent = nut.calories_guidance || "Caloric balance";
      document.getElementById("nut-protein").textContent = nut.protein_guidance || "Adequate lean protein";
      document.getElementById("nut-hydration").textContent = nut.hydration || "2-3L water daily";
      document.getElementById("nut-tip").textContent = nut.tip || "Focus on balanced whole-food meals";
    }
  }

  // Disclaimer
  const discEl = document.getElementById("plan-disclaimer");
  if (discEl && plan.disclaimer) {
    discEl.textContent = plan.disclaimer;
  }
}

async function toggleDayCompletion(day, shouldComplete) {
  if (!currentPlanId) return;

  try {
    const res = await apiRequest(`/api/plan/${currentPlanId}/complete`, {
      method: "POST",
      body: JSON.stringify({ day: day, completed: shouldComplete })
    });

    completedDaysList = res.completed_days || [];
    renderWorkoutPlan(currentPlanData, completedDaysList);
    showToast(shouldComplete ? `Great job completing ${day}!` : `${day} marked uncompleted`, "success");
  } catch (err) {
    showToast("Could not update completion status.", "error");
  }
}

function showEmptyState(msg) {
  const container = document.getElementById("workout-week-container");
  if (container) {
    container.innerHTML = `
      <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 4rem 2rem;">
        <h3 style="margin-bottom: 0.5rem;">No Workout Plan Found</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
          ${msg || "You haven't generated your personalized 7-day fitness plan yet."}
        </p>
        <a href="/onboarding" class="btn btn-primary">Create My Plan Now →</a>
      </div>
    `;
  }
}
