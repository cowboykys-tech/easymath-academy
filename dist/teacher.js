const $ = selector => document.querySelector(selector);
const KST_DATE = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
const formatTime = value => value ? new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(value)) : "--:--";
const formatDate = value => new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", month: "long", day: "numeric", weekday: "short" }).format(new Date(value));
const labels = { clock_in: "출근", clock_out: "퇴근", early_leave: "조퇴", overtime: "추가근무", schedule_change: "근무시간 변경", absence: "결근", pending: "승인 대기", approved: "승인 완료", rejected: "반려" };
const studentAttendanceLabels = { present: "출석", late: "지각", absent: "결석", excused: "인정결석", makeup: "보강" };
const dayLabels = { mon: "월", tue: "화", wed: "수", thu: "목", fri: "금", sat: "토", sun: "일" };
const dayNames = { mon: "월요일", tue: "화요일", wed: "수요일", thu: "목요일", fri: "금요일", sat: "토요일", sun: "일요일" };
const dayOrder = Object.keys(dayLabels);
const todayKey = { Mon: "mon", Tue: "tue", Wed: "wed", Thu: "thu", Fri: "fri", Sat: "sat", Sun: "sun" }[new Intl.DateTimeFormat("en-US", { timeZone: "Asia/Seoul", weekday: "short" }).format(new Date())];
const todayParts = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date()).split("-").map(Number);
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
let teacherLessons = [];
let evaluationLessons = [];
let todayWorkSchedule = null;
let teacherWorkSchedule = [];
let calendarYear = todayParts[0];
let calendarMonth = todayParts[1];

function toast(message) { const el = $("#toast"); el.textContent = message; el.classList.add("show"); clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove("show"), 2400); }
async function jsonFetch(url, options = {}) { const response = await fetch(url, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options }); const data = await response.json(); if (!response.ok) throw new Error(data.error || "요청을 처리하지 못했습니다."); return data; }

async function load() {
  const [config, meResponse] = await Promise.all([fetch("/api/config").then(r => r.json()), fetch("/api/teacher/me")]);
  $("#loadingView").hidden = true;
  if (!meResponse.ok) {
    $("#loginView").hidden = false;
    if (!config.kakaoConfigured) { $("#configNotice").hidden = false; $("#demoArea").hidden = false; }
    const error = new URLSearchParams(location.search).get("error");
    if (error) toast(error === "kakao_not_configured" ? "카카오 개발자 앱 설정이 아직 필요합니다." : "카카오 로그인을 완료하지 못했습니다.");
    return;
  }
  const me = await meResponse.json();
  $("#openAttendance").hidden = false;
  $("#appView").hidden = false;
  $("#teacherName").textContent = me.teacher.name;
  $("#teacherAvatar").textContent = me.teacher.name.slice(0, 1);
  if (me.teacher.profile_image) { $("#teacherAvatar").style.backgroundImage = `url(${JSON.stringify(me.teacher.profile_image).slice(1,-1)})`; $("#teacherAvatar").textContent = ""; }
  $("#todayLabel").textContent = new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "long", day: "numeric", weekday: "long" }).format(new Date());
  $("#evaluationDate").value = KST_DATE();
  $("#evaluationDate").max = KST_DATE();
  await Promise.all([loadHistory(), loadSchedule(), loadEvaluations()]);
}

const lessonTime = lesson => lesson.time_label || `${lesson.start_time}${lesson.end_time ? `–${lesson.end_time}` : ""}`;

async function loadSchedule() {
  try {
    const data = await jsonFetch("/api/teacher/schedule");
    teacherLessons = data.lessons;
    renderSchedule();
    renderMonthCalendar();
  } catch (error) {
    $("#myWeekCalendar").innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
  }
}

