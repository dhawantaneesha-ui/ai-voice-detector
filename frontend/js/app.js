const API_URL =
  ["8080", "8090", "8091", "8092"].includes(window.location.port)
    ? "http://127.0.0.1:8000"
    : "";
const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const recordingStatus =
  document.getElementById("recordingStatus");
let recordedAudioFile = null;
let audioContext = null;
let mediaStream = null;
let processor = null;
let recordedChunks = [];
let recordingSampleRate = 44100;
let currentPaymentId = null;
let currentPaymentProvider = null;
let currentPaymentWarning = null;

let transactionScenario = {
  amount: 50000,
  known_device: true,
  known_beneficiary: true,
  transactions_last_10m: 1
};

const demoScenarios = {
  safe: {
    amount: 50000,
    known_device: true,
    known_beneficiary: true,
    transactions_last_10m: 1
  },

  suspicious: {
    amount: 50000,
    known_device: false,
    known_beneficiary: false,
    transactions_last_10m: 6
  },

  attack: {
    amount: 50000,
    known_device: false,
    known_beneficiary: false,
    transactions_last_10m: 10
  }
};


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
const confidenceRing =
  document.getElementById("confidenceRing");

const modelNameEl =
  document.getElementById("modelName");

const riskLevelEl =
  document.getElementById("riskLevel");

const decisionActionEl =
  document.getElementById("decisionAction");

const aiProbabilityEl =
  document.getElementById("aiProbability");

const humanProbabilityEl =
  document.getElementById("humanProbability");

const aiBar =
  document.getElementById("aiBar");

const humanBar =
  document.getElementById("humanBar");

const reasonEl =
  document.getElementById("reason");

const paymentAmountEl =
  document.getElementById("paymentAmount");

const paymentIdEl =
  document.getElementById("paymentId");

const paymentStatusEl =
  document.getElementById("paymentStatus");

const paymentProviderEl =
  document.getElementById("paymentProvider");

const paymentWarningEl =
  document.getElementById("paymentWarning");

const paymentPreviewAmountEl =
  document.getElementById("paymentPreviewAmount");

const amountInput =
  document.getElementById("amountInput");


function setText(element, value) {
  if (element) {
    element.innerText = value;
  }
}

function mergeBuffers(chunks) {
  const length = chunks.reduce(
    (total, chunk) => total + chunk.length,
    0
  );

  const result = new Float32Array(length);

  let offset = 0;

  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }

  return result;
}


function encodeWav(samples, sampleRate) {
  const buffer = new ArrayBuffer(
    44 + samples.length * 2
  );

  const view = new DataView(buffer);


  function writeString(offset, value) {
    for (let i = 0; i < value.length; i++) {
      view.setUint8(
        offset + i,
        value.charCodeAt(i)
      );
    }
  }


  writeString(0, "RIFF");

  view.setUint32(
    4,
    36 + samples.length * 2,
    true
  );

  writeString(8, "WAVE");
  writeString(12, "fmt ");

  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);

  view.setUint32(
    24,
    sampleRate,
    true
  );

  view.setUint32(
    28,
    sampleRate * 2,
    true
  );

  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);

  writeString(36, "data");

  view.setUint32(
    40,
    samples.length * 2,
    true
  );


  let offset = 44;

  for (let i = 0; i < samples.length; i++) {
    const sample =
      Math.max(-1, Math.min(1, samples[i]));

    view.setInt16(
      offset,
      sample < 0
        ? sample * 0x8000
        : sample * 0x7fff,
      true
    );

    offset += 2;
  }


  return new Blob(
    [view],
    { type: "audio/wav" }
  );
}
async function startRecording() {
  try {
    mediaStream =
      await navigator.mediaDevices.getUserMedia({
        audio: true
      });

    audioContext =
      new AudioContext();

    recordingSampleRate =
      audioContext.sampleRate;

    const source =
      audioContext.createMediaStreamSource(
        mediaStream
      );

    processor =
      audioContext.createScriptProcessor(
        4096,
        1,
        1
      );

    recordedChunks = [];

    processor.onaudioprocess =
      (event) => {
        const input =
          event.inputBuffer.getChannelData(0);

        recordedChunks.push(
          new Float32Array(input)
        );
      };

    source.connect(processor);

    processor.connect(
      audioContext.destination
    );


    recordBtn.disabled = true;
    stopBtn.disabled = false;

    recordingStatus.innerText =
      "🔴 Recording... Speak now.";

    setMessage(
      'Say: "I authorize this payment."'
    );

  } catch (error) {
    console.error(error);

    setMessage(
      "Microphone permission is required.",
      "error"
    );
  }
}

async function stopRecording() {
  if (!mediaStream) {
    return;
  }

  processor.disconnect();
  audioContext.close();

  mediaStream
    .getTracks()
    .forEach(track => track.stop());

  const samples =
    mergeBuffers(recordedChunks);

  const wavBlob =
    encodeWav(
      samples,
      recordingSampleRate
    );
    console.log(
  "LIVE RECORDING:",
  wavBlob.size,
  "bytes",
  recordingSampleRate,
  "Hz"
);

  const file =
    new File(
      [wavBlob],
      "voice_authorization.wav",
      {
        type: "audio/wav"
      }
    );
    recordedAudioFile = file;
    console.log(
  "VERIFYING FILE:",
  file.name,
  file.size,
  file.type
);


  recordBtn.disabled = false;

  stopBtn.disabled = true;

  recordingStatus.innerText =
    "Voice captured. Verifying...";


  await verifyRealPayment(file);
}

