const seed = {
  classes: [
    { id: "c1", name: "초등 심화 A반", level: "초등 5·6학년", teacherId: "t1", students: ["s1", "s2", "s3", "s4"] },
    { id: "c2", name: "중등 개념 B반", level: "중등 1학년", teacherId: "t2", students: ["s5", "s6", "s7"] },
    { id: "c3", name: "중등 심화 C반", level: "중등 2학년", teacherId: "t1", students: ["s8"] }
  ],
  teachers: [
    { id: "t0", name: "원장님", subject: "교과수학·클리닉", classes: [] },
    { id: "t1", name: "이선생", subject: "수학 심화", classes: ["c1", "c3"] },
    { id: "t2", name: "최선생", subject: "수학 개념", classes: ["c2"] }
  ],
  students: [
    { id: "s1", name: "김민서", school: "가온초 6", classId: "c1", parent: "김민서 학부모", latest: "A-2", focus: "풀이 과정을 말로 설명하는 힘이 좋아지고 있습니다." },
    { id: "s2", name: "박도윤", school: "가온초 6", classId: "c1", parent: "박도윤 학부모", latest: "A-2", focus: "계산 실수를 줄이기 위해 검산 습관을 지도 중입니다." },
    { id: "s3", name: "윤서아", school: "나래초 5", classId: "c1", parent: "윤서아 학부모", latest: "A-2", focus: "규칙을 찾는 속도와 자신감이 좋아졌습니다." },
    { id: "s4", name: "정하준", school: "나래초 5", classId: "c1", parent: "정하준 학부모", latest: "A-2", focus: "문제 조건에 밑줄을 긋는 습관을 연습합니다." },
    { id: "s5", name: "한지우", school: "내포중 1", classId: "c2", parent: "한지우 학부모", latest: "B-3", focus: "방정식 활용 문제의 식 세우기가 안정되었습니다." },
    { id: "s6", name: "서준호", school: "내포중 1", classId: "c2", parent: "서준호 학부모", latest: "B-3", focus: "단위 확인과 답 문장 쓰기를 집중 지도합니다." },
    { id: "s7", name: "오유나", school: "홍성중 1", classId: "c2", parent: "오유나 학부모", latest: "B-3", focus: "개념 이해는 좋고 계산 속도를 보완하고 있습니다." },
    { id: "s8", name: "임채원", school: "내포중 2", classId: "c3", parent: "임채원 학부모", latest: "A-1", focus: "식의 계산 순서를 놓치지 않도록 반복 확인합니다." }
  ],
  records: [
    { id: "r1", date: "2026-10-15", classId: "c3", teacherId: "t1", studentId: "s8", code: "A-1", title: "문자와 식의 기본 원리", summary: "문자를 사용해 수량 사이의 관계를 식으로 나타내고 식의 값을 구했습니다.", notes: "식은 잘 세우지만 계산 순서를 놓치는 경우가 있어 다음 시간에 다시 확인합니다.", photos: ["수업판서.jpg", "풀이과정.jpg"], status: "주간 누적" },
    { id: "r2", date: "2026-10-14", classId: "c1", teacherId: "t1", studentId: "s1", code: "A-2", title: "규칙을 식으로 표현하기", summary: "표와 그림에서 반복되는 규칙을 찾고 간단한 식으로 표현했습니다.", notes: "규칙을 말로 설명하는 힘이 좋아졌고 기호로 바꾸는 연습을 이어갑니다.", photos: ["민서풀이.jpg"], status: "주간 누적" },
    { id: "r3", date: "2026-10-13", classId: "c2", teacherId: "t2", studentId: "s5", code: "B-3", title: "일차방정식 활용", summary: "문제 상황에서 미지수를 정하고 일차방정식을 세워 해결했습니다.", notes: "문제의 조건을 차분히 구분하면서 식 세우기가 안정되었습니다.", photos: ["문제풀이.jpg", "오답정리.jpg"], status: "주간 누적" },
    { id: "r4", date: "2026-10-10", classId: "c1", teacherId: "t1", studentId: "s2", code: "A-1", title: "수와 연산의 관계", summary: "연산 순서와 수 사이의 관계를 그림과 식으로 표현했습니다.", notes: "검산을 하면 스스로 계산 실수를 찾아 고칠 수 있었습니다.", photos: [], status: "발송 완료" }
  ],
  schedule: [
    { time: "14:30", classId: "c1", code: "A-2", topic: "규칙을 식으로 표현하기", recordStatus: "작성 완료", photos: 3 },
    { time: "16:10", classId: "c3", code: "A-1", topic: "문자와 식의 기본 원리", recordStatus: "사진 확인", photos: 0 },
    { time: "19:30", classId: "c2", code: "B-3", topic: "일차방정식 활용", recordStatus: "미작성", photos: 0 }
  ],
  weeklyFeedback: [
    { id: "w1", studentId: "s1", lessons: 2, photos: 3, summary: "이번 주에는 규칙을 식으로 표현하고 풀이 과정을 말로 설명하는 연습을 했습니다.", individual: "민서는 규칙을 찾는 과정은 안정적이며, 식으로 옮길 때 기호를 정확히 쓰는 연습을 이어가겠습니다.", next: "다음 주에는 다양한 규칙 문제로 식 세우기를 확실히 다집니다.", status: "발송 준비" },
    { id: "w2", studentId: "s2", lessons: 2, photos: 0, summary: "연산 순서와 규칙 찾기를 복습했습니다.", individual: "도윤이는 풀이 이해도는 좋지만 계산 후 검산이 더 필요합니다.", next: "검산 표시를 남기는 습관을 확인하겠습니다.", status: "내용 확인" },
    { id: "w3", studentId: "s5", lessons: 2, photos: 2, summary: "일차방정식 활용 문제에서 미지수를 정하고 식을 세웠습니다.", individual: "지우는 문제 조건을 구분하는 속도가 좋아졌습니다.", next: "단위와 답 문장까지 완성하는 연습을 이어갑니다.", status: "발송 준비" },
    { id: "w4", studentId: "s8", lessons: 2, photos: 2, summary: "문자와 식의 기본 원리를 복습하고 식의 값을 계산했습니다.", individual: "채원이는 식 세우기는 정확하며 계산 순서를 천천히 확인하면 좋겠습니다.", next: "연산 순서를 표시하는 습관을 점검합니다.", status: "발송 준비" },
    { id: "w5", studentId: "s3", lessons: 1, photos: 1, summary: "표에서 규칙을 찾는 연습을 진행했습니다.", individual: "서아는 규칙을 빠르게 발견하고 설명도 또렷했습니다.", next: "발견한 규칙을 식으로 표현해 봅니다.", status: "발송 완료" }
  ],
  weeklySchedule: [
    { id: "ws01", day: "mon", start: "15:00", end: "", timeLabel: "3시", className: "교과수학 원장 클리닉", subject: "교과수학 클리닉", teacherId: "t0", studentIds: [] },
    { id: "ws02", day: "mon", start: "16:00", end: "17:10", className: "7세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws03", day: "mon", start: "17:15", end: "18:25", className: "2학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws04", day: "mon", start: "18:00", end: "", timeLabel: "6시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },
    { id: "ws05", day: "mon", start: "19:00", end: "", timeLabel: "7시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },

    { id: "ws06", day: "tue", start: "14:10", end: "15:20", className: "1학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws07", day: "tue", start: "15:00", end: "", timeLabel: "3시", className: "교과수학 원장 클리닉", subject: "교과수학 클리닉", teacherId: "t0", studentIds: [] },
    { id: "ws08", day: "tue", start: "16:00", end: "16:50", className: "5세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws09", day: "tue", start: "17:10", end: "18:10", className: "6세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws10", day: "tue", start: "18:15", end: "19:25", className: "1학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws11", day: "tue", start: "19:00", end: "", timeLabel: "7시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },

    { id: "ws12", day: "wed", start: "15:00", end: "", timeLabel: "3시", className: "교과수학 원장 클리닉", subject: "교과수학 클리닉", teacherId: "t0", studentIds: [] },
    { id: "ws13", day: "wed", start: "15:50", end: "16:50", className: "RAT", subject: "RAT", teacherId: "", studentIds: [] },
    { id: "ws14", day: "wed", start: "17:00", end: "18:10", className: "1학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws15", day: "wed", start: "18:15", end: "19:15", className: "6세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws16", day: "wed", start: "19:00", end: "", timeLabel: "7시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },

    { id: "ws17", day: "thu", start: "14:10", end: "15:10", className: "RAT", subject: "RAT", teacherId: "", studentIds: [] },
    { id: "ws18", day: "thu", start: "15:00", end: "", timeLabel: "3시", className: "교과수학 원장 클리닉", subject: "교과수학 클리닉", teacherId: "t0", studentIds: [] },
    { id: "ws19", day: "thu", start: "15:50", end: "17:00", className: "2학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws20", day: "thu", start: "17:05", end: "18:20", className: "3학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws21", day: "thu", start: "18:30", end: "19:40", className: "7세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws22", day: "thu", start: "19:00", end: "", timeLabel: "7시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },

    { id: "ws23", day: "fri", start: "15:00", end: "", timeLabel: "3시", className: "주간 오답클리닉", subject: "오답 클리닉", teacherId: "t0", studentIds: [] },
    { id: "ws24", day: "fri", start: "16:05", end: "17:15", className: "1학년 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws25", day: "fri", start: "17:20", end: "18:30", className: "7세 사고력", subject: "사고력 수학", teacherId: "", studentIds: [] },
    { id: "ws26", day: "fri", start: "18:00", end: "", timeLabel: "6시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },
    { id: "ws27", day: "fri", start: "19:00", end: "", timeLabel: "7시", className: "한글", subject: "한글", teacherId: "", studentIds: [] },

    { id: "ws28", day: "sat", start: "09:20", end: "09:50", className: "한글", subject: "한글", teacherId: "", studentIds: [] },
    { id: "ws29", day: "sat", start: "10:00", end: "11:00", className: "7세 독서", subject: "독서", teacherId: "", studentIds: [] },
    { id: "ws30", day: "sat", start: "11:30", end: "12:00", className: "한글", subject: "한글", teacherId: "", studentIds: [] },
    { id: "ws31", day: "sat", start: "17:00", end: "19:00", className: "보강", subject: "보강 수업", teacherId: "", studentIds: [] }
  ],
  attendance: [
    { id: "a1", date: "2026-10-16", teacherId: "t1", in: "13:42", out: "", status: "근무 중" },
    { id: "a2", date: "2026-10-16", teacherId: "t2", in: "15:51", out: "", status: "근무 중" },
    { id: "a3", date: "2026-10-15", teacherId: "t1", in: "13:38", out: "21:47", status: "퇴근" },
    { id: "a4", date: "2026-10-15", teacherId: "t2", in: "15:55", out: "21:35", status: "퇴근" }
  ],
  studentAttendanceSummary: [],
  consultations: [
    { id: "q1", date: "2026-10-15", studentId: "s2", type: "전화", summary: "최근 계산 실수가 늘어난 부분을 공유하고 가정에서도 검산 표시를 확인하기로 했습니다.", followup: "2026-10-23" },
    { id: "q2", date: "2026-10-14", studentId: "s8", type: "방문", summary: "중간고사 이후 학습 계획과 보강 일정에 대해 상담했습니다.", followup: "2026-10-20" },
    { id: "q3", date: "2026-10-11", studentId: "s5", type: "카카오톡", summary: "숙제 분량과 오답 정리 방법을 안내했습니다.", followup: "" }
  ]
};

const stored = JSON.parse(localStorage.getItem("easymath-demo") || "null");
const state = {
  classes: stored?.classes || structuredClone(seed.classes),
  teachers: stored?.teachers || structuredClone(seed.teachers),
  students: stored?.students || structuredClone(seed.students),
  records: (stored?.records || structuredClone(seed.records)).map((item, index) => ({ ...item, studentId: item.studentId || seed.students[index % seed.students.length].id, photos: item.photos || [] })),
  schedule: structuredClone(seed.schedule).map((item, index) => ({ ...item, ...(stored?.schedule || [])[index], recordStatus: (stored?.schedule || [])[index]?.recordStatus || item.recordStatus, photos: (stored?.schedule || [])[index]?.photos ?? item.photos })),
  weeklyFeedback: stored?.weeklyFeedback || structuredClone(seed.weeklyFeedback),
  weeklySchedule: stored?.weeklySchedule || structuredClone(seed.weeklySchedule),
  attendance: stored?.attendance || structuredClone(seed.attendance),
  studentAttendanceSummary: stored?.studentAttendanceSummary || [],
  consultations: stored?.consultations || structuredClone(seed.consultations)
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const byId = (list, id) => list.find(item => item.id === id);
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
const className = id => byId(state.classes, id)?.name || "미지정 반";
const teacherName = id => byId(state.teachers, id)?.name || "미지정";
const studentName = id => byId(state.students, id)?.name || "미지정 학생";
const photoName = photo => typeof photo === "string" ? photo : photo?.originalName || "수업 사진";
const photoUrl = photo => typeof photo === "object" && String(photo?.url || "").startsWith("/media/") ? photo.url : "";
const localDate = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
const localTime = () => new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date());
const formatDate = date => date ? new Intl.DateTimeFormat("ko-KR", { month: "long", day: "numeric", weekday: "short" }).format(new Date(`${date}T12:00:00+09:00`)) : "없음";
const dayLabels = { mon: "월", tue: "화", wed: "수", thu: "목", fri: "금", sat: "토", sun: "일" };
const dayOrder = Object.keys(dayLabels);
const scheduleTone = subject => subject.includes("클리닉") ? "clinic" : subject.includes("사고력") ? "thinking" : subject === "RAT" ? "rat" : subject.includes("독서") ? "reading" : subject.includes("보강") ? "makeup" : "hangul";
const timetableCollapsedKey = "easymath-weekly-timetable-collapsed";
const timetableUxVersionKey = "easymath-weekly-timetable-ux-version";
const mobileMoreViews = new Set(["weekly", "students", "checkins", "attendance", "consultations"]);
let timetableFilterMode = "all";
let timetableFilterId = "";
let timetableTodayPositioned = false;
let scheduleSelectedStudentIds = new Set();
let dailyEvaluations = [];
let dailyFeedbackFilter = "all";
let feedbackAiConfigured = false;
let feedbackAiProvider = "template";
let messagingConnector = { configured: false, ready: false, kind: "none" };
let messagingLinks = [];
let checkinReportPeriod = "week";
let checkinReport = null;

let serverStateReady = false;
let saveQueue = Promise.resolve();

function replaceState(saved) {
  const fallback = structuredClone(seed);
  Object.keys(fallback).forEach(key => {
    state[key] = Array.isArray(saved?.[key]) ? saved[key] : fallback[key];
  });
}

async function postOwnerState(snapshot) {
  const response = await fetch("/api/owner/state", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state: snapshot })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "운영 데이터를 저장하지 못했습니다.");
  return data;
}

async function loadOwnerState() {
  const response = await fetch("/api/owner/state", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "운영 데이터를 불러오지 못했습니다.");
  if (data.initialized && data.state) {
    replaceState(data.state);
  } else {
    await postOwnerState(structuredClone(state));
  }
  localStorage.setItem("easymath-demo", JSON.stringify(state));
  serverStateReady = true;
}

function persist() {
  localStorage.setItem("easymath-demo", JSON.stringify(state));
  if (!serverStateReady) return Promise.resolve(false);
  const snapshot = structuredClone(state);
  saveQueue = saveQueue.catch(() => undefined).then(() => postOwnerState(snapshot));
  return saveQueue.then(() => true);
}
async function syncWeeklySchedule() {
  const lessons = state.weeklySchedule.map(item => ({
    id: item.id,
    day: item.day,
    start: item.start,
    end: item.end || "",
    timeLabel: item.timeLabel || "",
    className: item.className,
    subject: item.subject,
    teacherId: item.teacherId || "",
    teacherName: item.teacherId ? teacherName(item.teacherId) : "",
    students: (item.studentIds || []).map(id => byId(state.students, id)).filter(Boolean).map(student => ({ id: student.id, name: student.name, school: student.school }))
  }));
  try {
    const response = await fetch("/api/owner/schedule", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ lessons }) });
    if (!response.ok) throw new Error("시간표 동기화 실패");
    return true;
  } catch (error) { console.warn(error.message); return false; }
}
function toast(message) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.add("show");
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => element.classList.remove("show"), 2400);
}

