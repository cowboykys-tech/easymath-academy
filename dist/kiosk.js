const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const tokenKey = "easymath-kiosk-token-v1";
let kioskToken = localStorage.getItem(tokenKey) || "";
let enteredCode = "";
let busy = false;
let resetTimer = 0;
let pendingCode = "";

function updateClock() {
  const now = new Date();
  $("#clockTime").textContent = new Intl.DateTimeFormat("ko-KR", { timeZone:"Asia/Seoul", hour:"2-digit", minute:"2-digit", hour12:false }).format(now);
  $("#clockDate").textContent = new Intl.DateTimeFormat("ko-KR", { timeZone:"Asia/Seoul", month:"long", day:"numeric", weekday:"long" }).format(now);
}

function showScreen(name) {
  $("#pairScreen").hidden = name !== "pair";
  $("#checkinScreen").hidden = name !== "checkin";
  $("#resultScreen").hidden = name !== "result";
  $("#choiceScreen").hidden = name !== "choice";
}

function renderPin() {
  $$("#pinDisplay i").forEach((dot, index) => dot.classList.toggle("filled", index < enteredCode.length));
  $("#checkinButton").disabled = enteredCode.length !== 4 || busy;
}

function resetInput() {
  enteredCode = "";
  busy = false;
  $("#checkinHelp").textContent = "번호는 화면에 표시되거나 저장되지 않습니다.";
  $("#checkinHelp").className = "checkin-help";
  renderPin();
}

async function request(path, options = {}) {
  const headers = { "Content-Type":"application/json", ...(options.headers || {}) };
  if (kioskToken) headers.Authorization = `Bearer ${kioskToken}`;
  const response = await fetch(path, { ...options, headers, cache:"no-store" });
  const data = await response.json();
  if (!response.ok) {
    if (data.pairingRequired || response.status === 401) {
      localStorage.removeItem(tokenKey); kioskToken = ""; showScreen("pair");
    }
    throw new Error(data.error || "요청을 처리하지 못했습니다.");
  }
  return data;
}

async function checkPairing() {
  if (!kioskToken) { showScreen("pair"); return; }
  try {
    const data = await request("/api/kiosk/status");
    $("#deviceLabel").textContent = data.device?.name || "등원 기기";
    showScreen("checkin"); resetInput();
  } catch { showScreen("pair"); }
}

async function pairDevice(event) {
  event.preventDefault();
  const error = $("#pairError"); error.textContent = "";
  const submit = event.currentTarget.querySelector("button"); submit.disabled = true;
  try {
    const data = await request("/api/kiosk/pair", {
      method:"POST", body:JSON.stringify({ deviceName:$("#deviceName").value.trim(), code:$("#pairingCode").value })
    });
    kioskToken = data.token; localStorage.setItem(tokenKey, kioskToken);
    $("#deviceLabel").textContent = data.device.name;
    $("#pairingCode").value = "";
    showScreen("checkin"); resetInput();
  } catch (failure) { error.textContent = failure.message; }
  finally { submit.disabled = false; }
}

async function submitCheckin(studentId = "") {
  if (enteredCode.length !== 4 || busy) return;
  busy = true; renderPin();
  $("#checkinHelp").textContent = "등원 기록을 확인하고 있습니다…";
  try {
    const data = await request("/api/kiosk/checkin", { method:"POST", body:JSON.stringify({ code:enteredCode, studentId }) });
    if (data.selectionRequired) {
      pendingCode = enteredCode;
      $("#candidateList").innerHTML = data.candidates.map(item => `<button type="button" data-student-id="${String(item.studentId).replace(/[&<>\"']/g, "")}">${String(item.studentName).replace(/[&<>\"']/g, "")}</button>`).join("");
      $$("[data-student-id]").forEach(button => button.addEventListener("click", () => { enteredCode = pendingCode; busy = false; submitCheckin(button.dataset.studentId); }));
      busy = false; showScreen("choice");
      return;
    }
    $("#resultTitle").textContent = data.duplicate ? "이미 등원 확인되었습니다" : `${data.studentName} 학생, 반가워요!`;
    $("#resultMessage").textContent = data.duplicate ? data.notice : "등원 기록이 안전하게 저장되었습니다.\n학부모 알림도 확인하고 있습니다.";
    showScreen("result");
    clearTimeout(resetTimer); resetTimer = setTimeout(returnToCheckin, 4500);
  } catch (failure) {
    busy = false; enteredCode = ""; renderPin();
    $("#checkinHelp").textContent = failure.message;
    $("#checkinHelp").className = "checkin-help error";
  }
}

function returnToCheckin() { clearTimeout(resetTimer); showScreen("checkin"); resetInput(); }

$("#keypad").addEventListener("click", event => {
  const button = event.target.closest("button"); if (!button || busy) return;
  if (button.dataset.key && enteredCode.length < 4) enteredCode += button.dataset.key;
  if (button.dataset.action === "backspace") enteredCode = enteredCode.slice(0,-1);
  if (button.dataset.action === "clear") enteredCode = "";
  $("#checkinHelp").textContent = "번호는 화면에 표시되거나 저장되지 않습니다.";
  $("#checkinHelp").className = "checkin-help";
  renderPin();
});
document.addEventListener("keydown", event => {
  if ($("#checkinScreen").hidden || busy) return;
  if (/^[0-9]$/.test(event.key) && enteredCode.length < 4) enteredCode += event.key;
  if (event.key === "Backspace") enteredCode = enteredCode.slice(0,-1);
  if (event.key === "Enter") submitCheckin();
  renderPin();
});
$("#pairForm").addEventListener("submit", pairDevice);
$("#pairingCode").addEventListener("input", event => { event.currentTarget.value = event.currentTarget.value.replace(/\D/g, "").slice(0,6); });
$("#checkinButton").addEventListener("click", () => submitCheckin());
$("#resultReset").addEventListener("click", returnToCheckin);
$("#choiceCancel").addEventListener("click", returnToCheckin);
$("#resetPairing").addEventListener("click", () => {
  if (!confirm("이 기기의 연결 정보를 지울까요? 다시 연결하려면 원장 화면에서 새 코드를 받아야 합니다.")) return;
  localStorage.removeItem(tokenKey); kioskToken = ""; $("#deviceLabel").textContent = "연결되지 않음"; showScreen("pair");
});
updateClock(); setInterval(updateClock, 1000); checkPairing();
