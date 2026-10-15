const seed = {
  classes: [
    { id: "c1", name: "초등 심화 A반", level: "초등 5·6학년", teacherId: "t1", students: ["s1", "s2", "s3", "s4"] },
    { id: "c2", name: "중등 개념 B반", level: "중등 1학년", teacherId: "t2", students: ["s5", "s6", "s7"] },
    { id: "c3", name: "중등 심화 C반", level: "중등 2학년", teacherId: "t1", students: ["s8", "s9", "s10", "s11", "s12"] }
  ],
  teachers: [
    { id: "t1", name: "이선생", subject: "수학 심화", classes: ["c1", "c3"] },
    { id: "t2", name: "최선생", subject: "수학 개념", classes: ["c2"] }
  ],
  students: [
    { id: "s1", name: "김민서", school: "가온초 6", classId: "c1", latest: "A-2" },
    { id: "s2", name: "박도윤", school: "가온초 6", classId: "c1", latest: "A-2" },
    { id: "s3", name: "윤서아", school: "나래초 5", classId: "c1", latest: "A-2" },
    { id: "s4", name: "정하준", school: "나래초 5", classId: "c1", latest: "A-2" },
    { id: "s5", name: "한지우", school: "내포중 1", classId: "c2", latest: "B-3" },
    { id: "s6", name: "서준호", school: "내포중 1", classId: "c2", latest: "B-3" },
    { id: "s7", name: "오유나", school: "홍성중 1", classId: "c2", latest: "B-3" },
    { id: "s8", name: "임채원", school: "내포중 2", classId: "c3", latest: "A-1" }
  ],
  records: [
    { id: "r1", date: "2026-10-15", classId: "c3", teacherId: "t1", code: "A-1", title: "문자와 식의 기본 원리", summary: "문자를 사용해 수량 사이의 관계를 식으로 나타내고, 식의 값을 구하는 기본 원리를 확인했습니다. 개념을 말로 설명한 뒤 식으로 옮기는 과정을 반복했습니다.", notes: "식은 세울 수 있지만 계산 순서를 놓치는 경우가 있어 다음 수업에서 다시 확인합니다.", homework: 50, wrong: 25, status: "검토 대기" },
    { id: "r2", date: "2026-07-09", classId: "c2", teacherId: "t2", code: "A-1", title: "문자와 식의 기본 원리", summary: "문자를 이용한 식 세우기와 식의 값 계산을 학습했습니다. 생활 속 문장을 수학식으로 바꾸는 연습을 중심으로 진행했습니다.", notes: "문제의 조건을 밑줄로 구분하면 식 세우기가 안정적이었습니다.", homework: 80, wrong: 20, status: "승인 완료" },
    { id: "r3", date: "2026-03-12", classId: "c1", teacherId: "t1", code: "A-1", title: "수와 연산의 관계", summary: "연산 순서와 수 사이의 관계를 그림과 식으로 표현했습니다. 풀이 과정을 한 줄씩 설명하는 습관을 연습했습니다.", notes: "계산보다 문제를 읽고 관계를 찾는 데 집중했습니다.", homework: 90, wrong: 15, status: "승인 완료" },
    { id: "r4", date: "2026-10-14", classId: "c1", teacherId: "t1", code: "A-2", title: "규칙을 식으로 표현하기", summary: "표와 그림에서 반복되는 규칙을 찾고, 이를 간단한 식으로 표현했습니다.", notes: "규칙을 말로 설명하는 것은 잘했지만 기호로 바꾸는 연습이 더 필요합니다.", homework: 75, wrong: 18, status: "검토 대기" },
    { id: "r5", date: "2026-10-13", classId: "c2", teacherId: "t2", code: "B-3", title: "일차방정식 활용", summary: "문제 상황에서 미지수를 정하고 일차방정식을 세워 해결했습니다.", notes: "단위 확인과 답 문장 작성까지 이어지도록 지도했습니다.", homework: 65, wrong: 30, status: "검토 대기" },
    { id: "r6", date: "2026-10-10", classId: "c3", teacherId: "t1", code: "G-2", title: "도형의 성질 정리", summary: "평행선과 각의 관계를 이용해 도형의 성질을 설명했습니다.", notes: "보조선을 그어 조건을 시각화하는 방법을 연습했습니다.", homework: 85, wrong: 12, status: "승인 완료" }
  ],
  schedule: [
    { time: "14:30", classId: "c1", code: "A-2", topic: "규칙을 식으로 표현하기" },
    { time: "16:10", classId: "c3", code: "A-1", topic: "문자와 식의 기본 원리" },
    { time: "19:30", classId: "c2", code: "B-3", topic: "일차방정식 활용" }
  ]
};