async function setupOwnerSession() {
  const response = await fetch("/api/owner/session", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) return;
  const logoutButton = $("#ownerLogout");
  logoutButton.hidden = !data.configured;
  if (!data.configured) return;
  logoutButton.addEventListener("click", async () => {
    const logoutResponse = await fetch("/api/owner/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}"
    });
    const result = await logoutResponse.json();
    if (logoutResponse.ok) window.location.href = result.redirect || "/owner-login.html";
    else toast(result.error || "로그아웃하지 못했습니다.");
  });
}

async function loadFeedbackConfig() {
  try {
    const response = await fetch("/api/config", { cache: "no-store" });
    const config = await response.json();
    feedbackAiConfigured = Boolean(config.feedbackAiConfigured);
    feedbackAiProvider = config.feedbackAiProvider || "template";
    messagingConnector = config.messagingConnector || messagingConnector;
  } catch {
    feedbackAiConfigured = false;
    feedbackAiProvider = "template";
  }
  const guide = $("#feedbackAiGuide");
  const providerName = feedbackAiProvider === "codex" ? "Codex 로그인" : feedbackAiProvider === "openai" ? "OpenAI API" : "기본 문안";
  if (guide) guide.textContent = feedbackAiConfigured ? `${providerName} 사용 가능 · 원장 검토 필수` : "AI 연결 전에는 안전한 기본 초안 제공";
}

function switchView(name) {
  $$(".view").forEach(view => view.classList.toggle("active", view.id === `${name}View`));
  $$(".nav-item").forEach(button => button.classList.toggle("active", button.dataset.view === name));
  $("#navMoreToggle").classList.toggle("active", mobileMoreViews.has(name));
  setMobileMoreMenu(false);
  const titles = { dashboard: "오늘의 학원 흐름", people: "학생·직원 등록", compose: "오늘 수업 기록하기", daily: "오늘 학부모 피드백", weekly: "이번 주 학부모 피드백", students: "학생별 성장 기록", checkins: "학생 등원·리포트", attendance: "강사 출퇴근 현황", consultations: "학부모 상담 기록" };
  $("#pageTitle").textContent = titles[name] || "이지매쓰";
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (name === "weekly") renderWeekly();
  if (name === "daily") loadDailyEvaluations();
  if (name === "people") renderPeopleManagement();
  if (name === "students") renderStudents();
  if (name === "checkins") { loadKioskDevices(); loadCheckinReport(); }
  if (name === "attendance") renderAttendance();
  if (name === "consultations") renderConsultations();
  if (name === "compose") updateParentPreview();
}

function setMobileMoreMenu(open) {
  const menu = $("#mobileMoreMenu");
  const toggle = $("#navMoreToggle");
  menu.hidden = !open;
  toggle.setAttribute("aria-expanded", String(open));
  toggle.classList.toggle("is-open", open);
}

function populateSelects() {
  const classOptions = state.classes.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  const activeTeachers = state.teachers.filter(item => item.active !== false);
  const activeStudents = state.students.filter(item => item.status !== "퇴원");
  const teacherOptions = activeTeachers.map(item => `<option value="${item.id}">${escapeHtml(item.name)}${item.subject ? ` · ${escapeHtml(item.subject)}` : ""}</option>`).join("");
  const scheduleTeacherOptions = state.teachers.map(item => `<option value="${item.id}" ${item.active === false ? "disabled" : ""}>${escapeHtml(item.name)}${item.subject ? ` · ${escapeHtml(item.subject)}` : ""}${item.active === false ? " (퇴직)" : ""}</option>`).join("");
  const studentOptions = activeStudents.map(item => `<option value="${item.id}">${escapeHtml(item.name)} · ${escapeHtml(item.school || item.grade || "학교 미등록")}</option>`).join("");
  $("#recordClass").innerHTML = classOptions;
  $("#recordTeacher").innerHTML = teacherOptions;
  $("#consultStudent").innerHTML = studentOptions;
  $("#scheduleTeacher").innerHTML = `<option value="">선생님 미등록</option>${scheduleTeacherOptions}`;
  renderScheduleStudentChecks();
  updateTimetableFilterOptions();
  updateStudentSelect();
}

function updateStudentSelect() {
  const selectedClass = $("#recordClass").value;
  const students = state.students.filter(item => item.classId === selectedClass && item.status !== "퇴원");
  $("#recordStudent").innerHTML = students.map(item => `<option value="${item.id}">${escapeHtml(item.name)} · ${escapeHtml(item.school)}</option>`).join("");
  const teacherId = byId(state.classes, selectedClass)?.teacherId;
  if (teacherId) $("#recordTeacher").value = teacherId;
  updateParentPreview();
}

function renderWeeklyTimetable() {
  const visibleSchedule = state.weeklySchedule.filter(item => {
    if (timetableFilterMode === "teacher") return item.teacherId === timetableFilterId;
    if (timetableFilterMode === "student") return (item.studentIds || []).includes(timetableFilterId);
    return true;
  });
  const focused = timetableFilterMode !== "all";
  const visibleDays = focused ? dayOrder.filter(day => visibleSchedule.some(item => item.day === day)) : dayOrder;
  const timetable = $("#weeklyTimetable");
  timetable.classList.toggle("focused-timetable", focused);
  timetable.innerHTML = visibleDays.length ? visibleDays.map(day => {
    const sessions = visibleSchedule.filter(item => item.day === day).sort((a, b) => a.start.localeCompare(b.start));
    const isToday = day === currentDayKey();
    return `<section class="timetable-day ${isToday ? "is-today" : ""}" data-timetable-day="${day}"><div class="timetable-day-head"><strong>${dayLabels[day]}요일${isToday ? '<em>오늘</em>' : ""}</strong><span>${sessions.length}개 수업</span></div><div class="timetable-session-list">${sessions.map(item => `
      <button class="timetable-session ${scheduleTone(item.subject)}" data-schedule-id="${item.id}">
        <span class="session-time">${escapeHtml(item.timeLabel || `${item.start}${item.end ? `–${item.end}` : ""}`)}</span>
        <strong>${escapeHtml(item.className)}</strong>
        <small>${escapeHtml(item.subject)}</small>
        <span class="session-meta">${timetableFilterMode === "teacher" ? escapeHtml((item.studentIds || []).map(studentName).join(", ") || "학생 미등록") : `${item.teacherId ? escapeHtml(teacherName(item.teacherId)) : "선생님 미등록"} · ${item.studentIds.length ? `${item.studentIds.length}명` : "학생 미등록"}`}</span>
      </button>`).join("")}</div><button class="add-day-session" data-add-day="${day}">+ ${dayLabels[day]}요일 수업</button></section>`;
  }).join("") : `<div class="focused-timetable-empty"><strong>배정된 수업이 없습니다.</strong><span>위의 ‘수업 등록’ 버튼에서 담당 선생님과 학생을 선택해 주세요.</span><button class="secondary small" type="button" data-empty-schedule>+ 첫 수업 등록</button></div>`;
  $$('[data-schedule-id]').forEach(button => button.addEventListener("click", () => openScheduleDialog(button.dataset.scheduleId)));
  $$('[data-add-day]').forEach(button => button.addEventListener("click", () => openScheduleDialog(null, button.dataset.addDay)));
  $$('[data-empty-schedule]').forEach(button => button.addEventListener("click", () => openScheduleDialog()));
  const label = timetableFilterMode === "teacher" ? teacherName(timetableFilterId) : timetableFilterMode === "student" ? studentName(timetableFilterId) : "전체";
  $("#timetableFilterSummary").textContent = `${label} · ${visibleSchedule.length}개 수업`;
  renderTeacherScheduleOverview(visibleSchedule);
  if (!timetableTodayPositioned && timetableFilterMode === "all" && window.innerWidth <= 760) {
    timetableTodayPositioned = true;
    requestAnimationFrame(() => positionTimetableToday());
  }
}

function positionTimetableToday(showNotice = false) {
  const timetable = $("#weeklyTimetable");
  const today = $(`[data-timetable-day="${currentDayKey()}"]`, timetable);
  if (!today) {
    if (showNotice) toast("선택한 조회 기준에는 오늘 수업이 없습니다.");
    return;
  }
  timetable.scrollTo({ left: Math.max(0, today.offsetLeft - timetable.offsetLeft), behavior: showNotice ? "smooth" : "auto" });
}

function lessonDurationMinutes(item) {
  const [startHour, startMinute] = String(item.start || "").split(":").map(Number);
  const [endHour, endMinute] = String(item.end || "").split(":").map(Number);
  if (![startHour, startMinute, endHour, endMinute].every(Number.isFinite)) return 0;
  return Math.max(0, endHour * 60 + endMinute - startHour * 60 - startMinute);
}

function renderTeacherScheduleOverview(visibleSchedule = []) {
  const quick = $("#teacherScheduleQuick");
  const stats = $("#teacherScheduleStats");
  const teachers = state.teachers.filter(item => item.active !== false);
  const teacherMode = timetableFilterMode === "teacher";
  quick.hidden = !teacherMode;
  stats.hidden = !teacherMode;
  if (!teacherMode) return;
  quick.innerHTML = `<span class="teacher-quick-label">선생님 바로 선택</span><div class="teacher-quick-buttons">${teachers.map(item => {
    const lessonCount = state.weeklySchedule.filter(lesson => lesson.teacherId === item.id).length;
    return `<button type="button" class="teacher-quick-card ${item.id === timetableFilterId ? "active" : ""}" data-teacher-quick="${item.id}"><span class="teacher-quick-initial">${escapeHtml(item.name.slice(0, 1))}</span><span><strong>${escapeHtml(item.name)}</strong><small>${lessonCount}개 수업${item.subject ? ` · ${escapeHtml(item.subject)}` : ""}</small></span></button>`;
  }).join("")}</div>`;
  $$('[data-teacher-quick]', quick).forEach(button => button.addEventListener("click", () => {
    timetableFilterId = button.dataset.teacherQuick;
    $("#timetableFilterPerson").value = timetableFilterId;
    renderWeeklyTimetable();
  }));
  const teacher = byId(state.teachers, timetableFilterId);
  const workDays = new Set(visibleSchedule.map(item => item.day)).size;
  const studentCount = new Set(visibleSchedule.flatMap(item => item.studentIds || [])).size;
  const totalMinutes = visibleSchedule.reduce((sum, item) => sum + lessonDurationMinutes(item), 0);
  const hoursLabel = totalMinutes ? `${Math.floor(totalMinutes / 60)}시간${totalMinutes % 60 ? ` ${totalMinutes % 60}분` : ""}` : "시간 미등록";
  stats.innerHTML = `<div><span class="teacher-stat-name">${escapeHtml(teacher?.name || "선생님")}</span><small>${escapeHtml(teacher?.subject || "담당 과목 미등록")}</small></div><dl><div><dt>주간 수업</dt><dd>${visibleSchedule.length}개</dd></div><div><dt>수업 요일</dt><dd>${workDays}일</dd></div><div><dt>담당 학생</dt><dd>${studentCount}명</dd></div><div><dt>예정 시간</dt><dd>${hoursLabel}</dd></div></dl>`;
}