function renderSchedule() {
  $("#myLessonCount").textContent = `${teacherLessons.length}개 수업`;
  $("#myWeekCalendar").innerHTML = dayOrder.map(day => {
    const lessons = teacherLessons.filter(item => item.day === day);
    return `<section class="calendar-day ${day === todayKey ? "today" : ""}"><div class="calendar-day-head"><strong>${dayLabels[day]}요일</strong><span>${lessons.length ? `${lessons.length}개` : "수업 없음"}</span></div>${lessons.length ? lessons.map(lesson => `<button class="teacher-lesson" data-lesson-id="${escapeHtml(lesson.id)}"><span>${escapeHtml(lessonTime(lesson))}</span><strong>${escapeHtml(lesson.class_name)}</strong><small>${escapeHtml(lesson.subject)} · ${lesson.students.length}명</small></button>`).join("") : `<div class="no-lesson">배정된 수업 없음</div>`}</section>`;
  }).join("");
  document.querySelectorAll("[data-lesson-id]").forEach(button => button.addEventListener("click", () => openLesson(button.dataset.lessonId)));
}

function renderMonthCalendar() {
  const weekdayKeys = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
  const weekdayLabels = ["일", "월", "화", "수", "목", "금", "토"];
  const firstWeekday = new Date(Date.UTC(calendarYear, calendarMonth - 1, 1)).getUTCDay();
  const daysInMonth = new Date(Date.UTC(calendarYear, calendarMonth, 0)).getUTCDate();
  const cellCount = Math.ceil((firstWeekday + daysInMonth) / 7) * 7;
  $("#monthLabel").textContent = `${calendarYear}년 ${calendarMonth}월`;
  const headers = weekdayLabels.map((label, index) => `<div class="month-weekday ${index === 0 ? "sunday" : index === 6 ? "saturday" : ""}">${label}</div>`).join("");
  const cells = Array.from({ length: cellCount }, (_, index) => {
    const dayNumber = index - firstWeekday + 1;
    if (dayNumber < 1 || dayNumber > daysInMonth) return `<div class="month-day outside"></div>`;
    const weekdayIndex = index % 7;
    const weekday = weekdayKeys[weekdayIndex];
    const lessons = teacherLessons.filter(item => item.day === weekday);
    const isToday = calendarYear === todayParts[0] && calendarMonth === todayParts[1] && dayNumber === todayParts[2];
    const dateLabel = `${calendarMonth}월 ${dayNumber}일 ${weekdayIndex === 0 ? "일요일" : weekdayIndex === 6 ? "토요일" : dayNames[weekday]}`;
    return `<div class="month-day ${weekdayIndex === 0 ? "sunday" : weekdayIndex === 6 ? "saturday" : ""} ${isToday ? "today" : ""}"><span class="month-date">${dayNumber}</span>${lessons.map(lesson => `<button class="month-lesson" data-month-lesson-id="${escapeHtml(lesson.id)}" data-lesson-date="${escapeHtml(dateLabel)}"><strong>${escapeHtml(lesson.class_name)}</strong><small>${escapeHtml(lessonTime(lesson))}</small></button>`).join("")}</div>`;
  }).join("");
  $("#monthCalendar").innerHTML = headers + cells;
  document.querySelectorAll("[data-month-lesson-id]").forEach(button => button.addEventListener("click", () => openLesson(button.dataset.monthLessonId, button.dataset.lessonDate)));
}

function moveMonth(offset) {
  const next = new Date(Date.UTC(calendarYear, calendarMonth - 1 + offset, 1));
  calendarYear = next.getUTCFullYear();
  calendarMonth = next.getUTCMonth() + 1;
  renderMonthCalendar();
}

function openLesson(id, dateLabel = "") {
  const lesson = teacherLessons.find(item => item.id === id);
  if (!lesson) return;
  $("#lessonDialogDay").textContent = dateLabel || dayNames[lesson.day];
  $("#lessonDialogTitle").textContent = lesson.class_name;
  $("#lessonDialogTime").textContent = lessonTime(lesson);
  $("#lessonDialogSubject").textContent = lesson.subject;
  $("#lessonStudentCount").textContent = `${lesson.students.length}명`;
  $("#lessonStudentList").innerHTML = lesson.students.length ? lesson.students.map(student => `<div class="student-row"><span class="student-initial">${escapeHtml(student.name.slice(0, 1))}</span><div><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.school || "학교 정보 없음")}</small></div></div>`).join("") : `<div class="empty">등록된 학생이 없습니다.</div>`;
  $("#lessonDialog").showModal();
}

