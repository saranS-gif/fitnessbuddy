// ===================================================
// FITBUDDY — PLAN FEEDBACK CONTROLLER
// ===================================================

let currentPlanId = null;

document.addEventListener("DOMContentLoaded", async () => {
  currentPlanId = getStoredPlanId();
  if (!currentPlanId) {
    showToast("Please generate a workout plan first.", "info");
  }
});

function insertFeedbackPrompt(text) {
  const textarea = document.getElementById("feedback-input");
  if (textarea) {
    textarea.value = text;
    textarea.focus();
  }
}

async function submitFeedback(event) {
  if (event) event.preventDefault();
  currentPlanId = getStoredPlanId();

  if (!currentPlanId) {
    showToast("No active workout plan found to update. Complete onboarding first.", "error");
    return;
  }

  const textarea = document.getElementById("feedback-input");
  const feedbackText = textarea ? textarea.value.trim() : "";

  if (!feedbackText || feedbackText.length < 3) {
    showToast("Please describe what you would like to change (e.g. 'Add more cardio').", "error");
    textarea && textarea.focus();
    return;
  }

  const btn = document.getElementById("btn-submit-feedback");
  const originalText = btn.innerHTML;
  const statusEl = document.getElementById("feedback-status");

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="width:18px;height:18px;border-width:2px;display:inline-block;margin:0;vertical-align:middle;"></span> Updating Your Plan with Gemini...`;

  if (statusEl) {
    statusEl.style.display = "block";
    statusEl.textContent = "Gemini AI is recalibrating your regimen based on your feedback...";
    statusEl.style.color = "var(--text-muted)";
  }

  try {
    const res = await apiRequest("/api/feedback", {
      method: "POST",
      body: JSON.stringify({
        plan_id: parseInt(currentPlanId, 10),
        feedback: feedbackText
      })
    });

    // Preserve original for comparison
    const previousPlan = localStorage.getItem("fitbuddy_plan");
    if (res.original_plan) {
      localStorage.setItem("fitbuddy_comparison_original", JSON.stringify(res.original_plan));
    } else if (previousPlan) {
      localStorage.setItem("fitbuddy_comparison_original", previousPlan);
    }

    // Store updated plan
    if (res.plan) {
      localStorage.setItem("fitbuddy_comparison_updated", JSON.stringify(res.plan));
      localStorage.setItem("fitbuddy_plan", JSON.stringify(res.plan));
    }
    localStorage.setItem("fitbuddy_comparison_feedback", feedbackText);

    // Sync to Cloud Firestore if enabled
    if (window.FitBuddyFirebase && window.FitBuddyFirebase.syncFeedbackToFirestore) {
      window.FitBuddyFirebase.syncFeedbackToFirestore(currentPlanId, feedbackText, res.plan);
    }

    showToast("Plan successfully calibrated! Opening comparison...", "success");
    if (statusEl) {
      statusEl.textContent = "Success! Your calibrated plan is ready. Opening comparison review...";
      statusEl.style.color = "var(--primary-dark)";
    }

    // Redirect to Plan Comparison / Revision View
    setTimeout(() => {
      window.location.href = "/comparison";
    }, 700);

  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = originalText;
    if (statusEl) {
      statusEl.textContent = `Error: ${err.message || "Failed to update plan."}`;
      statusEl.style.color = "#dc2626";
    }
    showToast(err.message || "Unable to update plan. Please try again.", "error");
  }
}