function updateTimetableFilterOptions() {
  const select = $("#timetableFilterPerson");
  if (!select) return;
  if (timetableFilterMode === "teacher") {
    select.innerHTML = state.teachers.filter(item => item.active !== false).map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  } else if (timetableFilterMode === "student") {
    select.innerHTML = state.students.filter(item => item.status !== "퇴원").map(item => `<option value="${item.id}">${escapeHtml(item.name)} · ${escapeHtml(item.school || item.grade || "학교 미등록")}</option>`).join("");
  } else {
    select.innerHTML = "";
  }
  select.hidden = timetableFilterMode !== "student";
  const values = [...select.options].map(option => option.value);
  if (!values.includes(timetableFilterId)) timetableFilterId = values[0] || "";
  select.value = timetableFilterId;
  renderTeacherScheduleOverview(state.weeklySchedule.filter(item => item.teacherId === timetableFilterId));
}

function renderScheduleStudentChecks(query = "") {
  const container = $("#scheduleStudentChecks");
  if (!container) return;
  const normalized = query.trim().toLowerCase();
  const students = state.students.filter(item => (item.status !== "퇴원" || scheduleSelectedStudentIds.has(item.id)) && (!normalized || `${item.name} ${item.school || ""} ${item.grade || ""}`.toLowerCase().includes(normalized)));
  container.innerHTML = students.length ? students.map(item => `<label><input type="checkbox" name="scheduleStudent" value="${item.id}" ${scheduleSelectedStudentIds.has(item.id) ? "checked" : ""} /><span>${escapeHtml(item.name)}<small>${escapeHtml([item.school, item.grade].filter(Boolean).join(" · ") || "학교·학년 미등록")}</small></span></label>`).join("") : `<div class="compact-empty">검색되는 학생이 없습니다.</div>`;
  $$('input[name="scheduleStudent"]', container).forEach(input => input.addEventListener("change", () => {
    if (input.checked) scheduleSelectedStudentIds.add(input.value); else scheduleSelectedStudentIds.delete(input.value);
  }));
}

function setWeeklyTimetableCollapsed(collapsed) {
  const timetable = $("#weeklyTimetable");
  const toggle = $("#weeklyTimetableToggle");
  timetable.hidden = collapsed;
  toggle.setAttribute("aria-expanded", String(!collapsed));
  toggle.innerHTML = collapsed
    ? '<span aria-hidden="true">▾</span> 시간표 펼치기'
    : '<span aria-hidden="true">▴</span> 시간표 접기';
  localStorage.setItem(timetableCollapsedKey, String(collapsed));
}

function renderDashboard() {
  const ready = state.weeklyFeedback.filter(item => item.status === "발송 준비");
  const followups = state.consultations.filter(item => item.followup && item.followup <= localDate());
  const missingRecords = state.schedule.filter(item => item.recordStatus !== "작성 완료").length;
  $("#readyCount").textContent = ready.length;
  $("#studentCount").textContent = state.students.length;
  $("#todayClassCount").textContent = state.schedule.length;
  $("#missingRecordCount").textContent = missingRecords;
  $("#followupCount").textContent = followups.length;
  $("#weeklyBadge").textContent = `${ready.length}명`;
  updateOperationsSummary();
  loadDashboardLiveCounts();

  $("#scheduleList").innerHTML = state.schedule.map(item => `
    <div class="schedule-item">
      <div class="time">${item.time}</div>
      <div><strong>${escapeHtml(className(item.classId))}</strong><span>${escapeHtml(item.topic)} · ${escapeHtml(teacherName(byId(state.classes, item.classId)?.teacherId))}</span></div>
      <button class="status-chip ${item.recordStatus === "미작성" ? "danger" : item.recordStatus === "사진 확인" ? "warn" : "done"}" data-compose-class="${item.classId}">${escapeHtml(item.recordStatus)}</button>
    </div>`).join("");

  $("#weeklyPreview").innerHTML = state.weeklyFeedback.filter(item => item.status !== "발송 완료").slice(0, 4).map(item => `
    <div class="pending-item">
      <span class="status-dot ${item.status === "발송 준비" ? "ready" : ""}"></span>
      <div><strong>${escapeHtml(studentName(item.studentId))} · 사진 ${item.photos}장</strong><span>${item.lessons}회 수업 · ${escapeHtml(item.status)}</span></div>
      <button class="text-button" data-open-weekly>확인</button>
    </div>`).join("");

  $("#consultationPreview").innerHTML = `
    <div class="record-row consultation-row header"><span>학생</span><span>상담일</span><span>상담 내용</span><span>후속 연락</span></div>
    ${followups.slice(0, 4).map(item => `<div class="record-row consultation-row"><strong>${escapeHtml(studentName(item.studentId))}</strong><span>${formatDate(item.date)}</span><span>${escapeHtml(item.summary)}</span><span>${formatDate(item.followup)}</span></div>`).join("")}`;

  $$('[data-compose-class]').forEach(button => button.addEventListener("click", () => {
    switchView("compose");
    $("#recordClass").value = button.dataset.composeClass;
    updateStudentSelect();
  }));
  $$('[data-open-weekly]').forEach(button => button.addEventListener("click", () => switchView("weekly")));
  renderWeeklyTimetable();
}

function updateOperationsSummary() {
  const countIds = ["missingRecordCount", "dailyFeedbackPendingCount", "attendanceApprovalCount", "followupCount", "readyCount"];
  const actionCount = countIds.reduce((sum, id) => sum + Number($(`#${id}`)?.textContent || 0), 0);
  $("#operationsSummary").textContent = actionCount
    ? `지금 처리할 업무 ${actionCount}건을 우선순위대로 모았습니다.`
    : "오늘 바로 처리할 업무가 없습니다.";
  $("#sidebarFocusTitle").textContent = actionCount ? `처리할 업무 ${actionCount}건` : "오늘 업무 확인 완료";
  $("#sidebarFocusDetail").textContent = actionCount
    ? "수업 기록·피드백·근태 승인·상담 후속을 확인해 주세요."
    : "새 요청이 생기면 이곳에 바로 표시됩니다.";
  $$(".operation-card").forEach(card => {
    const count = Number(card.querySelector("strong b")?.textContent || 0);
    card.classList.toggle("has-work", count > 0);
    card.classList.toggle("is-clear", count === 0);
  });
}

async function loadDashboardLiveCounts() {
  try {
    const [evaluationResponse, attendanceResponse] = await Promise.all([
      fetch(`/api/owner/evaluations?date=${encodeURIComponent(localDate())}`, { cache: "no-store" }),
      fetch("/api/owner/attendance", { cache: "no-store" })
    ]);
    if (evaluationResponse.ok) {
      const data = await evaluationResponse.json();
      $("#dailyFeedbackPendingCount").textContent = (data.evaluations || []).filter(item => item.message_status !== "sent").length;
    }
    if (attendanceResponse.ok) {
      const data = await attendanceResponse.json();
      const pending = [...(data.requests || []), ...(data.adjustments || [])].filter(item => item.status === "pending").length;
      $("#attendanceApprovalCount").textContent = pending;
    }
    updateOperationsSummary();
  } catch {
    updateOperationsSummary();
  }
}

function openScheduleDialog(id = null, presetDay = "mon") {
  const item = id ? byId(state.weeklySchedule, id) : null;
  const defaultTeacherId = !item && timetableFilterMode === "teacher" ? timetableFilterId : "";
  const defaultStudentIds = !item && timetableFilterMode === "student" && timetableFilterId ? [timetableFilterId] : [];
  $("#scheduleId").value = item?.id || "";
  $("#scheduleDialogTitle").textContent = item ? "수업 정보 수정" : "새 수업 등록";
  $("#scheduleDay").value = item?.day || presetDay;
  $("#scheduleClassName").value = item?.className || "";
  $("#scheduleStart").value = item?.start || "14:00";
  $("#scheduleEnd").value = item?.end || "";
  $("#scheduleSubject").value = item?.subject || "";
  $("#scheduleTeacher").value = item?.teacherId || defaultTeacherId;
  scheduleSelectedStudentIds = new Set(item?.studentIds || defaultStudentIds);
  $("#scheduleStudentSearch").value = "";
  renderScheduleStudentChecks();
  $("#deleteSchedule").hidden = !item;
  $("#scheduleDialog").showModal();
}

async function saveSchedule(event) {
  event.preventDefault();
  const id = $("#scheduleId").value;
  const saved = {
    id: id || `ws${Date.now()}`,
    day: $("#scheduleDay").value,
    start: $("#scheduleStart").value,
    end: $("#scheduleEnd").value,
    className: $("#scheduleClassName").value.trim(),
    subject: $("#scheduleSubject").value.trim(),
    teacherId: $("#scheduleTeacher").value,
    studentIds: [...scheduleSelectedStudentIds]
  };
  if (id) Object.assign(byId(state.weeklySchedule, id), saved); else state.weeklySchedule.push(saved);
  await persist(); renderWeeklyTimetable(); $("#scheduleDialog").close();
  const synced = await syncWeeklySchedule();
  toast(synced ? (id ? "수업 정보를 수정하고 선생님 앱에 반영했습니다." : "수업을 등록하고 선생님 앱에 반영했습니다.") : "원장님 화면에는 저장됐지만 선생님 앱 동기화에 실패했습니다.");
}

async function deleteSchedule() {
  const id = $("#scheduleId").value;
  if (!id || !window.confirm("이 수업을 시간표에서 삭제할까요?")) return;
  state.weeklySchedule = state.weeklySchedule.filter(item => item.id !== id);
  await persist(); renderWeeklyTimetable(); $("#scheduleDialog").close();
  const synced = await syncWeeklySchedule();
  toast(synced ? "시간표에서 삭제하고 선생님 앱에 반영했습니다." : "원장님 화면에서는 삭제됐지만 선생님 앱 동기화에 실패했습니다.");
}

function feedbackMessage(item) {
  const student = byId(state.students, item.studentId);
  return `안녕하세요, ${student?.name || "학생"} 학부모님.\n\n[이번 주 수업 내용]\n${item.summary}\n\n[개별 피드백]\n${item.individual}\n\n[다음 수업 계획]\n${item.next}\n\n이번 주 수업 사진 ${item.photos}장을 함께 보내드립니다.`;
}

const fieldValue = (selector, value = "") => { const field = $(selector); if (field) field.value = value ?? ""; };
const salaryText = item => {
  if (!item.salaryAmount) return "금액 미등록";
  const amount = new Intl.NumberFormat("ko-KR").format(Number(item.salaryAmount));
  return item.salaryType === "비율제" ? `${amount}%` : `${amount}원`;
};

function renderPeopleManagement() {
  const studentQuery = ($("#studentRegistrySearch")?.value || "").trim().toLowerCase();
  const teacherQuery = ($("#teacherRegistrySearch")?.value || "").trim().toLowerCase();
  const students = state.students.filter(item => !studentQuery || `${item.name} ${item.phone || ""} ${item.school || ""} ${item.grade || ""} ${item.parent || ""} ${item.guardianPhone || ""}`.toLowerCase().includes(studentQuery));
  const teachers = state.teachers.filter(item => !teacherQuery || `${item.name} ${item.phone || ""} ${item.subject || ""} ${item.university || ""} ${item.major || ""}`.toLowerCase().includes(teacherQuery));
  $("#registeredStudentCount").textContent = `${students.length}명`;
  $("#registeredTeacherCount").textContent = `${teachers.length}명`;
  $("#registeredStudents").innerHTML = students.length ? students.map(item => {
    const assignedLessonCount = state.weeklySchedule.filter(lesson => (lesson.studentIds || []).includes(item.id)).length;
    return `<article class="registry-card">
      <div class="registry-card-head"><span class="initial">${escapeHtml(item.name.slice(0, 1))}</span><span class="badge ${item.status === "재원" || !item.status ? "ready-badge" : ""}">${escapeHtml(item.status || "재원")}</span></div>
      <h3>${escapeHtml(item.name)}</h3>
      <p>${escapeHtml([item.school, item.grade].filter(Boolean).join(" · ") || "학교·학년 미등록")}</p>
      <dl><dt>학생 연락처</dt><dd>${escapeHtml(item.phone || "등록 필요")}</dd><dt>학부모</dt><dd>${escapeHtml(item.parent || "미등록")}</dd><dt>학부모 연락처</dt><dd>${escapeHtml(item.guardianPhone || "미등록")}</dd><dt>등원번호</dt><dd>${item.phone ? `학생번호 뒤 ${escapeHtml(item.phone.replace(/\D/g, "").slice(-4))}` : "전화번호 등록 필요"}</dd><dt>등록 수업</dt><dd>${assignedLessonCount}개</dd></dl>
      <button class="secondary small" data-edit-student="${item.id}">학생 정보 수정</button>
    </article>`;
  }).join("") : `<div class="compact-empty">등록된 학생이 없습니다.</div>`;
  $("#registeredTeachers").innerHTML = teachers.length ? teachers.map(item => `
    <article class="registry-card">
      <div class="registry-card-head"><span class="initial">${escapeHtml(item.name.slice(0, 1))}</span><span class="badge ${item.active !== false ? "ready-badge" : ""}">${item.active !== false ? "재직" : "퇴직"}</span></div>
      <h3>${escapeHtml(item.name)}</h3>
      <p>${escapeHtml(item.subject || "담당 과목 미등록")}</p>
      <dl><dt>연락처</dt><dd>${escapeHtml(item.phone || "미등록")}</dd><dt>학력·전공</dt><dd>${escapeHtml([item.university, item.major].filter(Boolean).join(" · ") || "미등록")}</dd><dt>재직 기간</dt><dd>${escapeHtml(item.hireDate || "미등록")} ${item.terminationDate ? `– ${escapeHtml(item.terminationDate)}` : "– 현재"}</dd><dt>급여</dt><dd>${escapeHtml(item.salaryType || "미등록")} · ${escapeHtml(salaryText(item))}</dd></dl>
      <div class="registry-card-actions"><button class="secondary small" data-teacher-history="${item.id}">누적 근무기록</button><button class="secondary small" data-edit-teacher="${item.id}">직원 정보 수정</button></div>
    </article>`).join("") : `<div class="compact-empty">등록된 선생님이 없습니다.</div>`;
  $$('[data-edit-student]').forEach(button => button.addEventListener("click", () => openStudentForm(button.dataset.editStudent)));
  $$('[data-edit-teacher]').forEach(button => button.addEventListener("click", () => openTeacherForm(button.dataset.editTeacher)));
  $$('[data-teacher-history]').forEach(button => button.addEventListener("click", () => openTeacherHistory(button.dataset.teacherHistory)));
}

