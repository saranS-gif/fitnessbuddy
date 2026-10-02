// ===================================================
// FITBUDDY — ONBOARDING CONTROLLER (DEFAULT / UNSELECTED)
// ===================================================

const onboardingState = {
  name: "",
  age: 25,
  weight: 70,
  height: 170,
  goal: "",
  intensity: "",
  experience: "",
  location: "",
  equipment: "",
  preferred_days: []
};

function selectOption(category, value, element) {
  // If already selected, allow toggling off
  if (onboardingState[category] === value) {
    onboardingState[category] = "";
    element.classList.remove("selected");
    return;
  }
  onboardingState[category] = value;
  const parent = element.parentElement;
  parent.querySelectorAll(".option-card").forEach(el => el.classList.remove("selected"));
  element.classList.add("selected");
}

function toggleDay(element) {
  const day = element.dataset.day;
  const index = onboardingState.preferred_days.indexOf(day);
  if (index > -1) {
    onboardingState.preferred_days.splice(index, 1);
    element.classList.remove("selected");
  } else {
    onboardingState.preferred_days.push(day);
    element.classList.add("selected");
  }
}

function validateForm() {
  const nameInput = document.getElementById("name");
  const ageInput = document.getElementById("age");
  const weightInput = document.getElementById("weight");
  const heightInput = document.getElementById("height");

  const name = nameInput ? nameInput.value.trim() : "";
  const age = ageInput && ageInput.value ? parseInt(ageInput.value, 10) : 25;
  const weight = weightInput && weightInput.value ? parseFloat(weightInput.value) : 70.0;
  const height = heightInput && heightInput.value ? parseFloat(heightInput.value) : 170.0;

  if (!name || name.length < 2) {
    showToast("Please enter your name.", "error");
    nameInput && nameInput.focus();
    return false;
  }

  onboardingState.name = name;
  onboardingState.age = isNaN(age) ? 25 : age;
  onboardingState.weight = isNaN(weight) ? 70.0 : weight;
  onboardingState.height = isNaN(height) ? 170.0 : height;

  // Apply sensible defaults under the hood if user chose not to select anything
  if (!onboardingState.goal) {
    onboardingState.goal = "General Fitness";
  }
  if (!onboardingState.intensity) {
    onboardingState.intensity = "Medium";
  }
  if (!onboardingState.experience) {
    onboardingState.experience = "Beginner";
  }
  if (!onboardingState.location) {
    onboardingState.location = "Home";
  }
  if (!onboardingState.equipment) {
    onboardingState.equipment = "None";
  }
  if (!onboardingState.preferred_days || onboardingState.preferred_days.length === 0) {
    onboardingState.preferred_days = ["Monday", "Wednesday", "Friday"];
  }

  return true;
}

async function handleGenerate(event) {
  if (event) event.preventDefault();
  if (!validateForm()) return;

  const btn = document.getElementById("btn-generate");
  const originalText = btn.innerHTML;
  const statusEl = document.getElementById("generate-status");

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="width:18px;height:18px;border-width:2px;display:inline-block;margin:0;vertical-align:middle;"></span> Creating Your AI Plan...`;

  if (statusEl) {
    statusEl.style.display = "block";
    statusEl.style.color = "var(--primary-dark)";
    statusEl.textContent = "AI is creating your personalized plan...";
  }

  try {
    const res = await apiRequest("/api/generate", {
      method: "POST",
      body: JSON.stringify(onboardingState)
    });

    setStoredPlan(res.user_id, res.plan_id, res.plan);

    // Sync to Cloud Firestore
    if (window.FitBuddyFirebase && window.FitBuddyFirebase.syncPlanToFirestore) {
      window.FitBuddyFirebase.syncPlanToFirestore(res.user_id, res.plan_id, res.plan);
    }

    showToast("Your personalized fitness plan is ready!", "success");

    // Redirect to dashboard
    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 600);

  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = originalText;
    if (statusEl) {
      statusEl.style.display = "block";
      statusEl.textContent = `Error: ${err.message || "Unable to generate your plan."}`;
      statusEl.style.color = "#dc2626";
    }
    showToast(err.message || "Failed to generate plan. Please try again.", "error");
  }
}