async function verifyRealPayment(file) {
  setLoading(true);

  try {
    const payment =
      await createPayment();

    currentPaymentId =
      payment.payment.payment_id;


    setMessage(
      "Payment created. Analyzing voice with AASIST-L..."
    );


    const result =
      await verifyPayment(file);


    renderResult(result);


    recordingStatus.innerText =
      "Verification complete.";

  } catch (error) {
    console.error(error);

    setMessage(
      `Verification failed: ${error.message}`,
      "error"
    );

    recordingStatus.innerText =
      "Verification failed.";

  } finally {
    setLoading(false);
  }
}
function setMessage(text, type = "info") {
  setText(message, text);

  if (message) {
    message.className =
      type === "error"
        ? "message error"
        : "message";
  }
}


function setLoading(isLoading) {
  if (analyzeBtn) {
    analyzeBtn.disabled = isLoading;

    setText(
      analyzeBtn,
      isLoading
        ? "Analyzing..."
        : "Analyze Voice"
    );
  }

  setText(
    apiStatus,
    isLoading
      ? "Running VoxGuard..."
      : "Backend ready"
  );
}


function percent(value) {
  return `${Math.round(
    (Number(value) || 0) * 100
  )}%`;
}

function formatInr(value) {
  return Number(value || 0).toLocaleString("en-IN");
}


function currentAmount() {
  const parsed = Number(amountInput?.value);

  if (Number.isFinite(parsed) && parsed > 0) {
    return parsed;
  }

  return transactionScenario.amount;
}


function updatePaymentPreview() {
  transactionScenario = {
    ...transactionScenario,
    amount: currentAmount()
  };

  setText(
    paymentPreviewAmountEl,
    formatInr(transactionScenario.amount)
  );

  setText(
    paymentAmountEl,
    formatInr(transactionScenario.amount)
  );
}


function verdictClass(label) {
  if (label === "AI") {
    return "verdict ai";
  }

  if (label === "HUMAN") {
    return "verdict human";
  }

  return "verdict uncertain";
}

function actionClass(action) {
  if (action === "ALLOW") {
    return "verdict allow";
  }

  if (action === "STEP_UP") {
    return "verdict step-up";
  }

  if (action === "REVIEW") {
    return "verdict review";
  }

  if (action === "DENY_VOICE_AUTH") {
    return "verdict deny";
  }

  return "verdict uncertain";
}


function displayVoiceSignal(verdict) {
  if (verdict === "AI") {
    return "Spoof Signal Detected";
  }

  if (verdict === "HUMAN") {
    return "Bona Fide Voice Signal";
  }

  return "Uncertain Voice Signal";
}


function displayPolicyAction(action) {
  const labels = {
    ALLOW: "Payment Authorized",
    STEP_UP: "Additional Verification Required",
    REVIEW: "Payment Under Review",
    DENY_VOICE_AUTH: "Voice Authorization Rejected"
  };

  return labels[action] || "Decision Pending";
}


function displayRiskFactor(code) {
  const labels = {
    voice_spoof_probability: "AASIST spoof signal",
    voice_uncertain: "Uncertain voice signal",
    high_value_transaction: "High-value payment",
    unknown_device: "New device",
    unknown_beneficiary: "New beneficiary",
    high_velocity: "High recent payment velocity"
  };

  return labels[code] || code;
}


async function createPayment() {
  const formData = new FormData();

  formData.append(
    "amount",
    currentAmount()
  );

  const response = await fetch(
    `${API_URL}/create-payment`,
    {
      method: "POST",
      body: formData
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Payment creation failed"
    );
  }

  currentPaymentId =
    data.payment.payment_id;
  currentPaymentProvider =
    data.payment.provider;
  currentPaymentWarning =
    data.payment.gateway_warning || "";

  return data;
}


async function verifyPayment(file) {
  const formData = new FormData();

  formData.append("file", file);

  formData.append(
    "payment_id",
    currentPaymentId
  );

  formData.append(
    "amount",
    currentAmount()
  );

  formData.append(
    "known_device",
    transactionScenario.known_device
  );

  formData.append(
    "known_beneficiary",
    transactionScenario.known_beneficiary
  );

  formData.append(
    "transactions_last_10m",
    transactionScenario.transactions_last_10m
  );

  const response = await fetch(
    `${API_URL}/verify-payment`,
    {
      method: "POST",
      body: formData
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Payment verification failed"
    );
  }

  return data;
}