const evaluationFields = [
  { key: "attitude", label: "수업 태도", options: ["보완 필요", "조금 아쉬움", "좋음", "매우 좋음"] },
  { key: "concentration", label: "집중도", options: ["집중 어려움", "간헐적 집중", "잘 집중함", "매우 몰입함"] },
  { key: "understanding", label: "이해도", options: ["추가 설명 필요", "반복 연습 필요", "잘 이해함", "응용 가능"] },
  { key: "progress", label: "진도", options: ["진도 보완", "조금 느림", "계획대로", "심화 가능"] },
  { key: "participation", label: "참여도", options: ["소극적", "보통", "적극적", "주도적"] },
  { key: "homework", label: "과제 수행", options: ["보완 필요", "일부 수행", "잘 수행함", "매우 충실함"] }
];

async function loadEvaluations() {
  const lessonDate = $("#evaluationDate").value || KST_DATE();
  try {
    const data = await jsonFetch(`/api/teacher/evaluations?date=${encodeURIComponent(lessonDate)}`);
    evaluationLessons = data.lessons || [];
    renderEvaluations();
  } catch (error) {
    evaluationLessons = [];
    $("#evaluationProgress").textContent = "평가를 불러오지 못했습니다.";
    $("#evaluationLessonList").innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
  }
}

function renderEvaluations() {
  const students = evaluationLessons.flatMap(lesson => lesson.students || []);
  const completed = students.filter(student => student.attendance && (["absent", "excused"].includes(student.attendance.attendance_status) || student.evaluation)).length;
  $("#evaluationProgress").textContent = `${completed} / ${students.length}명 출결·평가 완료`;
  $("#evaluationLessonList").innerHTML = evaluationLessons.length ? evaluationLessons.map(lesson => {
    const lessonCompleted = lesson.students.filter(student => student.attendance && (["absent", "excused"].includes(student.attendance.attendance_status) || student.evaluation)).length;
    return `<article class="evaluation-lesson"><div class="evaluation-lesson-head"><div><strong>${escapeHtml(lesson.class_name)}</strong><span>${escapeHtml(lessonTime(lesson))} · ${escapeHtml(lesson.subject)}</span></div><small>${lessonCompleted}/${lesson.students.length}명 완료</small></div><div class="evaluation-students">${lesson.students.length ? lesson.students.map(student => { const status = student.attendance?.attendance_status; const complete = student.attendance && (["absent", "excused"].includes(status) || student.evaluation); const stateLabel = status ? `${studentAttendanceLabels[status]}${student.evaluation ? " · 평가 완료" : ""}` : "출결·평가"; return `<button type="button" class="evaluation-student ${complete ? "completed" : ""}" data-evaluation-lesson="${escapeHtml(lesson.id)}" data-evaluation-student="${escapeHtml(student.id)}"><span class="student-initial">${escapeHtml(student.name.slice(0, 1))}</span><span><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.school || "학교 정보 없음")}</small></span><span class="evaluation-state">${escapeHtml(stateLabel)}</span></button>`; }).join("") : `<div class="empty">등록된 학생이 없습니다.</div>`}</div></article>`;
  }).join("") : `<div class="empty">선택한 날짜에 배정된 수업이 없습니다.</div>`;
  document.querySelectorAll("[data-evaluation-lesson]").forEach(button => button.addEventListener("click", () => openStudentEvaluation(button.dataset.evaluationLesson, button.dataset.evaluationStudent)));
}

