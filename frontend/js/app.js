const API_URL = "http://127.0.0.1:8000/predict";

const analyzeBtn = document.getElementById("analyzeBtn");
const audioInput = document.getElementById("audioInput");
const dropzone = document.getElementById("dropzone");
const fileName = document.getElementById("fileName");
const message = document.getElementById("message");
const apiStatus = document.getElementById("apiStatus");
const emptyState = document.getElementById("emptyState");
const result = document.getElementById("result");

const labelEl = document.getElementById("label");
const strengthEl = document.getElementById("strength");
const confidenceEl = document.getElementById("confidence");
const confidenceRing = document.getElementById("confidenceRing");
const languageEl = document.getElementById("language");
const durationEl = document.getElementById("duration");
const modelNameEl = document.getElementById("modelName");
const aiProbabilityEl = document.getElementById("aiProbability");
const humanProbabilityEl = document.getElementById("humanProbability");
const aiBar = document.getElementById("aiBar");
const humanBar = document.getElementById("humanBar");
const reasonEl = document.getElementById("reason");

function setText(element, value) {
  if (element) {
    element.innerText = value;
  }
}

function setMessage(text, type = "info") {
  setText(message, text);
  message.className = type === "error" ? "message error" : "message";
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  setText(analyzeBtn, isLoading ? "Analyzing..." : "Analyze Voice");
  setText(apiStatus, isLoading ? "Analyzing sample" : "Backend ready");
}

function percent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function verdictClass(label) {
  if (label === "AI") return "verdict ai";
  if (label === "HUMAN") return "verdict human";
  return "verdict uncertain";
}

function renderResult(data) {
  const aiProb = data.probabilities?.AI ?? data.probability_breakdown?.AI ?? 0;
  const humanProb = data.probabilities?.HUMAN ?? data.probability_breakdown?.HUMAN ?? 0;
  const confidence = Math.round(Number(data.confidence) || Math.max(aiProb, humanProb) * 100);
  const ringDegrees = Math.min(confidence, 100) * 3.6;

  emptyState.style.display = "none";
  result.classList.add("show");

  labelEl.className = verdictClass(data.label);
  setText(labelEl, data.label || "UNCERTAIN");
  setText(strengthEl, data.decision_reason || "Prediction completed");
  setText(confidenceEl, `${confidence}%`);
  confidenceRing.style.background = `conic-gradient(var(--blue) ${ringDegrees}deg, var(--surface-2) 0deg)`;

  setText(languageEl, data.language || "Unknown");
  setText(durationEl, `${data.audio_duration || 0}s`);
  setText(modelNameEl, data.model_name || "ML Classifier");

  setText(aiProbabilityEl, percent(aiProb));
  setText(humanProbabilityEl, percent(humanProb));
  aiBar.style.width = percent(aiProb);
  humanBar.style.width = percent(humanProb);

  setText(reasonEl, data.decision_reason || "No explanation returned.");
}

audioInput.addEventListener("change", () => {
  const file = audioInput.files[0];
  setText(fileName, file ? file.name : "");
  setMessage(file ? "Ready to analyze." : "");
});

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-active");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, () => {
    dropzone.classList.remove("is-active");
  });
});

analyzeBtn.addEventListener("click", async () => {
  const file = audioInput.files[0];

  if (!file) {
    setMessage("Please upload a WAV audio file first.", "error");
    return;
  }

  if (!file.name.toLowerCase().endsWith(".wav")) {
    setMessage("Only WAV files are supported by the backend.", "error");
    return;
  }

  setLoading(true);
  setMessage("Sending audio to the model...");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Backend error");
    }

    renderResult(data);
    setMessage("Analysis complete.");
  } catch (err) {
    setMessage(`Analysis failed: ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
});