const state = JSON.parse(localStorage.getItem("easymath-demo") || "null") || structuredClone(seed);
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const byId = (list, id) => list.find(item => item.id === id);
const className = id => byId(state.classes, id)?.name || "미지정 반";
const teacherName = id => byId(state.teachers, id)?.name || "미지정";
const formatDate = date => new Intl.DateTimeFormat("ko-KR", { month: "long", day: "numeric", weekday: "short" }).format(new Date(`${date}T12:00:00`));
const escapeHtml = value => String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));

function persist() {
  localStorage.setItem("easymath-demo", JSON.stringify(state));
}

function toast(message) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.add("show");
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => element.classList.remove("show"), 2200);
}

function switchView(name) {
  $$(".view").forEach(view => view.classList.toggle("active", view.id === `${name}View`));
  $$(".nav-item").forEach(button => button.classList.toggle("active", button.dataset.view === name));
  const titles = { dashboard: "오늘의 학원 흐름", records: "쌓인 기록을 다시 쓰기", compose: "이번 수업 기록하기", people: "학원 구성 한눈에 보기" };
  $("#pageTitle").textContent = titles[name];
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (name === "records") renderRecordCards();
  if (name === "compose") updateSimilarRecords();
  if (name === "people") renderPeople("classes");
}

function populateSelects() {
  const classOptions = state.classes.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  const teacherOptions = state.teachers.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  $("#classFilter").insertAdjacentHTML("beforeend", classOptions);
  $("#teacherFilter").insertAdjacentHTML("beforeend", teacherOptions);
  $("#recordClass").innerHTML = classOptions;
  $("#recordTeacher").innerHTML = teacherOptions;
}

function renderDashboard() {
  $("#scheduleList").innerHTML = state.schedule.map(item => `
    <div class="schedule-item">
      <div class="time">${item.time}</div>
      <div><strong>${escapeHtml(className(item.classId))}</strong><span>${escapeHtml(item.topic)} · ${escapeHtml(teacherName(byId(state.classes, item.classId)?.teacherId))}</span></div>
      <div class="code">${escapeHtml(item.code)}</div>
    </div>`).join("");

  const pending = state.records.filter(item => item.status === "검토 대기").slice(0, 3);
  $("#pendingList").innerHTML = pending.map(item => `
    <div class="pending-item" data-record-id="${item.id}">
      <span class="status-dot"></span>
      <div><strong>${escapeHtml(className(item.classId))} · ${escapeHtml(item.code)}</strong><span>${escapeHtml(teacherName(item.teacherId))} · ${formatDate(item.date)}</span></div>
      <button class="text-button">확인</button>
    </div>`).join("");

  const rows = [...state.records].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5);
  $("#recentRecords").innerHTML = `
    <div class="record-row header"><span>날짜</span><span>진도코드</span><span>수업 주제</span><span>반</span><span>상태</span></div>
    ${rows.map(item => `<div class="record-row" data-record-id="${item.id}"><span>${formatDate(item.date)}</span><strong>${escapeHtml(item.code)}</strong><span>${escapeHtml(item.title)}</span><span>${escapeHtml(className(item.classId))}</span><span>${escapeHtml(item.status)}</span></div>`).join("")}`;
  $("#weekRecordCount").textContent = state.records.length + 6;
  $$('[data-record-id]').forEach(element => element.addEventListener("click", () => openRecord(element.dataset.recordId)));
}

function filteredRecords() {
  const query = $("#recordSearch").value.trim().toLowerCase();
  const selectedClass = $("#classFilter").value;
  const selectedTeacher = $("#teacherFilter").value;
  return [...state.records]
    .filter(item => !query || `${item.code} ${item.title} ${item.summary}`.toLowerCase().includes(query))
    .filter(item => selectedClass === "all" || item.classId === selectedClass)
    .filter(item => selectedTeacher === "all" || item.teacherId === selectedTeacher)
    .sort((a, b) => b.date.localeCompare(a.date));
}