function openStudentEvaluation(lessonId, studentId) {
  const lesson = evaluationLessons.find(item => item.id === lessonId);
  const student = lesson?.students.find(item => String(item.id) === studentId);
  if (!lesson || !student) return;
  const saved = student.evaluation;
  const savedAttendance = student.attendance;
  $("#evaluationLessonId").value = lesson.id;
  $("#evaluationStudentId").value = student.id;
  $("#evaluationDialogTitle").textContent = `${student.name} 학생 평가`;
  $("#evaluationLessonSummary").textContent = `${$("#evaluationDate").value} · ${lessonTime(lesson)} · ${lesson.class_name} · ${lesson.subject}`;
  $("#evaluationCriteria").innerHTML = evaluationFields.map(field => `<fieldset class="evaluation-field"><legend>${field.label}</legend><div class="evaluation-options">${field.options.map((label, index) => `<label class="evaluation-option"><input type="radio" name="${field.key}" value="${index + 1}" ${Number(saved?.[field.key]) === index + 1 ? "checked" : ""} required><span>${label}</span></label>`).join("")}</div></fieldset>`).join("");
  $("#studentAttendanceStatus").value = savedAttendance?.attendance_status || "present";
  $("#evaluationNote").value = saved?.note || savedAttendance?.note || "";
  $("#evaluationNoteCount").textContent = $("#evaluationNote").value.length;
  updateEvaluationAttendanceState();
  $("#evaluationDialog").showModal();
}

function updateEvaluationAttendanceState() {
  const status = $("#studentAttendanceStatus").value;
  const evaluationRequired = !["absent", "excused"].includes(status);
  $("#evaluationCriteria").classList.toggle("disabled", !evaluationRequired);
  document.querySelectorAll('#evaluationCriteria input[type="radio"]').forEach(input => {
    input.disabled = !evaluationRequired;
    input.required = evaluationRequired;
  });
  $("#evaluationNote").required = evaluationRequired;
  $("#evaluationNote").placeholder = evaluationRequired
    ? "오늘 잘한 점, 어려워한 부분, 다음 수업에서 확인할 내용을 몇 문장으로 적어 주세요."
    : "결석 또는 인정결석 사유가 있으면 적어 주세요. (선택)";
  $(".save-evaluation").textContent = evaluationRequired ? "출결·평가 저장" : "출결만 저장";
}

async function saveEvaluation(event) {
  event.preventDefault();
  const payload = {
    lessonId: $("#evaluationLessonId").value,
    studentId: $("#evaluationStudentId").value,
    lessonDate: $("#evaluationDate").value,
    note: $("#evaluationNote").value.trim()
  };
  const attendanceStatus = $("#studentAttendanceStatus").value;
  const attendancePayload = {
    lessonId: payload.lessonId,
    studentId: payload.studentId,
    lessonDate: payload.lessonDate,
    attendanceStatus,
    note: payload.note
  };
  const evaluationRequired = !["absent", "excused"].includes(attendanceStatus);
  if (!evaluationRequired) {
    try {
      await jsonFetch("/api/teacher/student-attendance", { method: "POST", body: JSON.stringify(attendancePayload) });
      $("#evaluationDialog").close();
      toast(`${studentAttendanceLabels[attendanceStatus]}으로 저장해 원장님께 전달했습니다.`);
      await loadEvaluations();
    } catch (error) { toast(error.message); }
    return;
  }
  for (const field of evaluationFields) {
    const selected = document.querySelector(`input[name="${field.key}"]:checked`);
    if (!selected) { toast(`${field.label} 항목을 선택해 주세요.`); return; }
    payload[field.key] = Number(selected.value);
  }
  try {
    await jsonFetch("/api/teacher/student-attendance", { method: "POST", body: JSON.stringify(attendancePayload) });
    await jsonFetch("/api/teacher/evaluations", { method: "POST", body: JSON.stringify(payload) });
    $("#evaluationDialog").close();
    toast("학생 평가를 저장하고 원장님께 전달했습니다.");
    await loadEvaluations();
  } catch (error) { toast(error.message); }
}

