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

    // Update stored plan with latest
    if (res.plan) {
      localStorage.setItem("fitbuddy_plan", JSON.stringify(res.plan));
    }

    // Sync to Cloud Firestore
    if (window.FitBuddyFirebase && window.FitBuddyFirebase.syncFeedbackToFirestore) {
      window.FitBuddyFirebase.syncFeedbackToFirestore(currentPlanId, feedbackText, res.plan);
    }

    showToast("Plan successfully updated with your feedback!", "success");
    if (statusEl) {
      statusEl.textContent = "Success! Your updated plan has been saved as a new version.";
      statusEl.style.color = "var(--primary-dark)";
    }

    // Redirect to dashboard to see updated plan
    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 800);

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
