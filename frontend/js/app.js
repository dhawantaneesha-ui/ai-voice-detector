console.log("JS FILE CONNECTED");
console.log("JS loaded successfully");
const analyzeBtn = document.getElementById("analyzeBtn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");

const labelEl = document.getElementById("label");
const confidenceEl = document.getElementById("confidence");
const confidenceBar = document.getElementById("confidenceBar");
const reasonEl = document.getElementById("reason");
const languageEl = document.getElementById("language");
const audioInput = document.getElementById("audioInput");

function setText(element, value) {
  if (element) {
    element.innerText = value;
  }
}

analyzeBtn.addEventListener("click", async () => {
  const file = audioInput.files[0];
  console.log("Analyze clicked");
  if (!file) {
    alert("Please upload a WAV audio file first!");
    return;
  }

  loading.classList.remove("hidden");
  result.classList.add("hidden");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: formData
    });
console.log("Response status:", response.status);

    if (!response.ok) {
      throw new Error("Backend error");
    }

    const data = await response.json();
    console.log("Backend data:", data);


    // Label
    setText(labelEl, data.label);

    // Confidence (based on AI probability)
   // Confidence
const confidence =
  data.label === "AI"
    ? Math.round(data.probabilities.AI * 100)
    : Math.round(data.probabilities.HUMAN * 100);

   setText(confidenceEl, confidence + "%");
   if (confidenceBar) {
     confidenceBar.style.width = confidence + "%";
   }

   
    // Explainability
    setText(reasonEl, data.decision_reason);

    // Language
    setText(languageEl, data.language);

    result.classList.remove("hidden");

  } catch (err) {
    alert("Failed to analyze audio. Check console.");
    console.error(err);
  } finally {
    loading.classList.add("hidden");
  }
});