async function loadHistory() {
  const data = await jsonFetch("/api/teacher/history");
  const requests = data.requests;
  const adjustments = data.adjustments || [];
  teacherWorkSchedule = data.workSchedule || [];
  todayWorkSchedule = data.todaySchedule || null;
  const today = KST_DATE();
  const todays = requests.filter(item => item.work_date === today);
  const todayAdjustments = adjustments.filter(item => item.work_date === today && item.status !== "rejected");
  const clockIn = todays.find(item => item.event_type === "clock_in" && item.status !== "rejected");
  const clockOut = todays.find(item => item.event_type === "clock_out" && item.status !== "rejected");
  const earlyLeave = todayAdjustments.find(item => item.request_type === "early_leave");
  const overtime = todayAdjustments.find(item => item.request_type === "overtime");
  $("#todayWorkPlan").innerHTML = todayWorkSchedule
    ? `<span>오늘 예정 근무</span><strong>${escapeHtml(todayWorkSchedule.start_time)}–${escapeHtml(todayWorkSchedule.end_time)}</strong><small>${todayWorkSchedule.break_minutes ? `휴게 ${todayWorkSchedule.break_minutes}분` : "휴게시간 없음"}</small>`
    : `<span>오늘 예정 근무</span><strong>등록된 근무시간 없음</strong><small>원장님이 먼저 등록해야 합니다.</small>`;
  $("#clockInTime").textContent = formatTime(clockIn?.requested_at);
  $("#clockOutTime").textContent = formatTime(clockOut?.requested_at);
  $("#clockInStatus").textContent = clockIn ? labels[clockIn.status] : "요청 전";
  $("#clockOutStatus").textContent = clockOut ? labels[clockOut.status] : "요청 전";
  $("#clockInButton").disabled = !todayWorkSchedule || Boolean(clockIn);
  $("#clockOutButton").disabled = !clockIn || clockIn.status !== "approved" || Boolean(clockOut);
  $("#earlyLeaveButton").disabled = !todayWorkSchedule || !clockIn || clockIn.status !== "approved" || Boolean(clockOut) || Boolean(earlyLeave);
  $("#overtimeButton").disabled = !todayWorkSchedule || !clockIn || clockIn.status !== "approved" || Boolean(overtime);
  $("#scheduleChangeButton").disabled = teacherWorkSchedule.length === 0;
  $("#earlyLeaveButton").textContent = earlyLeave ? `조퇴 ${labels[earlyLeave.status]}` : "조퇴 요청";
  $("#overtimeButton").textContent = overtime ? `추가근무 ${labels[overtime.status]}` : "추가근무 요청";
  if (!todayWorkSchedule) { $("#statusTitle").textContent = "오늘 근무시간이 등록되지 않았습니다."; $("#statusDescription").textContent = "원장님이 오늘 예정 근무를 등록하면 출근 요청을 보낼 수 있습니다."; $("#attendanceQuickStatus").textContent = "근무시간 미등록"; }
  else if (!clockIn) { $("#statusTitle").textContent = "오늘 근무를 시작해 주세요."; $("#statusDescription").textContent = "출근 버튼을 누르면 원장님에게 승인 요청이 전달됩니다."; $("#attendanceQuickStatus").textContent = "출근 전"; }
  else if (clockIn.status === "pending") { $("#statusTitle").textContent = "출근 승인을 기다리고 있어요."; $("#statusDescription").textContent = "원장님이 승인하면 출근 기록이 확정되고 퇴근 요청 버튼이 열립니다."; $("#attendanceQuickStatus").textContent = "출근 승인 대기"; }
  else if (!clockOut) { $("#statusTitle").textContent = "출근이 승인되었습니다."; $("#statusDescription").textContent = "수업을 마친 뒤 퇴근 요청을 눌러 주세요."; $("#attendanceQuickStatus").textContent = "근무 중"; }
  else if (clockOut.status === "pending") { $("#statusTitle").textContent = "퇴근 승인을 기다리고 있어요."; $("#statusDescription").textContent = "원장님이 승인하면 오늘 근무 기록이 완성됩니다."; $("#attendanceQuickStatus").textContent = "퇴근 승인 대기"; }
  else { $("#statusTitle").textContent = "오늘 근무 기록이 완료되었습니다."; $("#statusDescription").textContent = "출근과 퇴근 시간이 모두 승인되었습니다."; $("#attendanceQuickStatus").textContent = "근무 완료"; }
  const history = [
    ...requests.map(item => ({ ...item, kind: item.event_type, detail: formatTime(item.requested_at) })),
    ...adjustments.map(item => ({ ...item, kind: item.request_type, detail: item.request_type === "early_leave" ? `${item.end_time} 조퇴` : item.request_type === "absence" ? "근무 없음" : `${item.start_time}–${item.end_time}` }))
  ].sort((a, b) => b.requested_at.localeCompare(a.requested_at));
  $("#historyList").innerHTML = history.length ? history.map(item => `<div class="history-item"><strong>${labels[item.kind]}</strong><div><span>${escapeHtml(item.detail)}</span><small>${formatDate(item.requested_at)}${item.reason ? ` · ${escapeHtml(item.reason)}` : ""}</small></div><span class="status ${item.status}">${labels[item.status]}</span></div>`).join("") : `<div class="empty">아직 근무 요청이 없습니다.</div>`;
}

