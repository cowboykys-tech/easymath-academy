const form = document.querySelector("#ownerLoginForm");
const message = document.querySelector("#loginMessage");

async function checkSession() {
  const response = await fetch("/api/owner/session", { cache: "no-store" });
  const data = await response.json();
  if (!data.configured) {
    message.textContent = "원장 계정 설정이 필요합니다. 설치 프로그램에서 비밀번호를 먼저 등록해 주세요.";
    form.querySelector("button").disabled = true;
  } else if (data.authenticated) {
    window.location.replace("/");
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  message.textContent = "";
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch("/api/owner/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.querySelector("#ownerUsername").value.trim(),
        password: document.querySelector("#ownerPassword").value
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "로그인하지 못했습니다.");
    window.location.replace(data.redirect || "/");
  } catch (error) {
    message.textContent = error.message;
    document.querySelector("#ownerPassword").select();
  } finally {
    button.disabled = false;
  }
});

checkSession().catch(() => { message.textContent = "서버에 연결하지 못했습니다."; });
