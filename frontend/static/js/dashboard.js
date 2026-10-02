// ===============================================================
// FITBUDDY USER DASHBOARD CONTROLLER
// ===============================================================

let currentPlanData = null;
let currentUser = null;

const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

document.addEventListener("DOMContentLoaded", async () => {
  await loadUserData();
});

async function loadUserData() {
  const userId = localStorage.getItem("fitbuddy_user_id");
  if (!userId) {
    showEmptyDashboardState();
    return;
  }

  try {
    // 1. Fetch user profile
    currentUser = await apiRequest(`/api/users/${userId}`);
    updateProfileDisplay(currentUser);

    // 2. Fetch latest workout plan
    const plan = await apiRequest(`/api/workouts/${userId}`);
    currentPlanData = plan;
    localStorage.setItem("fitbuddy_active_plan", JSON.stringify(plan));
    renderDashboard(plan);

  } catch (err) {
    console.warn("Could not load user or plan:", err);
    showEmptyDashboardState();
  }
}

function updateProfileDisplay(user) {
  const greetingEl = document.getElementById("dash-greeting");
  if (greetingEl) {
    greetingEl.textContent = `Good morning, ${user.name} 👋`;
  }

  const bar = document.getElementById("profile-summary-bar");
  if (bar) {
    bar.innerHTML = `
      <span class="badge badge-emerald">🎯 Goal: ${user.goal}</span>
      <span class="badge badge-blue">⚖️ Weight: ${user.weight} kg</span>
      <span class="badge badge-amber">⚡ Intensity: ${user.intensity}</span>
      <span class="badge badge-gray">🏆 Level: ${user.experience}</span>
      <span class="badge badge-gray">🏠 Location: ${user.workout_location}</span>
    `;
  }
}

function renderDashboard(plan) {
  // Use updated_plan if available, else original_plan
  const activePlan = plan.updated_plan || plan.original_plan;
  const week = activePlan.week || [];
  const completedDays = plan.completed_days || [];

  // Determine current day of week
  const todayIdx = new Date().getDay(); // 0 is Sunday
  const todayName = DAY_NAMES[todayIdx];

  // Find today's daily workout from week array (Monday-Sunday)
  let todayWorkout = week.find(d => d.day.toLowerCase() === todayName.toLowerCase());
  if (!todayWorkout && week.length > 0) {
    todayWorkout = week[0]; // fallback to day 1
  }

  // Render TODAY'S WORKOUT CARD
  const todayCard = document.getElementById("today-workout-container");
  if (todayCard && todayWorkout) {
    const isDone = completedDays.includes(todayWorkout.day.capitalize ? todayWorkout.day.capitalize() : todayWorkout.day);
    const exerciseCount = (todayWorkout.exercises || []).length;
    
    todayCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
        <div>
          <span class="badge ${todayWorkout.is_rest_day ? 'badge-blue' : 'badge-emerald'}">
            ${todayWorkout.is_rest_day ? 'Active Recovery' : 'Scheduled Workout'}
          </span>
          <h2 style="font-size: 1.6rem; margin-top: 0.5rem; color: var(--text-primary);">${todayWorkout.day}: ${todayWorkout.title}</h2>
          <p style="color: var(--text-secondary); font-size: 0.95rem;">
            ${exerciseCount} Movements • Rest: 45–90s • ${todayWorkout.recovery || 'Follow warm-up & cooldown'}
          </p>
        </div>
        <div>
          ${isDone 
            ? '<span class="badge badge-emerald" style="font-size: 0.85rem;">✓ COMPLETED</span>'
            : `<button class="btn btn-outline btn-sm" onclick="markTodayComplete('${todayWorkout.day}', true)">Mark Complete</button>`
          }
        </div>
      </div>

      <div style="margin-top: 1.25rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <a href="/dashboard/daily-workout?day=${todayWorkout.day}" class="btn btn-primary">
          Open Exercise Walkthrough →
        </a>
        <a href="/feedback" class="btn btn-secondary">
          Request AI Plan Adjustment
        </a>
      </div>
    `;
  }

  // Render 7-DAY SCHEDULE
  const scheduleGrid = document.getElementById("week-schedule-grid");
  if (scheduleGrid) {
    scheduleGrid.innerHTML = week.map(d => {
      const isToday = d.day.toLowerCase() === todayName.toLowerCase();
      const isDone = completedDays.includes(d.day);
      return `
        <div class="day-card ${isToday ? 'today' : ''} ${isDone ? 'completed' : ''}" onclick="window.location.href='/dashboard/daily-workout?day=${d.day}'">
          <div>
            <div class="day-name-tag">${d.day.substring(0, 3)}</div>
            <div class="day-workout-title">${d.title}</div>
          </div>
          <div class="day-meta">
            <span>${(d.exercises || []).length} ex</span>
            <div class="completion-status-indicator ${isDone ? 'status-done' : 'status-pending'}">
              ${isDone ? '● Done' : '○ Scheduled'}
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  // Render NUTRITION TIP & RECOVERY TIP & AI INSIGHT
  const nutritionEl = document.getElementById("dash-nutrition-tip");
  if (nutritionEl && plan.nutrition_tip) {
    const n = plan.nutrition_tip;
    nutritionEl.textContent = typeof n === "object" ? n.protein : n;
  }

  const recoveryEl = document.getElementById("dash-recovery-tip");
  if (recoveryEl) {
    recoveryEl.textContent = plan.recovery_tip || "Prioritize 8 hours sleep and active joint mobility.";
  }

  const aiInsightEl = document.getElementById("dash-ai-insight");
  if (aiInsightEl) {
    if (plan.updated_plan) {
      aiInsightEl.innerHTML = `<strong>Calibrated Plan:</strong> Gemini adapted this regimen based on your recent feedback.`;
    } else {
      aiInsightEl.innerHTML = `<strong>Baseline Active:</strong> 7-day custom regimen programmed. Submit feedback whenever you need volume adjusted.`;
    }
  }
}

async function markTodayComplete(day, status) {
  if (!currentPlanData) return;
  try {
    const res = await apiRequest(`/api/workouts/${currentPlanData.id}/complete`, {
      method: "POST",
      body: JSON.stringify({ day: day, completed: status })
    });
    currentPlanData.completed_days = res.completed_days;
    showToast(`Marked ${day} workout as completed! Great work.`, "success");
    renderDashboard(currentPlanData);
  } catch (err) {
    showToast("Could not update completion status.", "error");
  }
}

function showEmptyDashboardState() {
  const container = document.getElementById("dashboard-root");
  if (container) {
    container.innerHTML = `
      <div class="empty-state" style="max-width: 600px; margin: 4rem auto;">
        <div class="empty-icon">🏋️‍♂️</div>
        <h2>No Active Workout Plan Found</h2>
        <p style="margin: 0.75rem 0 1.75rem; color: var(--text-secondary);">
          Create your personalized fitness profile and let Gemini generate your custom 7-day workout split.
        </p>
        <a href="/onboarding" class="btn btn-primary">Start Onboarding Wizard →</a>
      </div>
    `;
  }
}