async function requestAttendance(eventType) {
  try { await jsonFetch("/api/teacher/attendance", { method: "POST", body: JSON.stringify({ eventType }) }); toast(`${labels[eventType]} 요청을 원장님께 보냈습니다.`); await loadHistory(); }
  catch (error) { toast(error.message); }
}

function addMinutes(value, amount) {
  const [hours, minutes] = value.split(":").map(Number);
  const total = Math.max(0, Math.min(23 * 60 + 59, hours * 60 + minutes + amount));
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

function dateAtOffset(offset) {
  const date = new Date(Date.UTC(todayParts[0], todayParts[1] - 1, todayParts[2] + offset));
  return date.toISOString().slice(0, 10);
}

function workPlanForDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  const dayKey = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"][new Date(Date.UTC(year, month - 1, day)).getUTCDay()];
  return teacherWorkSchedule.find(item => item.day === dayKey) || null;
}

function updateScheduleChangePlan() {
  const plan = workPlanForDate($("#scheduleChangeDate").value);
  if (!plan) {
    $("#adjustmentPlanSummary").textContent = "선택한 요일에는 등록된 근무시간이 없습니다.";
    $("#scheduleChangeStart").value = "";
    $("#scheduleChangeEnd").value = "";
    return;
  }
  $("#adjustmentPlanSummary").textContent = `기존 예정 근무 ${plan.start_time}–${plan.end_time}${plan.break_minutes ? ` · 휴게 ${plan.break_minutes}분` : ""}`;
  $("#scheduleChangeStart").value = plan.start_time;
  $("#scheduleChangeEnd").value = plan.end_time;
}

function openAdjustmentDialog(requestType) {
  if (requestType !== "schedule_change" && !todayWorkSchedule) { toast("원장님이 오늘 근무시간을 먼저 등록해야 합니다."); return; }
  if (requestType === "schedule_change" && !teacherWorkSchedule.length) { toast("원장님이 주간 근무시간을 먼저 등록해야 합니다."); return; }
  const isEarlyLeave = requestType === "early_leave";
  const isOvertime = requestType === "overtime";
  const isScheduleChange = requestType === "schedule_change";
  $("#adjustmentType").value = requestType;
  $("#adjustmentDialogTitle").textContent = isEarlyLeave ? "조퇴 요청" : isOvertime ? "추가근무 요청" : "근무시간 변경 요청";
  $("#adjustmentPlanSummary").textContent = isScheduleChange ? "날짜를 선택해 주세요." : `오늘 예정 근무 ${todayWorkSchedule.start_time}–${todayWorkSchedule.end_time}${todayWorkSchedule.break_minutes ? ` · 휴게 ${todayWorkSchedule.break_minutes}분` : ""}`;
  $("#earlyLeaveFields").hidden = !isEarlyLeave;
  $("#overtimeFields").hidden = !isOvertime;
  $("#scheduleChangeFields").hidden = !isScheduleChange;
  $("#earlyLeaveEnd").required = isEarlyLeave;
  $("#overtimeStart").required = isOvertime;
  $("#overtimeEnd").required = isOvertime;
  $("#scheduleChangeDate").required = isScheduleChange;
  $("#scheduleChangeStart").required = isScheduleChange;
  $("#scheduleChangeEnd").required = isScheduleChange;
  if (isEarlyLeave) {
    $("#earlyLeaveEnd").value = addMinutes(todayWorkSchedule.end_time, -30);
  } else if (isOvertime) {
    $("#overtimeStart").value = todayWorkSchedule.end_time;
    $("#overtimeEnd").value = addMinutes(todayWorkSchedule.end_time, 60);
  } else if (isScheduleChange) {
    $("#scheduleChangeDate").min = KST_DATE();
    $("#scheduleChangeDate").removeAttribute("max");
    $("#scheduleChangeDate").value = Array.from({ length: 7 }, (_, offset) => dateAtOffset(offset)).find(workPlanForDate) || KST_DATE();
    updateScheduleChangePlan();
  }
  $("#adjustmentReason").value = "";
  $("#adjustmentDialog").showModal();
}