function renderResult(data) {
  const voice = data.voice || {};
  const risk = data.risk || {};
  const decision = data.decision || {};
  const payment = data.payment || {};
  const transaction = data.transaction || {};

  const spoofProbability =
    Number(
      voice.spoof_probability || 0
    );

  const humanProbability =
    Math.max(
      0,
      1 - spoofProbability
    );

  const confidence =
    Math.round(
      Number(
        voice.confidence || 0
      )
    );

  const voiceSignal =
    displayVoiceSignal(
      voice.verdict
    );

  const policyAction =
    displayPolicyAction(
      decision.action
    );

  if (emptyState) {
    emptyState.style.display = "none";
  }

  if (result) {
    result.classList.add("show");
  }


  setText(
    labelEl,
    policyAction
  );

  if (labelEl) {
    labelEl.className =
      actionClass(
        decision.action
      );
  }


  setText(
    strengthEl,
    `Model margin: ${confidence}% (not calibrated)`
  );


  setText(
    confidenceEl,
    `${confidence}%`
  );


  if (confidenceRing) {
    confidenceRing.style.background =
      `conic-gradient(
        var(--blue)
        ${Math.min(confidence, 100) * 3.6}deg,
        var(--surface-2) 0deg
      )`;
  }


  setText(
    modelNameEl,
    voice.model_name || "AASIST-L"
  );

  setText(
    riskLevelEl,
    risk.risk_level || "UNKNOWN"
  );

  setText(
    decisionActionEl,
    policyAction
  );


  setText(
    aiProbabilityEl,
    percent(spoofProbability)
  );

  setText(
    humanProbabilityEl,
    percent(humanProbability)
  );


  if (aiBar) {
    aiBar.style.width =
      percent(spoofProbability);
  }

  if (humanBar) {
    humanBar.style.width =
      percent(humanProbability);
  }


  const amount =
    transaction.amount ??
    payment.amount ??
    transactionScenario.amount ??
    0;

  setText(
    paymentAmountEl,
    formatInr(amount)
  );

  setText(
    paymentIdEl,
    payment.payment_id ||
    currentPaymentId ||
    "Not created"
  );

  setText(
    paymentStatusEl,
    payment.payment_status ||
    payment.status ||
    "CREATED"
  );

  setText(
    paymentProviderEl,
    payment.provider ||
    currentPaymentProvider ||
    "VoxGuard"
  );

  setText(
    paymentWarningEl,
    payment.gateway_warning ||
    currentPaymentWarning ||
    ""
  );


  const factors =
    risk.risk_factors
      ?.map(
        factor =>
          `- ${displayRiskFactor(factor.code)}: +${factor.points}`
      )
      .join("\n") ||
    "No additional risk factors";


  setText(
    reasonEl,
`Decision:
${policyAction}

Voice Signal:
${voiceSignal} from AASIST-L

Model Margin:
${confidence}% (not calibrated probability)

Risk Level:
${risk.risk_level || "UNKNOWN"}

Risk Score:
${risk.risk_score ?? 0}/100

Risk Factors:

${factors}`
  );
}


async function runRealVerification() {

  const file =
    recordedAudioFile ||
    audioInput?.files?.[0];


  if (!file) {

    setMessage(
      "Record voice or upload WAV first.",
      "error"
    );

    return;
  }


  setLoading(true);

  setMessage(
    "Creating payment..."
  );


  try {

    await createPayment();


    setMessage(
      "Payment created. Running AASIST-L verification..."
    );


    const data =
      await verifyPayment(file);


    renderResult(data);


    setMessage(
      "Real payment verification complete."
    );


  } catch(error) {

    console.error(error);

    setMessage(
      `Analysis failed: ${error.message}`,
      "error"
    );

  } finally {

    setLoading(false);

  }
}


/* ---------------------------------------------
   Analyze button
--------------------------------------------- */

if (analyzeBtn) {
  analyzeBtn.addEventListener(
    "click",
    runRealVerification
  );
}

/* ---------------------------------------------
   REAL DEMO SCENARIOS
--------------------------------------------- */

document
  .querySelectorAll(".demo-btn")
  .forEach((button) => {

    button.addEventListener("click", async () => {

      const type =
        button.dataset.scenario;

      if (!demoScenarios[type]) {
        return;
      }

      transactionScenario =
        {
          ...demoScenarios[type],
          amount: currentAmount()
        };

      document
        .querySelectorAll(".demo-btn")
        .forEach((demoButton) => {
          demoButton.classList.toggle(
            "is-selected",
            demoButton === button
          );
        });

      updatePaymentPreview();

      setMessage(
        `${type.toUpperCase()} payment selected. Running real audio verification...`
      );

      await runRealVerification();

    });

  });

if (amountInput) {
  amountInput.addEventListener(
    "input",
    updatePaymentPreview
  );
}

updatePaymentPreview();


/* ---------------------------------------------
   VOICE RECORDING BUTTONS
--------------------------------------------- */

if (recordBtn) {

  recordBtn.addEventListener(
    "click",
    async () => {

      console.log(
        "START RECORDING CLICKED"
      );

      await startRecording();

    }
  );

}


if (stopBtn) {

  stopBtn.addEventListener(
    "click",
    async () => {

      console.log(
        "STOP RECORDING CLICKED"
      );

      await stopRecording();

    }
  );

}