function openStudentForm(id = "") {
  const item = id ? byId(state.students, id) : null;
  fieldValue("#studentId", item?.id || "");
  fieldValue("#studentName", item?.name || "");
  fieldValue("#studentPhone", item?.phone || "");
  fieldValue("#studentGrade", item?.grade || "");
  fieldValue("#studentSchool", item?.school || "");
  fieldValue("#studentParent", item?.parent || "");
  fieldValue("#studentGuardianPhone", item?.guardianPhone || "");
  fieldValue("#studentAddress", item?.address || "");
  fieldValue("#studentBirthDate", item?.birthDate || "");
  fieldValue("#studentEnrollmentDate", item?.enrollmentDate || localDate());
  fieldValue("#studentStatus", item?.status || "재원");
  fieldValue("#studentLatest", item?.latest || "");
  fieldValue("#studentFocus", item?.focus || "");
  fieldValue("#studentNotesProfile", item?.notes || "");
  $("#studentDialogTitle").textContent = item ? "학생 정보 수정" : "새 학생 등록";
  $("#studentDialog").showModal();
}

async function saveStudentProfile(event) {
  event.preventDefault();
  const id = $("#studentId").value || `student-${Date.now()}`;
  const existing = byId(state.students, id);
  const saved = {
    ...(existing || {}), id, name: $("#studentName").value.trim(), phone: $("#studentPhone").value.trim(),
    grade: $("#studentGrade").value.trim(), school: $("#studentSchool").value.trim(), parent: $("#studentParent").value.trim(),
    guardianPhone: $("#studentGuardianPhone").value.trim(), address: $("#studentAddress").value.trim(), birthDate: $("#studentBirthDate").value,
    enrollmentDate: $("#studentEnrollmentDate").value, status: $("#studentStatus").value, classId: existing?.classId || "",
    latest: $("#studentLatest").value.trim(), focus: $("#studentFocus").value.trim(), notes: $("#studentNotesProfile").value.trim()
  };
  if (saved.phone.replace(/\D/g, "").length < 10) { toast("등원번호로 사용할 학생 전화번호를 정확히 입력해 주세요."); return; }
  if (existing) Object.assign(existing, saved); else state.students.push(saved);
  await persist();
  populateSelects(); renderPeopleManagement(); renderStudents(); renderDashboard(); renderWeeklyTimetable();
  $("#studentDialog").close();
  toast(existing ? "학생 정보를 수정했습니다." : "학생을 등록하고 시간표 선택 목록에 추가했습니다.");
}

function openTeacherForm(id = "") {
  const item = id ? byId(state.teachers, id) : null;
  fieldValue("#teacherId", item?.id || "");
  fieldValue("#teacherNameInput", item?.name || "");
  fieldValue("#teacherPhone", item?.phone || "");
  fieldValue("#teacherEmail", item?.email || "");
  fieldValue("#teacherAddress", item?.address || "");
  fieldValue("#teacherSubject", item?.subject || "");
  fieldValue("#teacherUniversity", item?.university || "");
  fieldValue("#teacherMajor", item?.major || "");
  fieldValue("#teacherCareer", item?.career || "");
  fieldValue("#teacherCertifications", item?.certifications || "");
  fieldValue("#teacherHireDate", item?.hireDate || localDate());
  fieldValue("#teacherTerminationDate", item?.terminationDate || "");
  fieldValue("#teacherEmploymentType", item?.employmentType || "시간강사");
  fieldValue("#teacherSalaryType", item?.salaryType || "시급");
  fieldValue("#teacherSalaryAmount", item?.salaryAmount || "");
  fieldValue("#teacherStatus", item?.active === false ? "inactive" : "active");
  fieldValue("#teacherNotes", item?.notes || "");
  $("#teacherDialogTitle").textContent = item ? "직원 정보 수정" : "새 선생님 등록";
  $("#teacherDialog").showModal();
}

async function saveTeacherProfile(event) {
  event.preventDefault();
  const id = $("#teacherId").value || `teacher-${Date.now()}`;
  const existing = byId(state.teachers, id);
  const saved = {
    ...(existing || {}), id, name: $("#teacherNameInput").value.trim(), phone: $("#teacherPhone").value.trim(), email: $("#teacherEmail").value.trim(),
    address: $("#teacherAddress").value.trim(), subject: $("#teacherSubject").value.trim(), university: $("#teacherUniversity").value.trim(),
    major: $("#teacherMajor").value.trim(), career: $("#teacherCareer").value.trim(), certifications: $("#teacherCertifications").value.trim(),
    hireDate: $("#teacherHireDate").value, terminationDate: $("#teacherTerminationDate").value, employmentType: $("#teacherEmploymentType").value, salaryType: $("#teacherSalaryType").value,
    salaryAmount: Number($("#teacherSalaryAmount").value || 0), active: $("#teacherStatus").value === "active", notes: $("#teacherNotes").value.trim(),
    classes: existing?.classes || []
  };
  if (existing) Object.assign(existing, saved); else state.teachers.push(saved);
  await persist();
  populateSelects(); renderPeopleManagement(); renderAttendance(); renderDashboard(); renderWeeklyTimetable();
  $("#teacherDialog").close();
  toast(existing ? "직원 정보를 수정했습니다." : "선생님을 등록하고 시간표 선택 목록에 추가했습니다.");
}

async function openTeacherHistory(id) {
  const teacher = byId(state.teachers, id);
  if (!teacher) return;
  $("#dialogContent").innerHTML = `<div class="dialog-body"><span class="eyebrow">STAFF HISTORY</span><h2>${escapeHtml(teacher.name)} 누적 근무기록</h2><div class="compact-empty">근무 이력을 불러오는 중입니다.</div></div>`;
  $("#detailDialog").showModal();
  try {
    const response = await fetch(`/api/owner/teacher-history?teacherId=${encodeURIComponent(id)}`, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "누적 근무기록을 불러오지 못했습니다.");
    const approvedClockIns = data.requests.filter(item => item.status === "approved" && item.event_type === "clock_in");
    const approvedAdjustments = data.adjustments.filter(item => item.status === "approved");
    const pending = [...data.requests, ...data.adjustments].filter(item => item.status === "pending").length;
    const eventLabels = { hire: "입사", termination: "퇴사", rehire: "재입사", status_change: "재직상태 변경" };
    const workHistory = [
      ...data.requests.map(item => ({ ...item, type: item.event_type, time: attendanceTime(item.requested_at), detail: "" })),
      ...data.adjustments.map(item => ({ ...item, type: item.request_type, time: item.request_type === "absence" ? "근무 없음" : item.request_type === "early_leave" ? item.end_time : `${item.start_time}–${item.end_time}`, detail: item.reason || "" }))
    ].sort((a, b) => `${b.work_date}${b.requested_at}`.localeCompare(`${a.work_date}${a.requested_at}`));
    const employmentHistory = data.employmentEvents.length ? data.employmentEvents.map(item => `<div class="timeline-item"><span>${formatDate(item.effective_date)}</span><strong>${escapeHtml(eventLabels[item.event_type] || item.event_type)}</strong><p>${escapeHtml(item.note || "-")}</p></div>`).join("") : `<p>등록된 재직 변동 이력이 없습니다.</p>`;
    const workRows = workHistory.length ? workHistory.map(item => `<div class="history-table-row"><span>${escapeHtml(item.work_date)}</span><strong>${escapeHtml(attendanceEventLabel(item.type))}</strong><span>${escapeHtml(item.time || "-")}</span><span class="badge ${item.status === "approved" ? "ready-badge" : item.status === "pending" ? "coral" : ""}">${item.status === "approved" ? "승인" : item.status === "pending" ? "대기" : "반려"}</span><small>${escapeHtml(item.detail || "-")}</small></div>`).join("") : `<div class="compact-empty">아직 근무 기록이 없습니다.</div>`;
    $("#dialogContent").innerHTML = `<div class="dialog-body"><span class="eyebrow">STAFF HISTORY</span><h2>${escapeHtml(teacher.name)} 누적 근무기록</h2><p>${escapeHtml(teacher.subject || "담당 과목 미등록")} · ${escapeHtml(teacher.employmentType || "고용형태 미등록")}</p><div class="history-summary"><div><span>재직 기간</span><strong>${escapeHtml(teacher.hireDate || "미등록")}<small>${teacher.terminationDate ? `– ${escapeHtml(teacher.terminationDate)}` : "– 현재"}</small></strong></div><div><span>승인 출근</span><strong>${approvedClockIns.length}<small>일</small></strong></div><div><span>추가근무</span><strong>${approvedAdjustments.filter(item => item.request_type === "overtime").length}<small>건</small></strong></div><div><span>조퇴·결근</span><strong>${approvedAdjustments.filter(item => ["early_leave", "absence"].includes(item.request_type)).length}<small>건</small></strong></div><div><span>승인 대기</span><strong>${pending}<small>건</small></strong></div></div><h3>입사·퇴사 이력</h3>${employmentHistory}<h3>출퇴근·변경 전체 기록</h3><div class="history-table"><div class="history-table-row header"><span>근무일</span><strong>구분</strong><span>시간</span><span>상태</span><small>사유</small></div>${workRows}</div></div>`;
  } catch (error) {
    $("#dialogContent").innerHTML = `<div class="dialog-body"><h2>누적 근무기록</h2><div class="compact-empty">${escapeHtml(error.message)}</div></div>`;
  }
}

const dailyMetricNames = { attitude: "태도", concentration: "집중", understanding: "이해", progress: "진도", participation: "참여", homework: "과제" };
const dailyStatusNames = { pending: "초안 필요", draft: "검토·발송", sent: "발송 완료", updated_after_sent: "평가 수정됨" };

function renderMessagingLinks() {
  const container = $("#messagingLinks");
  if (!container) return;
  container.innerHTML = messagingLinks.length ? messagingLinks.map(item => `<div class="messaging-link-row"><span><strong>${escapeHtml(item.student_name || "등록 해제된 학생")}</strong><small>${escapeHtml(item.room_title)}</small></span><button class="secondary small" type="button" data-messaging-recent="${escapeHtml(item.student_id)}">최근 대화</button></div>`).join("") : `<div class="compact-empty">아직 연결한 학부모 카톡방이 없습니다.</div>`;
  $$('[data-messaging-recent]', container).forEach(button => button.addEventListener("click", () => showRecentMessages(button.dataset.messagingRecent)));
}

async function loadMessagingLinks() {
  const response = await fetch("/api/owner/messaging/links", { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "카톡 연결 정보를 불러오지 못했습니다.");
  messagingLinks = data.links || [];
  messagingConnector = data.connector || messagingConnector;
  const status = $("#messagingConnectorStatus");
  if (status) {
    status.textContent = !messagingConnector.configured ? "설치 장소의 카카오 송수신기를 아직 연결하지 않았습니다." : messagingConnector.ready ? "카카오 송수신기가 연결되어 있습니다." : "송수신기 설정은 있지만 현재 응답하지 않습니다.";
    status.className = `messaging-status ${messagingConnector.ready ? "ready" : "warn"}`;
  }
  renderMessagingLinks();
}

async function refreshMessagingRooms() {
  const select = $("#messagingRoom");
  select.innerHTML = `<option value="">채팅방을 불러오는 중...</option>`;
  try {
    const response = await fetch("/api/owner/messaging/rooms", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "채팅방을 불러오지 못했습니다.");
    select.innerHTML = `<option value="">학부모 카톡방 선택</option>${(data.rooms || []).map(room => `<option value="${escapeHtml(room.chatId)}">${escapeHtml(room.title)}</option>`).join("")}`;
    toast(`${(data.rooms || []).length}개 채팅방을 불러왔습니다.`);
  } catch (error) {
    select.innerHTML = `<option value="">연결기를 확인해 주세요</option>`;
    toast(error.message);
  }
}

async function openMessagingDialog(studentId = "") {
  $("#messagingStudent").innerHTML = `<option value="">학생 선택</option>${state.students.map(student => `<option value="${escapeHtml(student.id)}">${escapeHtml(student.name)} · ${escapeHtml(student.parent || "학부모 미등록")}</option>`).join("")}`;
  if (studentId) $("#messagingStudent").value = studentId;
  $("#messagingDialog").showModal();
  try {
    await loadMessagingLinks();
    if (messagingConnector.ready && $("#messagingRoom").options.length <= 1) await refreshMessagingRooms();
  } catch (error) { toast(error.message); }
}

async function saveMessagingLink(event) {
  event.preventDefault();
  const studentId = $("#messagingStudent").value;
  const chatId = $("#messagingRoom").value;
  if (!studentId || !chatId) { toast("학생과 학부모 카톡방을 모두 선택해 주세요."); return; }
  const response = await fetch("/api/owner/messaging/link", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ studentId, chatId })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "카톡방을 연결하지 못했습니다.");
  toast(data.notice || "학부모 카톡방을 연결했습니다.");
  await loadMessagingLinks();
  await loadDailyEvaluations();
}