async function requestAdjustment(event) {
  event.preventDefault();
  const requestType = $("#adjustmentType").value;
  const payload = { requestType, reason: $("#adjustmentReason").value.trim() };
  if (requestType === "early_leave") payload.endTime = $("#earlyLeaveEnd").value;
  else if (requestType === "overtime") { payload.startTime = $("#overtimeStart").value; payload.endTime = $("#overtimeEnd").value; }
  else if (requestType === "schedule_change") { payload.workDate = $("#scheduleChangeDate").value; payload.startTime = $("#scheduleChangeStart").value; payload.endTime = $("#scheduleChangeEnd").value; }
  try {
    await jsonFetch("/api/teacher/attendance-adjustment", { method: "POST", body: JSON.stringify(payload) });
    $("#adjustmentDialog").close();
    toast(`${labels[requestType]} 요청을 원장님께 보냈습니다.`);
    await loadHistory();
  } catch (error) { toast(error.message); }
}

$("#clockInButton").addEventListener("click", () => requestAttendance("clock_in"));
$("#clockOutButton").addEventListener("click", () => requestAttendance("clock_out"));
$("#earlyLeaveButton").addEventListener("click", () => openAdjustmentDialog("early_leave"));
$("#overtimeButton").addEventListener("click", () => openAdjustmentDialog("overtime"));
$("#scheduleChangeButton").addEventListener("click", () => openAdjustmentDialog("schedule_change"));
$("#scheduleChangeDate").addEventListener("change", updateScheduleChangePlan);
$("#adjustmentForm").addEventListener("submit", requestAdjustment);
$("#closeAdjustmentDialog").addEventListener("click", () => $("#adjustmentDialog").close());
$("#cancelAdjustment").addEventListener("click", () => $("#adjustmentDialog").close());
$("#adjustmentDialog").addEventListener("click", event => { if (event.target === $("#adjustmentDialog")) $("#adjustmentDialog").close(); });
$("#openAttendance").addEventListener("click", async () => { await loadHistory(); $("#attendanceDialog").showModal(); });
$("#closeAttendanceDialog").addEventListener("click", () => $("#attendanceDialog").close());
$("#attendanceDialog").addEventListener("click", event => { if (event.target === $("#attendanceDialog")) $("#attendanceDialog").close(); });
$("#refreshButton").addEventListener("click", loadHistory);
$("#scheduleRefreshButton").addEventListener("click", loadSchedule);
$("#evaluationDate").addEventListener("change", loadEvaluations);
$("#evaluationForm").addEventListener("submit", saveEvaluation);
$("#studentAttendanceStatus").addEventListener("change", updateEvaluationAttendanceState);
$("#evaluationNote").addEventListener("input", event => { $("#evaluationNoteCount").textContent = event.currentTarget.value.length; });
$("#closeEvaluationDialog").addEventListener("click", () => $("#evaluationDialog").close());
$("#cancelEvaluation").addEventListener("click", () => $("#evaluationDialog").close());
$("#evaluationDialog").addEventListener("click", event => { if (event.target === $("#evaluationDialog")) $("#evaluationDialog").close(); });
$("#prevMonth").addEventListener("click", () => moveMonth(-1));
$("#nextMonth").addEventListener("click", () => moveMonth(1));
$("#todayMonth").addEventListener("click", () => { calendarYear = todayParts[0]; calendarMonth = todayParts[1]; renderMonthCalendar(); });
$("#closeLessonDialog").addEventListener("click", () => $("#lessonDialog").close());
$("#lessonDialog").addEventListener("click", event => { if (event.target === $("#lessonDialog")) $("#lessonDialog").close(); });
load().catch(error => { $("#loadingView").innerHTML = `<p>${error.message}</p>`; });