function renderRecordCards() {
  const records = filteredRecords();
  $("#resultCount").textContent = `${records.length}개의 기록`;
  $("#recordCards").innerHTML = records.length ? records.map(item => `
    <article class="record-card">
      <div class="record-card-top"><span class="code">${escapeHtml(item.code)}</span><span class="badge ${item.status === "검토 대기" ? "coral" : ""}">${escapeHtml(item.status)}</span></div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.summary)}</p>
      <div class="record-meta"><span>${escapeHtml(className(item.classId))}</span><span>${escapeHtml(teacherName(item.teacherId))}</span><span>${formatDate(item.date)}</span></div>
      <div class="card-actions"><button class="text-button" data-detail="${item.id}">자세히</button><button class="primary small" data-reuse="${item.id}">이 기록으로 작성</button></div>
    </article>`).join("") : `<article class="panel"><strong>조건에 맞는 기록이 없습니다.</strong><p>진도코드나 필터를 바꿔보세요.</p></article>`;
  $$('[data-detail]').forEach(button => button.addEventListener("click", () => openRecord(button.dataset.detail)));
  $$('[data-reuse]').forEach(button => button.addEventListener("click", () => reuseRecord(button.dataset.reuse)));
}

function updateSimilarRecords() {
  const code = $("#progressCode").value.trim().toLowerCase();
  const matches = [...state.records].filter(item => !code || item.code.toLowerCase() === code).sort((a, b) => b.date.localeCompare(a.date)).slice(0, 4);
  $("#similarRecords").innerHTML = matches.length ? matches.map(item => `
    <div class="similar-item"><strong>${escapeHtml(item.code)} · ${escapeHtml(className(item.classId))}</strong><small>${formatDate(item.date)} · ${escapeHtml(teacherName(item.teacherId))}</small><button type="button" data-reuse="${item.id}">내용 불러오기 →</button></div>`).join("") : `<div class="similar-item"><strong>같은 기록이 아직 없습니다.</strong><small>이번 기록이 첫 기준이 됩니다.</small></div>`;
  $$('[data-reuse]', $("#similarRecords")).forEach(button => button.addEventListener("click", () => reuseRecord(button.dataset.reuse, false)));
}

function reuseRecord(id, switchPage = true) {
  const record = byId(state.records, id);
  if (!record) return;
  if (switchPage) switchView("compose");
  $("#progressCode").value = record.code;
  $("#lessonTitle").value = record.title;
  $("#commonSummary").value = record.summary;
  $("#studentNotes").value = "";
  $("#recordTeacher").value = record.teacherId;
  updateSimilarRecords();
  toast(`${record.code} 이전 기록을 불러왔습니다. 달라진 부분을 수정하세요.`);
}

function renderPeople(type) {
  $$(".people-tab").forEach(button => button.classList.toggle("active", button.dataset.people === type));
  let cards = [];
  if (type === "classes") {
    cards = state.classes.map(item => ({ initial: item.name.slice(0, 1), title: item.name, subtitle: item.level, details: [["담당", teacherName(item.teacherId)], ["학생", `${item.students.length}명`], ["최근 진도", state.records.find(record => record.classId === item.id)?.code || "없음"]] }));
  } else if (type === "students") {
    cards = state.students.map(item => ({ initial: item.name.slice(0, 1), title: item.name, subtitle: item.school, details: [["소속 반", className(item.classId)], ["최근 진도", item.latest], ["누적 기록", `${state.records.filter(record => record.classId === item.classId).length}건`]] }));
  } else {
    cards = state.teachers.map(item => ({ initial: item.name.slice(0, 1), title: item.name, subtitle: item.subject, details: [["담당 반", `${item.classes.length}개`], ["이번 주 기록", `${state.records.filter(record => record.teacherId === item.id).length}건`], ["검토 대기", `${state.records.filter(record => record.teacherId === item.id && record.status === "검토 대기").length}건`]] }));
  }
  $("#peopleGrid").innerHTML = cards.map(card => `<article class="people-card"><div class="initial">${escapeHtml(card.initial)}</div><h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.subtitle)}</p><dl>${card.details.map(([term, value]) => `<dt>${escapeHtml(term)}</dt><dd>${escapeHtml(value)}</dd>`).join("")}</dl></article>`).join("");
}