async function showRecentMessages(studentId) {
  $("#dialogContent").innerHTML = `<div class="dialog-body"><h2>최근 카카오톡 대화</h2><div class="compact-empty">불러오는 중입니다.</div></div>`;
  $("#detailDialog").showModal();
  try {
    const response = await fetch(`/api/owner/messaging/messages?studentId=${encodeURIComponent(studentId)}`, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "최근 대화를 확인하지 못했습니다.");
    const messages = (data.messages || []).map(item => `<div class="message-history-row"><strong>${escapeHtml(item.author || "상대방")}</strong><p>${escapeHtml(item.text || "")}</p><small>${escapeHtml(item.timestamp || "")}</small></div>`).join("");
    $("#dialogContent").innerHTML = `<div class="dialog-body"><span class="eyebrow">KAKAO INBOX</span><h2>${escapeHtml(data.roomTitle)} 최근 대화</h2>${messages || `<div class="compact-empty">표시할 최근 메시지가 없습니다.</div>`}</div>`;
  } catch (error) {
    $("#dialogContent").innerHTML = `<div class="dialog-body"><h2>최근 카카오톡 대화</h2><div class="compact-empty">${escapeHtml(error.message)}</div></div>`;
  }
}

async function sendDailyKakao(item) {
  const textarea = $(`[data-daily-message="${CSS.escape(item.id)}"]`);
  const message = textarea.value.trim();
  if (!message) { toast("먼저 학부모 피드백 문안을 만들어 주세요."); return; }
  if (!item.messaging_linked) { await openMessagingDialog(item.student_id); return; }
  if (!messagingConnector.ready) { toast("설치 장소의 카카오 송수신기 연결 상태를 확인해 주세요."); return; }
  if (!window.confirm(`${item.student_name} 학생의 학부모 카톡방 '${item.messaging_room_title}'에 이 문안을 전송할까요?\n\n전송 후에는 자동으로 다시 보내지 않습니다.`)) return;
  const requestId = globalThis.crypto?.randomUUID?.() || `send-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const response = await fetch(`/api/owner/evaluations/${encodeURIComponent(item.id)}/kakao-send`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed: true, requestId, message })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "카톡을 전송하지 못했습니다.");
  toast(data.notice || "카톡 전송을 처리했습니다.");
  await loadDailyEvaluations();
}

async function loadDailyEvaluations() {
  const date = $("#dailyFeedbackDate").value || localDate();
  try {
    const response = await fetch(`/api/owner/evaluations?date=${encodeURIComponent(date)}`, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "학생 평가를 불러오지 못했습니다.");
    dailyEvaluations = data.evaluations || [];
    renderDailyFeedback();
  } catch (error) {
    dailyEvaluations = [];
    $("#dailyFeedbackCount").textContent = "불러오기 실패";
    $("#dailyFeedbackCards").innerHTML = `<div class="daily-empty">${escapeHtml(error.message)}</div>`;
  }
}

function renderDailyFeedback() {
  const visible = dailyEvaluations.filter(item => {
    if (dailyFeedbackFilter === "all") return true;
    if (dailyFeedbackFilter === "pending") return ["pending", "updated_after_sent"].includes(item.message_status);
    return item.message_status === dailyFeedbackFilter;
  });
  $("#dailyFeedbackCount").textContent = `평가 ${dailyEvaluations.length}건 · 발송 ${dailyEvaluations.filter(item => item.message_status === "sent").length}건`;
  $("#dailyFeedbackCards").innerHTML = visible.length ? visible.map(item => {
    const status = dailyStatusNames[item.message_status] || "초안 필요";
    const provider = item.message_provider === "codex" ? "Codex 생성 후 원장 검토" : item.message_provider === "openai" ? "OpenAI API 생성 후 원장 검토" : item.message_provider === "template" ? "기본 초안 · 원장 검토" : "초안 없음";
    const metricChips = Object.entries(dailyMetricNames).map(([key, name]) => `<span>${name} · ${escapeHtml(item.scores?.[key]?.label || "-")}</span>`).join("");
    const isSent = item.message_status === "sent";
    const room = item.messaging_linked ? `연결됨 · ${escapeHtml(item.messaging_room_title)}` : "학부모 카톡방 미연결";
    return `<article class="daily-feedback-card ${isSent ? "is-sent" : ""}" data-daily-card="${escapeHtml(item.id)}"><div class="daily-feedback-head"><div class="daily-feedback-person"><span class="avatar">${escapeHtml(item.student_name.slice(0, 1))}</span><div><h3>${escapeHtml(item.student_name)}</h3><p>${escapeHtml(item.class_name)} · ${escapeHtml(item.subject)} · ${escapeHtml(item.teacher_name)} 선생님</p></div></div><span class="badge ${item.message_status === "pending" || item.message_status === "updated_after_sent" ? "coral" : isSent ? "ready-badge" : ""}">${status}</span></div><div class="daily-feedback-metrics">${metricChips}</div><p class="teacher-observation"><strong>선생님 관찰</strong>${escapeHtml(item.note)}</p><label class="feedback-message-label"><span>학부모 전달 문안</span><small class="feedback-provider">${provider}</small></label><textarea class="daily-message" data-daily-message="${escapeHtml(item.id)}" placeholder="초안 만들기를 누르면 여기에 문안이 작성됩니다.">${escapeHtml(item.message_draft || "")}</textarea><div class="messaging-card-status ${item.messaging_linked ? "linked" : ""}"><span>${room}</span><button type="button" data-daily-room="${escapeHtml(item.id)}">${item.messaging_linked ? "연결 변경" : "카톡방 연결"}</button>${item.messaging_linked ? `<button type="button" data-daily-recent="${escapeHtml(item.id)}">최근 대화</button>` : ""}</div><div class="daily-feedback-actions"><button class="draft-button" type="button" data-daily-draft="${escapeHtml(item.id)}" ${isSent ? "disabled" : ""}>${item.message_draft ? "초안 다시 만들기" : "초안 만들기"}</button><button class="save-message-button" type="button" data-daily-save="${escapeHtml(item.id)}" ${isSent ? "disabled" : ""}>수정 문안 저장</button><button class="copy-message-button" type="button" data-daily-copy="${escapeHtml(item.id)}">카톡 문안 복사</button><button class="kakao-send-button" type="button" data-daily-kakao="${escapeHtml(item.id)}" ${isSent ? "disabled" : ""}>${isSent ? "카톡 발송 완료" : "확인 후 카톡 전송"}</button><button class="sent-message-button manual" type="button" data-daily-sent="${escapeHtml(item.id)}" ${isSent ? "disabled" : ""}>수동 발송 완료</button></div></article>`;
  }).join("") : `<div class="daily-empty">${dailyEvaluations.length ? "선택한 상태의 피드백이 없습니다." : "이 날짜에는 선생님이 저장한 학생 평가가 없습니다."}</div>`;

  $$('[data-daily-draft]').forEach(button => button.addEventListener("click", () => updateDailyEvaluation(button.dataset.dailyDraft, "draft")));
  $$('[data-daily-save]').forEach(button => button.addEventListener("click", () => {
    const message = $(`[data-daily-message="${CSS.escape(button.dataset.dailySave)}"]`).value.trim();
    updateDailyEvaluation(button.dataset.dailySave, "message", { message });
  }));
  $$('[data-daily-copy]').forEach(button => button.addEventListener("click", async () => {
    const message = $(`[data-daily-message="${CSS.escape(button.dataset.dailyCopy)}"]`).value.trim();
    if (!message) { toast("먼저 학부모 피드백 문안을 만들어 주세요."); return; }
    try { await navigator.clipboard.writeText(message); toast("카카오톡에 붙여넣을 문안을 복사했습니다."); }
    catch { toast("문안을 복사하지 못했습니다. 브라우저 권한을 확인해 주세요."); }
  }));
  $$('[data-daily-room]').forEach(button => button.addEventListener("click", () => {
    const item = dailyEvaluations.find(evaluation => evaluation.id === button.dataset.dailyRoom);
    if (item) openMessagingDialog(item.student_id);
  }));
  $$('[data-daily-recent]').forEach(button => button.addEventListener("click", () => {
    const item = dailyEvaluations.find(evaluation => evaluation.id === button.dataset.dailyRecent);
    if (item) showRecentMessages(item.student_id);
  }));
  $$('[data-daily-kakao]').forEach(button => button.addEventListener("click", async () => {
    const item = dailyEvaluations.find(evaluation => evaluation.id === button.dataset.dailyKakao);
    if (!item) return;
    try { await sendDailyKakao(item); } catch (error) { toast(error.message); }
  }));
  $$('[data-daily-sent]').forEach(button => button.addEventListener("click", async () => {
    const id = button.dataset.dailySent;
    const message = $(`[data-daily-message="${CSS.escape(id)}"]`).value.trim();
    if (!message) { toast("먼저 문안을 만들고 학부모에게 보내 주세요."); return; }
    try {
      await updateDailyEvaluation(id, "message", { message }, false);
      await updateDailyEvaluation(id, "sent");
    } catch (error) { toast(error.message); }
  }));
}

async function updateDailyEvaluation(id, action, payload = {}, refresh = true) {
  const response = await fetch(`/api/owner/evaluations/${encodeURIComponent(id)}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.error || "피드백을 처리하지 못했습니다.");
    if (refresh) toast(error.message);
    throw error;
  }
  if (refresh) {
    toast(data.notice || "피드백을 저장했습니다.");
    await loadDailyEvaluations();
  }
  return data;
}

let weeklyFilter = "all";
function renderWeekly() {
  const items = state.weeklyFeedback.filter(item => weeklyFilter === "all" || item.status === weeklyFilter);
  $("#weeklyCards").innerHTML = items.length ? items.map(item => {
    const student = byId(state.students, item.studentId);
    return `<article class="weekly-card">
      <div class="weekly-card-head"><div><span class="avatar small-avatar">${escapeHtml(student?.name?.slice(0, 1))}</span><div><h3>${escapeHtml(student?.name)}</h3><p>${escapeHtml(student?.school)} · ${escapeHtml(className(student?.classId))}</p></div></div><span class="badge ${item.status === "발송 준비" ? "ready-badge" : item.status === "내용 확인" ? "coral" : ""}">${escapeHtml(item.status)}</span></div>
      <div class="weekly-summary"><span>${item.lessons}회 수업</span><span>사진 ${item.photos}장</span></div>
      <h4>이번 주 수업</h4><p>${escapeHtml(item.summary)}</p>
      <h4>개별 피드백</h4><p>${escapeHtml(item.individual)}</p>
      <h4>다음 지도</h4><p>${escapeHtml(item.next)}</p>
      <div class="card-actions"><button class="secondary" data-copy-weekly="${item.id}">카톡 문안 복사</button><button class="primary small" data-sent-weekly="${item.id}" ${item.status === "발송 완료" ? "disabled" : ""}>${item.status === "발송 완료" ? "발송 완료" : "발송 완료 표시"}</button></div>
    </article>`;
  }).join("") : `<article class="panel empty-state"><strong>해당 상태의 피드백이 없습니다.</strong></article>`;

  $$('[data-copy-weekly]').forEach(button => button.addEventListener("click", async () => {
    const item = byId(state.weeklyFeedback, button.dataset.copyWeekly);
    try { await navigator.clipboard.writeText(feedbackMessage(item)); toast("카카오톡에 붙여넣을 문안을 복사했습니다."); }
    catch { toast("문안을 복사하지 못했습니다. 브라우저 권한을 확인해 주세요."); }
  }));
  $$('[data-sent-weekly]').forEach(button => button.addEventListener("click", async () => {
    const item = byId(state.weeklyFeedback, button.dataset.sentWeekly);
    if (!item || item.status === "발송 완료") return;
    item.status = "발송 완료";
    await persist(); renderWeekly(); renderDashboard(); toast(`${studentName(item.studentId)} 학생 피드백을 발송 완료로 표시했습니다.`);
  }));
}

const studentAttendanceNames = { present: "출석", late: "지각", absent: "결석", excused: "인정결석", makeup: "보강" };

function renderStudents(query = "") {
  const normalized = query.trim().toLowerCase();
  const students = state.students.filter(item => !normalized || `${item.name} ${item.school}`.toLowerCase().includes(normalized));
  $("#studentCards").innerHTML = students.map(item => {
    const records = state.records.filter(record => record.studentId === item.id);
    const consultations = state.consultations.filter(entry => entry.studentId === item.id);
    const weekly = state.weeklyFeedback.find(entry => entry.studentId === item.id);
    const attendance = (state.studentAttendanceSummary || []).find(entry => entry.studentId === item.id) || {};
    const attended = Number(attendance.present || 0) + Number(attendance.late || 0) + Number(attendance.makeup || 0);
    const attendanceRate = attendance.total ? `${Math.round(attended / attendance.total * 100)}%` : "기록 전";
    return `<article class="people-card student-card" data-student-detail="${item.id}"><div class="student-card-top"><div class="initial">${escapeHtml(item.name.slice(0, 1))}</div><span class="badge">${weekly ? escapeHtml(weekly.status) : "누적 중"}</span></div><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.school)} · ${escapeHtml(className(item.classId))}</p><div class="student-focus">${escapeHtml(item.focus)}</div><dl><dt>출석률</dt><dd>${attendanceRate}</dd><dt>결석·인정결석</dt><dd>${Number(attendance.absent || 0) + Number(attendance.excused || 0)}회</dd><dt>수업 기록</dt><dd>${records.length}건</dd><dt>상담 기록</dt><dd>${consultations.length}건</dd></dl><button class="text-button">누적 기록 보기 →</button></article>`;
  }).join("");
  $$('[data-student-detail]').forEach(card => card.addEventListener("click", () => openStudent(card.dataset.studentDetail)));
}

