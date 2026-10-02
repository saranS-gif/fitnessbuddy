// ===================================================
// FITBUDDY — FIREBASE AUTH & FIRESTORE INTEGRATION
// ===================================================

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { 
  getAuth, 
  signInWithPopup, 
  GoogleAuthProvider, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { 
  getFirestore, 
  doc, 
  setDoc, 
  getDoc, 
  collection, 
  addDoc, 
  serverTimestamp 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Firebase configuration provided by user
const firebaseConfig = {
  apiKey: "AIzaSyC1iV-J58zgzC5s0WMw8FDm1lZunQumrww",
  authDomain: "fitnessbuddy-5f275.firebaseapp.com",
  projectId: "fitnessbuddy-5f275",
  storageBucket: "fitnessbuddy-5f275.firebasestorage.app",
  messagingSenderId: "499709744159",
  appId: "1:499709744159:web:5f637ae58fd25deefe312a",
  measurementId: "G-E5RT6W5LK2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const googleProvider = new GoogleAuthProvider();

// Current active auth state
let currentFirebaseUser = null;

// Listen to Auth State
onAuthStateChanged(auth, async (user) => {
  currentFirebaseUser = user;
  updateAuthUI(user);

  if (user) {
    localStorage.setItem("fitbuddy_firebase_uid", user.uid);
    localStorage.setItem("fitbuddy_firebase_email", user.email || "");
    // Store user document in Firestore
    try {
      await setDoc(doc(db, "users", user.uid), {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName || user.email.split("@")[0],
        photoURL: user.photoURL || null,
        lastLogin: serverTimestamp()
      }, { merge: true });
    } catch (e) {
      console.warn("Firestore user sync warning:", e);
    }
  } else {
    localStorage.removeItem("fitbuddy_firebase_uid");
    localStorage.removeItem("fitbuddy_firebase_email");
  }
});

// Update Navbar UI based on Auth State
function updateAuthUI(user) {
  const authContainer = document.getElementById("nav-auth-container");
  if (!authContainer) return;

  if (user) {
    const displayName = user.displayName || (user.email ? user.email.split("@")[0] : "User");
    const avatar = user.photoURL 
      ? `<img src="${user.photoURL}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;">`
      : `<span style="background:var(--primary);color:#fff;width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;">${displayName.charAt(0).toUpperCase()}</span>`;

    authContainer.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.6rem;">
        ${avatar}
        <span style="font-weight:600; font-size:0.9rem; color:#cbd5e1;">${displayName}</span>
        <button id="btn-logout" class="btn btn-secondary btn-sm" style="padding:0.35rem 0.75rem; font-size:0.8rem; background:rgba(255,255,255,0.1); border-color:rgba(255,255,255,0.2); color:#cbd5e1;">
          Sign Out
        </button>
      </div>
    `;

    document.getElementById("btn-logout")?.addEventListener("click", handleLogout);

    // Auto-fill user's name in onboarding if present
    const nameInput = document.getElementById("name");
    if (nameInput && !nameInput.value && user.displayName) {
      nameInput.value = user.displayName;
    }
  } else {
    authContainer.innerHTML = `
      <button id="btn-open-login" class="btn btn-outline" style="padding:0.4rem 1rem; font-size:0.85rem; border-color:rgba(255,255,255,0.3); color:#ffffff;">
        Sign In 🔒
      </button>
    `;
    document.getElementById("btn-open-login")?.addEventListener("click", () => {
      openAuthModal();
    });
  }
}

// Authentication Actions
export async function signInGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    closeAuthModal();
    if (window.showToast) window.showToast(`Welcome back, ${result.user.displayName || 'Athlete'}!`, "success");
    return result.user;
  } catch (error) {
    if (window.showToast) window.showToast(error.message || "Google sign-in failed", "error");
    throw error;
  }
}

export async function loginEmail(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    closeAuthModal();
    if (window.showToast) window.showToast("Signed in successfully!", "success");
    return userCredential.user;
  } catch (error) {
    if (window.showToast) window.showToast(error.message || "Login failed", "error");
    throw error;
  }
}

export async function registerEmail(email, password) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    closeAuthModal();
    if (window.showToast) window.showToast("Account created successfully!", "success");
    return userCredential.user;
  } catch (error) {
    if (window.showToast) window.showToast(error.message || "Registration failed", "error");
    throw error;
  }
}

export async function handleLogout() {
  try {
    await signOut(auth);
    if (window.showToast) window.showToast("Signed out successfully.", "info");
  } catch (error) {
    console.error("Sign out error:", error);
  }
}

// Cloud Firestore Syncing Functions
export async function syncPlanToFirestore(userId, planId, planData) {
  try {
    const uid = currentFirebaseUser ? currentFirebaseUser.uid : `guest_${userId}`;
    const planRef = doc(db, "plans", `plan_${planId}`);
    await setDoc(planRef, {
      userId: uid,
      localPlanId: planId,
      plan: planData,
      updatedAt: serverTimestamp(),
      createdAt: serverTimestamp()
    }, { merge: true });

    // Also add to user's personal plans subcollection
    const userPlanRef = doc(db, "users", uid, "plans", `plan_${planId}`);
    await setDoc(userPlanRef, {
      planId: planId,
      summary: planData.summary || "Workout Plan",
      weeklyGoal: planData.weekly_goal || "",
      updatedAt: serverTimestamp()
    }, { merge: true });

    console.log("[FitBuddy Firebase] Plan synced to Cloud Firestore");
  } catch (e) {
    console.warn("[FitBuddy Firebase] Firestore plan sync notice:", e.message);
  }
}

export async function syncFeedbackToFirestore(planId, feedbackText, updatedPlan) {
  try {
    const feedbackCol = collection(db, "feedback");
    await addDoc(feedbackCol, {
      planId: planId,
      feedbackText: feedbackText,
      userId: currentFirebaseUser ? currentFirebaseUser.uid : null,
      timestamp: serverTimestamp()
    });

    // Update the active plan in Firestore
    const planRef = doc(db, "plans", `plan_${planId}`);
    await setDoc(planRef, {
      activePlan: updatedPlan,
      latestFeedback: feedbackText,
      updatedAt: serverTimestamp()
    }, { merge: true });

    console.log("[FitBuddy Firebase] Feedback & revision synced to Cloud Firestore");
  } catch (e) {
    console.warn("[FitBuddy Firebase] Firestore feedback sync notice:", e.message);
  }
}

// Modal UI Control
export function openAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.style.display = "flex";
}

export function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.style.display = "none";
}

// Expose globals for non-module inline scripts
window.FitBuddyFirebase = {
  auth,
  db,
  signInGoogle,
  loginEmail,
  registerEmail,
  handleLogout,
  syncPlanToFirestore,
  syncFeedbackToFirestore,
  openAuthModal,
  closeAuthModal,
  getCurrentUser: () => currentFirebaseUser
};