function openRecord(id) {
  const record = byId(state.records, id);
  if (!record) return;
  $("#dialogContent").innerHTML = `<div class="dialog-body"><span class="code">${escapeHtml(record.code)}</span><h2>${escapeHtml(record.title)}</h2><div class="dialog-details"><div><span>수업일</span><strong>${formatDate(record.date)}</strong></div><div><span>반 · 선생님</span><strong>${escapeHtml(className(record.classId))} · ${escapeHtml(teacherName(record.teacherId))}</strong></div><div><span>상태</span><strong>${escapeHtml(record.status)}</strong></div></div><h3>공통 학습 내용</h3><p>${escapeHtml(record.summary)}</p><h3>학생별 관찰 내용</h3><p>${escapeHtml(record.notes)}</p><div class="dialog-actions"><button class="secondary" data-markdown="${record.id}">옵시디언용 저장</button><button class="primary" data-dialog-reuse="${record.id}">이 기록으로 작성</button></div></div>`;
  $("#recordDialog").showModal();
  $('[data-dialog-reuse]').addEventListener("click", event => { $("#recordDialog").close(); reuseRecord(event.currentTarget.dataset.dialogReuse); });
  $('[data-markdown]').addEventListener("click", event => downloadMarkdown(event.currentTarget.dataset.markdown));
}

function downloadMarkdown(id) {
  const item = byId(state.records, id);
  const markdown = `---\ndate: ${item.date}\nprogress_code: ${item.code}\nclass: ${className(item.classId)}\nteacher: ${teacherName(item.teacherId)}\nstatus: ${item.status}\n---\n\n# ${item.code} ${item.title}\n\n## 공통 학습 내용\n\n${item.summary}\n\n## 학생별 관찰 내용\n\n${item.notes}\n\n## 수치\n\n- 숙제 수행률: ${item.homework}%\n- 교재 오답률: ${item.wrong}%\n`;
  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = Object.assign(document.createElement("a"), { href: url, download: `${item.date}_${item.code}_${className(item.classId)}.md` });
  anchor.click();
  URL.revokeObjectURL(url);
  toast("옵시디언용 Markdown 파일을 저장했습니다.");
}

function saveRecord(status) {
  const record = {
    id: `r${Date.now()}`,
    date: $("#recordDate").value,
    classId: $("#recordClass").value,
    teacherId: $("#recordTeacher").value,
    code: $("#progressCode").value.trim().toUpperCase(),
    title: $("#lessonTitle").value.trim(),
    summary: $("#commonSummary").value.trim(),
    notes: $("#studentNotes").value.trim(),
    homework: Number($("#homeworkRate").value || 0),
    wrong: Number($("#wrongRate").value || 0),
    status
  };
  if (!record.date || !record.code || !record.title) { toast("수업일, 진도코드, 수업 주제를 입력하세요."); return false; }
  state.records.push(record);
  persist();
  renderDashboard();
  toast(status === "검토 대기" ? "원장 검토 목록에 보냈습니다." : "임시저장했습니다.");
  return true;
}

function init() {
  const today = new Date();
  $("#todayLabel").textContent = new Intl.DateTimeFormat("ko-KR", { year: "numeric", month: "long", day: "numeric", weekday: "long" }).format(today);
  $("#recordDate").value = today.toISOString().slice(0, 10);
  populateSelects();
  renderDashboard();
  renderRecordCards();
  renderPeople("classes");
  updateSimilarRecords();

  $$(".nav-item").forEach(button => button.addEventListener("click", () => switchView(button.dataset.view)));
  $$('[data-view-jump]').forEach(button => button.addEventListener("click", () => switchView(button.dataset.viewJump)));
  $$('[data-open-compose]').forEach(button => button.addEventListener("click", () => switchView("compose")));
  $("#searchRecords").addEventListener("click", renderRecordCards);
  $("#recordSearch").addEventListener("keydown", event => { if (event.key === "Enter") renderRecordCards(); });
  $("#findSimilar").addEventListener("click", updateSimilarRecords);
  $("#progressCode").addEventListener("input", updateSimilarRecords);
  $("#saveDraft").addEventListener("click", () => saveRecord("임시저장"));
  $("#recordForm").addEventListener("submit", event => { event.preventDefault(); if (saveRecord("검토 대기")) switchView("dashboard"); });
  $$(".people-tab").forEach(button => button.addEventListener("click", () => renderPeople(button.dataset.people)));
  $(".dialog-close").addEventListener("click", () => $("#recordDialog").close());
  $("#recordDialog").addEventListener("click", event => { if (event.target === $("#recordDialog")) $("#recordDialog").close(); });
  $("#globalSearch").addEventListener("keydown", event => { if (event.key === "Enter") { $("#recordSearch").value = event.currentTarget.value; switchView("records"); } });
  $("[data-filter-pending]").addEventListener("click", () => { $("#recordSearch").value = ""; switchView("records"); toast("검토 대기 기록을 먼저 확인하세요."); });
}

init();