async function openStudent(id) {
  const student = byId(state.students, id);
  const records = state.records.filter(item => item.studentId === id).sort((a, b) => b.date.localeCompare(a.date));
  const consultations = state.consultations.filter(item => item.studentId === id).sort((a, b) => b.date.localeCompare(a.date));
  let evaluations = [];
  let attendance = { records: [], statusEvents: [], summary: { total: 0, present: 0, late: 0, absent: 0, excused: 0, makeup: 0 } };
  try {
    const [evaluationResponse, attendanceResponse] = await Promise.all([
      fetch(`/api/owner/evaluations?studentId=${encodeURIComponent(id)}`, { cache: "no-store" }),
      fetch(`/api/owner/student-attendance?studentId=${encodeURIComponent(id)}`, { cache: "no-store" })
    ]);
    const evaluationData = await evaluationResponse.json();
    const attendanceData = await attendanceResponse.json();
    if (evaluationResponse.ok) evaluations = evaluationData.evaluations || [];
    if (attendanceResponse.ok) attendance = attendanceData;
  } catch { evaluations = []; }
  const evaluationHistory = evaluations.length ? evaluations.map(item => `<div class="timeline-item"><span>${formatDate(item.lesson_date)} · ${escapeHtml(item.teacher_name)} 선생님</span><strong>${escapeHtml(item.class_name)} · ${escapeHtml(item.subject)}</strong><div class="daily-feedback-metrics">${Object.entries(dailyMetricNames).map(([key, name]) => `<span>${name} · ${escapeHtml(item.scores?.[key]?.label || "-")}</span>`).join("")}</div><p>${escapeHtml(item.note)}</p><small>${dailyStatusNames[item.message_status] || "초안 필요"}</small></div>`).join("") : "<p>아직 선생님 학생 평가가 없습니다.</p>";
  const attended = Number(attendance.summary.present || 0) + Number(attendance.summary.late || 0) + Number(attendance.summary.makeup || 0);
  const attendanceRate = attendance.summary.total ? `${Math.round(attended / attendance.summary.total * 100)}%` : "기록 전";
  const attendanceHistory = attendance.records.length ? attendance.records.map(item => `<div class="timeline-item attendance-history-item"><span>${formatDate(item.lesson_date)} · ${escapeHtml(item.teacher_name)} 선생님</span><strong>${escapeHtml(item.attendance_label)} · ${escapeHtml(item.class_name)} · ${escapeHtml(item.subject)}</strong>${item.note ? `<p>${escapeHtml(item.note)}</p>` : ""}</div>`).join("") : `<p>아직 출결 기록이 없습니다.</p>`;
  const statusHistory = attendance.statusEvents.length ? attendance.statusEvents.map(item => `<div class="timeline-item"><span>${formatDate(item.effective_date)}</span><strong>학생 상태 · ${escapeHtml(item.status)}</strong></div>`).join("") : "";
  $("#dialogContent").innerHTML = `<div class="dialog-body"><span class="eyebrow">STUDENT HISTORY</span><h2>${escapeHtml(student.name)} 누적 기록</h2><p>${escapeHtml(student.school)} · ${escapeHtml(student.grade || "학년 미등록")}</p><div class="history-summary student-history-summary"><div><span>출석률</span><strong>${attendanceRate}</strong></div><div><span>출석</span><strong>${attendance.summary.present || 0}<small>회</small></strong></div><div><span>지각</span><strong>${attendance.summary.late || 0}<small>회</small></strong></div><div><span>결석</span><strong>${attendance.summary.absent || 0}<small>회</small></strong></div><div><span>보강</span><strong>${attendance.summary.makeup || 0}<small>회</small></strong></div></div><div class="student-focus large"><strong>현재 진도·지도 포인트</strong>${escapeHtml(student.latest || "진도 미등록")} · ${escapeHtml(student.focus || "지도 포인트 미등록")}</div><h3>출결 기록</h3>${attendanceHistory}<h3>수업 태도·진도 평가</h3>${evaluationHistory}<h3>수업 기록·사진</h3>${records.length ? records.map(item => `<div class="timeline-item"><span>${formatDate(item.date)} · 진도 ${escapeHtml(item.code || "-")}</span><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.notes)}</p><small>사진 ${item.photos.length}장</small>${item.photos.length ? `<div class="timeline-photos">${item.photos.map(photo => photoUrl(photo) ? `<a href="${escapeHtml(photoUrl(photo))}" target="_blank" rel="noopener"><img src="${escapeHtml(photoUrl(photo))}" alt="${escapeHtml(photoName(photo))}" loading="lazy"><span>${escapeHtml(photoName(photo))}</span></a>` : `<span class="legacy-photo">${escapeHtml(photoName(photo))}</span>`).join("")}</div>` : ""}</div>`).join("") : "<p>아직 개별 수업 기록이 없습니다.</p>"}<h3>재원 상태 이력</h3>${statusHistory || "<p>상태 변동 기록이 없습니다.</p>"}<h3>학부모 상담</h3>${consultations.length ? consultations.map(item => `<div class="timeline-item"><span>${formatDate(item.date)} · ${escapeHtml(item.type)}</span><p>${escapeHtml(item.summary)}</p></div>`).join("") : "<p>상담 기록이 없습니다.</p>"}</div>`;
  $("#detailDialog").showModal();
}

const attendanceEventLabel = type => ({ clock_in: "출근", clock_out: "퇴근", early_leave: "조퇴", overtime: "추가근무", schedule_change: "근무시간 변경", absence: "결근" }[type] || type);
const attendanceTime = value => value ? new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(value)) : "--:--";
const currentDayKey = () => ({ Mon: "mon", Tue: "tue", Wed: "wed", Thu: "thu", Fri: "fri", Sat: "sat", Sun: "sun" }[new Intl.DateTimeFormat("en-US", { timeZone: "Asia/Seoul", weekday: "short" }).format(new Date())]);
let latestAttendanceData = null;

function inferredWorkPlan(teacherId, day) {
  const lessons = state.weeklySchedule.filter(item => item.teacherId === teacherId && item.day === day && item.start && item.end);
  if (!lessons.length) return null;
  const starts = lessons.map(item => item.start).filter(Boolean).sort();
  const ends = lessons.map(item => item.end).filter(Boolean).sort();
  return { day, start_time: starts[0], end_time: ends[ends.length - 1], break_minutes: 0, note: "수업표에서 제안" };
}

function renderWorkScheduleCards(data) {
  const activeTeachers = data.teachers.filter(item => item.active !== 0);
  $("#workScheduleTeacherCount").textContent = `${activeTeachers.length}명`;
  $("#workScheduleCards").innerHTML = activeTeachers.length ? activeTeachers.map(teacher => {
    const plans = data.workSchedules.filter(item => item.academy_teacher_id === teacher.academy_teacher_id);
    const plannedMinutes = plans.reduce((sum, item) => sum + Math.max(0, lessonDurationMinutes({ start: item.start_time, end: item.end_time }) - Number(item.break_minutes || 0)), 0);
    const hourLabel = plannedMinutes ? `${Math.floor(plannedMinutes / 60)}시간${plannedMinutes % 60 ? ` ${plannedMinutes % 60}분` : ""}` : "미등록";
    return `<article class="work-schedule-card"><div class="work-card-head"><span class="initial">${escapeHtml(teacher.name.slice(0, 1))}</span><div><h4>${escapeHtml(teacher.name)}</h4><p>${escapeHtml(teacher.subject || "담당 과목 미등록")}</p></div><span class="badge ${plans.length ? "ready-badge" : "coral"}">${plans.length ? `${plans.length}일` : "설정 필요"}</span></div><div class="work-plan-days">${plans.length ? plans.map(item => `<span><strong>${dayLabels[item.day]}요일</strong>${escapeHtml(item.start_time)}–${escapeHtml(item.end_time)}${item.break_minutes ? `<small>휴게 ${item.break_minutes}분</small>` : ""}</span>`).join("") : `<div class="compact-empty">등록된 근무시간이 없습니다.</div>`}</div><div class="work-card-footer"><span>주 ${hourLabel}</span><button class="secondary small" type="button" data-config-work="${teacher.academy_teacher_id}">근무시간 설정</button></div></article>`;
  }).join("") : `<div class="compact-empty">재직 중인 선생님이 없습니다.</div>`;
  $$('[data-config-work]').forEach(button => button.addEventListener("click", () => openWorkScheduleDialog(button.dataset.configWork)));
}

function renderWorkScheduleRows(academyTeacherId) {
  const saved = latestAttendanceData?.workSchedules || [];
  $("#workScheduleRows").innerHTML = dayOrder.map(day => {
    const plan = saved.find(item => item.academy_teacher_id === academyTeacherId && item.day === day);
    const suggested = plan || inferredWorkPlan(academyTeacherId, day);
    const enabled = Boolean(suggested);
    return `<div class="work-schedule-row" data-work-day="${day}"><label class="work-day-toggle"><input type="checkbox" data-work-enabled ${enabled ? "checked" : ""} /><span>${dayLabels[day]}요일</span></label><label><span>출근</span><input type="time" data-work-start value="${escapeHtml(suggested?.start_time || "14:00")}" ${enabled ? "" : "disabled"} /></label><label><span>퇴근</span><input type="time" data-work-end value="${escapeHtml(suggested?.end_time || "20:00")}" ${enabled ? "" : "disabled"} /></label><label><span>휴게(분)</span><input type="number" data-work-break min="0" max="480" step="10" value="${Number(suggested?.break_minutes || 0)}" ${enabled ? "" : "disabled"} /></label><label class="work-note"><span>메모</span><input data-work-note value="${escapeHtml(plan?.note || "")}" placeholder="선택" ${enabled ? "" : "disabled"} /></label></div>`;
  }).join("");
  $$('[data-work-enabled]', $("#workScheduleRows")).forEach(input => input.addEventListener("change", () => {
    const row = input.closest("[data-work-day]");
    $$('input:not([data-work-enabled])', row).forEach(field => { field.disabled = !input.checked; });
  }));
}

function openWorkScheduleDialog(academyTeacherId) {
  const teachers = (latestAttendanceData?.teachers || []).filter(item => item.active !== 0);
  $("#workScheduleTeacher").innerHTML = teachers.map(item => `<option value="${item.academy_teacher_id}">${escapeHtml(item.name)}</option>`).join("");
  $("#workScheduleTeacher").value = academyTeacherId || teachers[0]?.academy_teacher_id || "";
  renderWorkScheduleRows($("#workScheduleTeacher").value);
  $("#workScheduleDialog").showModal();
}

async function saveWorkSchedule(event) {
  event.preventDefault();
  const schedule = $$('[data-work-day]', $("#workScheduleRows")).filter(row => $('[data-work-enabled]', row).checked).map(row => ({
    day: row.dataset.workDay,
    startTime: $('[data-work-start]', row).value,
    endTime: $('[data-work-end]', row).value,
    breakMinutes: Number($('[data-work-break]', row).value || 0),
    note: $('[data-work-note]', row).value.trim()
  }));
  try {
    const response = await fetch("/api/owner/work-schedule", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ academyTeacherId: $("#workScheduleTeacher").value, schedule }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "근무시간을 저장하지 못했습니다.");
    $("#workScheduleDialog").close();
    toast("선생님 근무시간을 저장했습니다.");
    await renderAttendance();
  } catch (error) { toast(error.message); }
}

function openTeacherAbsenceDialog(academyTeacherId = "") {
  const teachers = (latestAttendanceData?.teachers || []).filter(item => item.active !== 0);
  if (!teachers.length) { toast("재직 중인 선생님을 먼저 등록해 주세요."); return; }
  $("#teacherAbsenceTeacher").innerHTML = teachers.map(item => `<option value="${item.academy_teacher_id}">${escapeHtml(item.name)}</option>`).join("");
  $("#teacherAbsenceTeacher").value = academyTeacherId || teachers[0].academy_teacher_id;
  $("#teacherAbsenceDate").max = localDate();
  $("#teacherAbsenceDate").value = localDate();
  $("#teacherAbsenceReason").value = "";
  $("#teacherAbsenceDialog").showModal();
}

async function saveTeacherAbsence(event) {
  event.preventDefault();
  try {
    const response = await fetch("/api/owner/teacher-absence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        academyTeacherId: $("#teacherAbsenceTeacher").value,
        workDate: $("#teacherAbsenceDate").value,
        reason: $("#teacherAbsenceReason").value.trim()
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "결근 기록을 저장하지 못했습니다.");
    $("#teacherAbsenceDialog").close();
    toast("원장님 확정 결근으로 저장했습니다.");
    await renderAttendance();
  } catch (error) { toast(error.message); }
}

async function renderAttendance() {
  try {
    const response = await fetch("/api/owner/attendance", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "출퇴근 기록을 불러오지 못했습니다.");
    latestAttendanceData = data;
    renderWorkScheduleCards(data);
    const pendingAttendance = data.requests.filter(item => item.status === "pending").map(item => ({ ...item, kind: "attendance", request_type: item.event_type }));
    const pendingAdjustments = data.adjustments.filter(item => item.status === "pending").map(item => ({ ...item, kind: "adjustment" }));
    const pending = [...pendingAttendance, ...pendingAdjustments].sort((a, b) => b.requested_at.localeCompare(a.requested_at));
    const approved = data.requests.filter(item => item.status === "approved");
    const approvedAdjustments = data.adjustments.filter(item => item.status === "approved");
    const today = localDate();
    $("#attendancePendingBadge").textContent = `${pending.length}건`;
    if ($("#attendanceApprovalCount")) {
      $("#attendanceApprovalCount").textContent = pending.length;
      updateOperationsSummary();
    }
    $("#attendancePending").innerHTML = pending.length ? pending.map(item => {
      const requestedTime = item.kind === "attendance" ? attendanceTime(item.requested_at) : item.request_type === "early_leave" ? `${item.end_time} 조퇴` : item.request_type === "absence" ? "근무 없음" : `${item.start_time}–${item.end_time}`;
      const detail = item.kind === "adjustment" ? ` · ${escapeHtml(item.reason)}` : "";
      return `<div class="approval-item"><div class="approval-person"><span class="initial">${escapeHtml(item.teacher_name.slice(0, 1))}</span><div><strong>${escapeHtml(item.teacher_name)} · ${attendanceEventLabel(item.request_type)} 요청</strong><small>${escapeHtml(item.work_date)} ${requestedTime}${detail}</small></div></div><div class="approval-actions"><button class="reject-button" data-review-kind="${item.kind}" data-review-id="${item.id}" data-review-action="reject">반려</button><button class="approve-button" data-review-kind="${item.kind}" data-review-id="${item.id}" data-review-action="approve">승인</button></div></div>`;
    }).join("") : `<div class="empty-state compact-empty">현재 승인 대기 중인 요청이 없습니다.</div>`;
    $("#attendanceCards").innerHTML = data.teachers.map(teacher => {
      const todays = approved.filter(item => item.teacher_id === teacher.id && item.work_date === today);
      const todaysAdjustments = approvedAdjustments.filter(item => item.teacher_id === teacher.id && item.work_date === today);
      const clockIn = todays.find(item => item.event_type === "clock_in");
      const clockOut = todays.find(item => item.event_type === "clock_out");
      const basePlan = data.workSchedules.find(item => item.academy_teacher_id === teacher.academy_teacher_id && item.day === currentDayKey());
      const scheduleChange = todaysAdjustments.find(item => item.request_type === "schedule_change");
      const todayPlan = scheduleChange ? { start_time: scheduleChange.start_time, end_time: scheduleChange.end_time, changed: true } : basePlan;
      const absence = todaysAdjustments.find(item => item.request_type === "absence");
      const status = absence ? "결근" : clockOut ? "퇴근 완료" : clockIn ? "근무 중" : "승인 기록 없음";
      return `<article class="attendance-card"><div><span class="initial">${escapeHtml(teacher.name.slice(0, 1))}</span><div><h3>${escapeHtml(teacher.name)}</h3><p>${todayPlan ? `오늘 ${todayPlan.changed ? "변경 " : "예정 "}${todayPlan.start_time}–${todayPlan.end_time}` : "오늘 근무시간 미등록"}</p></div></div><div class="attendance-times"><span>승인 출근<strong>${attendanceTime(clockIn?.requested_at)}</strong></span><span>승인 퇴근<strong>${attendanceTime(clockOut?.requested_at)}</strong></span></div><div class="attendance-actions"><span class="badge ${clockIn && !clockOut ? "ready-badge" : ""}">${status}</span>${todaysAdjustments.length ? `<small>${todaysAdjustments.map(item => attendanceEventLabel(item.request_type)).join(" · ")} 승인</small>` : ""}</div></article>`;
    }).join("");
    const approvedEntries = [
      ...approved.map(item => ({ ...item, request_type: item.event_type, display_time: attendanceTime(item.requested_at), reason: "", sort_at: item.requested_at })),
      ...approvedAdjustments.map(item => ({ ...item, display_time: item.request_type === "early_leave" ? item.end_time : item.request_type === "absence" ? "근무 없음" : `${item.start_time}–${item.end_time}`, sort_at: item.requested_at }))
    ].sort((a, b) => b.sort_at.localeCompare(a.sort_at));
    $("#attendanceTable").innerHTML = `<div class="record-row attendance-row header"><span>근무일</span><span>강사</span><span>구분</span><span>확정 시간</span><span>사유</span><span>승인 시각</span></div>${approvedEntries.map(item => `<div class="record-row attendance-row"><span>${escapeHtml(item.work_date)}</span><strong>${escapeHtml(item.teacher_name)}</strong><span>${attendanceEventLabel(item.request_type)}</span><span>${escapeHtml(item.display_time)}</span><span>${escapeHtml(item.reason || "-")}</span><span>${attendanceTime(item.reviewed_at)}</span></div>`).join("")}`;
    $$('[data-review-id]').forEach(button => button.addEventListener("click", () => reviewAttendance(button.dataset.reviewKind, button.dataset.reviewId, button.dataset.reviewAction)));
  } catch (error) {
    $("#attendancePending").innerHTML = `<div class="empty-state compact-empty">${escapeHtml(error.message)}</div>`;
    $("#workScheduleCards").innerHTML = "";
    $("#attendanceCards").innerHTML = "";
    $("#attendanceTable").innerHTML = "";
  }
}

async function reviewAttendance(kind, id, action) {
  try {
    const endpoint = kind === "adjustment" ? "adjustments" : "attendance";
    const response = await fetch(`/api/owner/${endpoint}/${id}/${action}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "승인 처리를 완료하지 못했습니다.");
    toast(action === "approve" ? "근무 요청을 승인해 확정 기록에 저장했습니다." : "근무 요청을 반려했습니다.");
    await renderAttendance();
  } catch (error) { toast(error.message); }
}

function renderConsultations() {
  $("#consultationList").innerHTML = [...state.consultations].sort((a, b) => b.date.localeCompare(a.date)).map(item => `<article class="consultation-card"><div class="consult-head"><div><span class="eyebrow">${escapeHtml(item.type)}</span><h3>${escapeHtml(studentName(item.studentId))} 학부모</h3></div><span>${formatDate(item.date)}</span></div><p>${escapeHtml(item.summary)}</p><div class="followup ${item.followup ? "due" : ""}">${item.followup ? `다시 연락: ${formatDate(item.followup)}` : "후속 연락 없음"}</div></article>`).join("");
}

function updateParentPreview() {
  if (!$("#parentPreview")) return;
  const student = byId(state.students, $("#recordStudent")?.value);
  const summary = $("#commonSummary")?.value.trim() || "오늘 수업 내용을 입력하면 여기에 표시됩니다.";
  const note = $("#studentNotes")?.value.trim() || "학생별 관찰 내용을 입력하면 여기에 표시됩니다.";
  const photoCount = $("#lessonPhotos")?.files?.length || 0;
  $("#parentPreview").innerHTML = `<div class="message-bubble"><strong>안녕하세요, ${escapeHtml(student?.name || "학생")} 학부모님.</strong><p><b>[오늘 수업]</b><br>${escapeHtml(summary)}</p><p><b>[개별 피드백]</b><br>${escapeHtml(note)}</p><span>사진 ${photoCount}장 첨부 예정</span></div><p class="preview-note">이 기록은 바로 전송되지 않고 주간 발송함에 누적됩니다.</p>`;
}

async function uploadRecordPhotos(files) {
  if (!files.length) return [];
  const formData = new FormData();
  files.forEach(file => formData.append("photos", file, file.name));
  const response = await fetch("/api/owner/photos", { method: "POST", body: formData });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "사진을 저장하지 못했습니다.");
  return data.photos || [];
}

async function saveRecord(status) {
  const selectedFiles = [...$("#lessonPhotos").files];
  const record = {
    id: `r${Date.now()}`, date: $("#recordDate").value, classId: $("#recordClass").value, teacherId: $("#recordTeacher").value,
    studentId: $("#recordStudent").value, code: $("#progressCode").value.trim().toUpperCase(), title: $("#lessonTitle").value.trim(),
    summary: $("#commonSummary").value.trim(), notes: $("#studentNotes").value.trim(), photos: [], status
  };
  if (!record.date || !record.code || !record.title || !record.studentId) { toast("수업일, 학생, 진도코드, 수업 주제를 입력하세요."); return false; }
  record.photos = await uploadRecordPhotos(selectedFiles);
  state.records.push(record);
  if (status === "주간 누적") {
    let weekly = state.weeklyFeedback.find(item => item.studentId === record.studentId && item.status !== "발송 완료");
    if (!weekly) {
      weekly = { id: `w${Date.now()}`, studentId: record.studentId, lessons: 0, photos: 0, summary: "", individual: "", next: "다음 수업에서 이어서 확인하겠습니다.", status: "내용 확인" };
      state.weeklyFeedback.push(weekly);
    }
    weekly.lessons += 1; weekly.photos += record.photos.length; weekly.summary = record.summary; weekly.individual = record.notes; weekly.status = record.photos.length ? "발송 준비" : "내용 확인";
    const schedule = state.schedule.find(item => item.classId === record.classId);
    if (schedule) { schedule.recordStatus = record.photos.length ? "작성 완료" : "사진 확인"; schedule.photos = record.photos.length; }
  }
  await persist(); renderDashboard();
  toast(status === "주간 누적" ? `${studentName(record.studentId)} 학생 주간 피드백에 누적했습니다.` : "수업 기록을 임시저장했습니다.");
  return true;
}

async function saveConsultation(event) {
  event.preventDefault();
  const form = event.currentTarget;
  state.consultations.push({ id: `q${Date.now()}`, date: localDate(), studentId: $("#consultStudent").value, type: $("#consultType").value, summary: $("#consultSummary").value.trim(), followup: $("#consultFollowup").value });
  await persist(); form.reset(); populateSelects(); renderConsultations(); renderDashboard(); toast("학부모 상담 내용을 학생 기록에 저장했습니다.");
}

const checkinNotificationLabels = {
  pending: "알림 대기", sending: "카톡 전송 중", sent: "카톡 전송", unknown: "전송 확인 필요",
  not_linked: "카톡방 미연결", not_configured: "송수신기 미연결"
};

function formatCheckinDateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul", month: "numeric", day: "numeric", weekday: "short",
    hour: "2-digit", minute: "2-digit", hour12: false
  }).format(new Date(value));
}

async function loadKioskDevices() {
  try {
    const response = await fetch("/api/owner/kiosk", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "등원 기기 정보를 불러오지 못했습니다.");
    messagingConnector = data.connector || messagingConnector;
    const devices = data.devices || [];
    $("#kioskDeviceCount").textContent = `${devices.filter(item => item.active).length}대 사용`;
    $("#kioskDeviceList").innerHTML = devices.length ? devices.map(item => `
      <div class="kiosk-device-row">
        <span><strong>${escapeHtml(item.name)}</strong><small>최근 연결 ${escapeHtml(formatCheckinDateTime(item.last_seen_at))}</small></span>
        <button class="secondary small" type="button" data-kiosk-device="${escapeHtml(item.id)}" data-kiosk-active="${item.active ? "0" : "1"}">${item.active ? "연결 해제" : "다시 사용"}</button>
      </div>`).join("") : `<div class="compact-empty">아직 연결한 등원 기기가 없습니다.</div>`;
    $$("[data-kiosk-device]").forEach(button => button.addEventListener("click", async () => { try { await updateKioskDevice(button.dataset.kioskDevice, button.dataset.kioskActive === "1"); } catch (error) { toast(error.message); } }));
    const status = $("#checkinConnectorStatus");
    status.textContent = !messagingConnector.configured ? "카카오 송수신기를 연결하면 등원과 동시에 학부모 카톡이 발송됩니다. 현재는 등원 기록만 안전하게 저장됩니다." : messagingConnector.ready ? "카카오 송수신기가 연결되어 등원 알림을 보낼 수 있습니다." : "송수신기 설정은 있지만 현재 응답하지 않습니다. 등원 기록은 계속 저장됩니다.";
    status.className = `messaging-status ${messagingConnector.ready ? "ready" : "warn"}`;
  } catch (error) {
    $("#kioskDeviceList").innerHTML = `<div class="compact-empty">${escapeHtml(error.message)}</div>`;
  }
}

async function createKioskPairingCode() {
  const response = await fetch("/api/owner/kiosk/pairing-code", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "연결코드를 만들지 못했습니다.");
  const expires = new Date(data.expiresAt * 1000);
  $("#pairingCodeBox").innerHTML = `<strong>${escapeHtml(data.code)}</strong><small>${expires.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })}까지 한 번만 사용 가능</small>`;
  toast("등원 기기에서 6자리 연결코드를 입력해 주세요.");
}

async function updateKioskDevice(deviceId, active) {
  if (!active && !window.confirm("이 기기의 등원 기록 권한을 해제할까요? 다시 사용으로 바꿀 수 있습니다.")) return;
  const response = await fetch("/api/owner/kiosk/device-status", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deviceId, active })
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "기기 상태를 바꾸지 못했습니다.");
  toast(active ? "등원 기기를 다시 사용하도록 설정했습니다." : "등원 기기 연결을 해제했습니다.");
  await loadKioskDevices();
}

function renderCheckinReport() {
  if (!checkinReport) return;
  const summary = checkinReport.summary;
  $("#todayCheckinCount").textContent = summary.todayCheckins || 0;
  $("#checkinReportRange").textContent = `${checkinReport.startDate} – ${checkinReport.endDate}`;
  $("#checkinSummary").innerHTML = `
    <div><span>등원 기록</span><strong>${summary.totalCheckins}<small>건</small></strong></div>
    <div><span>등원 학생</span><strong>${summary.uniqueStudents}<small>명</small></strong></div>
    <div><span>카톡 전송</span><strong>${summary.notificationsSent}<small>건</small></strong></div>
    <div class="${summary.notificationsAttention ? "needs-attention" : ""}"><span>확인 필요</span><strong>${summary.notificationsAttention}<small>건</small></strong></div>`;
  const rows = (checkinReport.students || []).filter(item => item.checkinDays > 0);
  $("#checkinReportCards").innerHTML = rows.length ? rows.map(item => `
    <article class="panel checkin-report-card">
      <div class="checkin-report-head"><span class="initial">${escapeHtml(item.studentName.slice(0, 1))}</span><div><h3>${escapeHtml(item.studentName)}</h3><p>${item.plannedDays ? `예정 ${item.plannedDays}일 중 ${item.checkinDays}일 등원` : `${item.checkinDays}일 등원`}${item.attendanceRate !== null ? ` · ${item.attendanceRate}%` : ""}</p></div><span class="badge ${item.messagingLinked ? "ready-badge" : "coral"}">${item.messagingLinked ? "카톡 연결" : "카톡 미연결"}</span></div>
      <div class="checkin-report-stats"><span><small>등원 횟수</small><b>${item.checkinCount}회</b></span><span><small>첫 등원</small><b>${escapeHtml(item.firstTime || "-")}</b></span><span><small>마지막 등원</small><b>${escapeHtml(item.lastTime || "-")}</b></span></div>
      <textarea rows="7" data-checkin-message="${escapeHtml(item.studentId)}">${escapeHtml(item.message)}</textarea>
      <div class="checkin-report-actions"><button class="secondary" type="button" data-copy-checkin-report="${escapeHtml(item.studentId)}">문안 복사</button>${item.messagingLinked ? `<button class="kakao-send-button" type="button" data-send-checkin-report="${escapeHtml(item.studentId)}">카톡으로 보내기</button>` : `<button class="secondary" type="button" data-link-checkin-student="${escapeHtml(item.studentId)}">학부모 카톡방 연결</button>`}</div>
    </article>`).join("") : `<div class="panel compact-empty">선택한 기간의 등원 기록이 없습니다. 태블릿에서 첫 등원을 기록하면 여기에 리포트가 만들어집니다.</div>`;
  $("#checkinRecentList").innerHTML = checkinReport.recent.length ? checkinReport.recent.map(item => `
    <div class="checkin-record-row"><strong>${escapeHtml(item.studentName)}</strong><span>${escapeHtml(formatCheckinDateTime(item.checkedInAt))}</span><span class="badge ${item.notificationStatus === "sent" ? "ready-badge" : item.notificationStatus === "pending" || item.notificationStatus === "sending" ? "" : "coral"}">${escapeHtml(checkinNotificationLabels[item.notificationStatus] || item.notificationStatus)}</span></div>`).join("") : `<div class="compact-empty">선택한 기간의 등원 기록이 없습니다.</div>`;
  $$('[data-copy-checkin-report]').forEach(button => button.addEventListener("click", () => copyCheckinReport(button.dataset.copyCheckinReport)));
  $$('[data-send-checkin-report]').forEach(button => button.addEventListener("click", async () => { try { await sendCheckinReport(button.dataset.sendCheckinReport); } catch (error) { toast(error.message); } }));
  $$('[data-link-checkin-student]').forEach(button => button.addEventListener("click", () => openMessagingDialog(button.dataset.linkCheckinStudent)));
}

async function loadCheckinReport(silent = false) {
  const selectedDate = $("#checkinReportDate")?.value || localDate();
  try {
    const response = await fetch(`/api/owner/checkins/report?period=${encodeURIComponent(checkinReportPeriod)}&date=${encodeURIComponent(selectedDate)}`, { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "등원 리포트를 불러오지 못했습니다.");
    checkinReport = data;
    renderCheckinReport();
  } catch (error) {
    if (!silent) toast(error.message);
  }
}

async function copyCheckinReport(studentId) {
  const textarea = $(`[data-checkin-message="${CSS.escape(studentId)}"]`);
  if (!textarea) return;
  try { await navigator.clipboard.writeText(textarea.value); }
  catch { textarea.select(); document.execCommand("copy"); }
  toast("등원 리포트 문안을 복사했습니다.");
}

async function sendCheckinReport(studentId) {
  const item = checkinReport?.students.find(student => student.studentId === studentId);
  const textarea = $(`[data-checkin-message="${CSS.escape(studentId)}"]`);
  if (!item || !textarea) return;
  if (!messagingConnector.ready) { toast("설치 장소의 카카오 송수신기 연결 상태를 확인해 주세요."); return; }
  if (!window.confirm(`${item.studentName} 학생의 학부모 카톡방 '${item.messagingRoomTitle}'에 이 리포트를 전송할까요?\n\n전송 후 자동 재전송하지 않습니다.`)) return;
  const requestId = globalThis.crypto?.randomUUID?.() || `report-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const response = await fetch("/api/owner/checkins/report/send", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      studentId, message: textarea.value.trim(), confirmed: true, requestId,
      periodKey: `${checkinReport.period}:${checkinReport.startDate}`
    })
  });
  const data = await response.json();
  if (!response.ok || !data.ok) throw new Error(data.error || data.notice || "전송 결과를 확인하지 못했습니다.");
  toast(data.notice || "등원 리포트를 전송했습니다.");
}

async function init() {
  await setupOwnerSession();
  await loadFeedbackConfig();
  try {
    await loadOwnerState();
  } catch (error) {
    console.warn(error.message);
    toast("서버 데이터 연결에 실패해 이 브라우저의 임시 데이터로 열었습니다.");
  }
  const today = new Date();
  $("#todayLabel").textContent = new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "long", day: "numeric", weekday: "long" }).format(today);
  $("#recordDate").value = localDate();
  $("#dailyFeedbackDate").value = localDate();
  $("#checkinReportDate").value = localDate();
  populateSelects(); renderDashboard(); renderPeopleManagement(); renderWeekly(); renderStudents(); renderAttendance(); renderConsultations(); updateParentPreview(); syncWeeklySchedule();
  loadCheckinReport(true);

  $$(".nav-item").forEach(button => button.addEventListener("click", () => switchView(button.dataset.view)));
  $("#navMoreToggle").addEventListener("click", () => setMobileMoreMenu($("#mobileMoreMenu").hidden));
  $$('[data-mobile-view]').forEach(button => button.addEventListener("click", () => switchView(button.dataset.mobileView)));
  document.addEventListener("click", event => {
    if (!$("#mobileMoreMenu").hidden && !event.target.closest(".sidebar")) setMobileMoreMenu(false);
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !$("#mobileMoreMenu").hidden) setMobileMoreMenu(false);
  });
  $$('[data-view-jump]').forEach(button => button.addEventListener("click", () => switchView(button.dataset.viewJump)));
  $$('[data-open-compose]').forEach(button => button.addEventListener("click", () => switchView("compose")));
  $$('[data-open-schedule]').forEach(button => button.addEventListener("click", () => openScheduleDialog()));
  if (localStorage.getItem(timetableUxVersionKey) !== "2") {
    localStorage.setItem(timetableCollapsedKey, "true");
    localStorage.setItem(timetableUxVersionKey, "2");
  }
  setWeeklyTimetableCollapsed(localStorage.getItem(timetableCollapsedKey) !== "false");
  $("#weeklyTimetableToggle").addEventListener("click", () => {
    setWeeklyTimetableCollapsed(!$("#weeklyTimetableToggle").matches('[aria-expanded="false"]'));
  });
  $("#timetableTodayButton").addEventListener("click", () => {
    if ($("#weeklyTimetable").hidden) setWeeklyTimetableCollapsed(false);
    positionTimetableToday(true);
  });
  $("#timetableFilterMode").addEventListener("change", event => {
    timetableFilterMode = event.currentTarget.value;
    timetableFilterId = "";
    updateTimetableFilterOptions();
    renderWeeklyTimetable();
  });
  $("#timetableFilterPerson").addEventListener("change", event => {
    timetableFilterId = event.currentTarget.value;
    renderWeeklyTimetable();
  });
  $("#recordClass").addEventListener("change", updateStudentSelect);
  ["#recordStudent", "#commonSummary", "#studentNotes", "#lessonPhotos"].forEach(selector => $(selector).addEventListener(selector === "#lessonPhotos" ? "change" : "input", updateParentPreview));
  $("#saveDraft").addEventListener("click", async () => { try { await saveRecord("임시저장"); } catch (error) { toast(error.message); } });
  $("#recordForm").addEventListener("submit", async event => { event.preventDefault(); try { if (await saveRecord("주간 누적")) switchView("weekly"); } catch (error) { toast(error.message); } });
  $("#weeklyFilters").addEventListener("click", event => { const button = event.target.closest("[data-weekly-filter]"); if (!button) return; weeklyFilter = button.dataset.weeklyFilter; $$("[data-weekly-filter]").forEach(item => item.classList.toggle("active", item === button)); renderWeekly(); });
  $("#dailyFeedbackDate").addEventListener("change", loadDailyEvaluations);
  $("#dailyFeedbackFilters").addEventListener("click", event => { const button = event.target.closest("[data-daily-filter]"); if (!button) return; dailyFeedbackFilter = button.dataset.dailyFilter; $$("[data-daily-filter]").forEach(item => item.classList.toggle("active", item === button)); renderDailyFeedback(); });
  $("#openMessagingSettings").addEventListener("click", () => openMessagingDialog());
  $("#refreshMessagingRooms").addEventListener("click", refreshMessagingRooms);
  $("#messagingLinkForm").addEventListener("submit", async event => { try { await saveMessagingLink(event); } catch (error) { toast(error.message); } });
  $(".messaging-close").addEventListener("click", () => $("#messagingDialog").close());
  $("#studentSearch").addEventListener("input", event => renderStudents(event.currentTarget.value));
  $("#globalSearch").addEventListener("keydown", event => { if (event.key === "Enter") { $("#studentSearch").value = event.currentTarget.value; switchView("students"); renderStudents(event.currentTarget.value); } });
  $("#consultForm").addEventListener("submit", saveConsultation);
  $("#createKioskPairingCode").addEventListener("click", async () => { try { await createKioskPairingCode(); } catch (error) { toast(error.message); } });
  $("#refreshCheckinReport").addEventListener("click", () => loadCheckinReport());
  $("#checkinReportDate").addEventListener("change", () => loadCheckinReport());
  $("#checkinPeriodFilters").addEventListener("click", event => {
    const button = event.target.closest("[data-checkin-period]");
    if (!button) return;
    checkinReportPeriod = button.dataset.checkinPeriod;
    $$('[data-checkin-period]').forEach(item => item.classList.toggle("active", item === button));
    loadCheckinReport();
  });
  $("#scheduleForm").addEventListener("submit", saveSchedule);
  $("#scheduleStudentSearch").addEventListener("input", event => renderScheduleStudentChecks(event.currentTarget.value));
  $("#cancelSchedule").addEventListener("click", () => $("#scheduleDialog").close());
  $("#deleteSchedule").addEventListener("click", deleteSchedule);
  $(".schedule-close").addEventListener("click", () => $("#scheduleDialog").close());
  $("#detailDialog .dialog-close").addEventListener("click", () => $("#detailDialog").close());
  $$('[data-new-student]').forEach(button => button.addEventListener("click", () => openStudentForm()));
  $$('[data-new-teacher]').forEach(button => button.addEventListener("click", () => openTeacherForm()));
  $("#studentRegistrySearch").addEventListener("input", renderPeopleManagement);
  $("#teacherRegistrySearch").addEventListener("input", renderPeopleManagement);
  $("#studentForm").addEventListener("submit", async event => { try { await saveStudentProfile(event); } catch (error) { toast(error.message); } });
  $("#teacherForm").addEventListener("submit", async event => { try { await saveTeacherProfile(event); } catch (error) { toast(error.message); } });
  $("#workScheduleForm").addEventListener("submit", saveWorkSchedule);
  $("#workScheduleTeacher").addEventListener("change", event => renderWorkScheduleRows(event.currentTarget.value));
  $(".work-schedule-close").addEventListener("click", () => $("#workScheduleDialog").close());
  $(".cancel-work-schedule").addEventListener("click", () => $("#workScheduleDialog").close());
  $$('[data-open-teacher-absence]').forEach(button => button.addEventListener("click", () => openTeacherAbsenceDialog(button.dataset.teacherId || "")));
  $("#teacherAbsenceForm").addEventListener("submit", saveTeacherAbsence);
  $(".teacher-absence-close").addEventListener("click", () => $("#teacherAbsenceDialog").close());
  $(".cancel-teacher-absence").addEventListener("click", () => $("#teacherAbsenceDialog").close());
  $(".student-profile-close").addEventListener("click", () => $("#studentDialog").close());
  $(".cancel-student-profile").addEventListener("click", () => $("#studentDialog").close());
  $(".teacher-profile-close").addEventListener("click", () => $("#teacherDialog").close());
  $(".cancel-teacher-profile").addEventListener("click", () => $("#teacherDialog").close());
  $("#detailDialog").addEventListener("click", event => { if (event.target === $("#detailDialog")) $("#detailDialog").close(); });
  $("#scheduleDialog").addEventListener("click", event => { if (event.target === $("#scheduleDialog")) $("#scheduleDialog").close(); });
  $("#studentDialog").addEventListener("click", event => { if (event.target === $("#studentDialog")) $("#studentDialog").close(); });
  $("#teacherDialog").addEventListener("click", event => { if (event.target === $("#teacherDialog")) $("#teacherDialog").close(); });
  $("#workScheduleDialog").addEventListener("click", event => { if (event.target === $("#workScheduleDialog")) $("#workScheduleDialog").close(); });
  $("#teacherAbsenceDialog").addEventListener("click", event => { if (event.target === $("#teacherAbsenceDialog")) $("#teacherAbsenceDialog").close(); });
  $("#messagingDialog").addEventListener("click", event => { if (event.target === $("#messagingDialog")) $("#messagingDialog").close(); });
}

init().catch(error => { console.error(error); toast("화면을 시작하지 못했습니다. 서버를 다시 실행해 주세요."); });
