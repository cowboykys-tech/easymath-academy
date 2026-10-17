(() => {
  const installButtons = [...document.querySelectorAll("[data-pwa-install]")];
  let deferredPrompt = null;
  const standalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

  if (standalone) document.documentElement.classList.add("is-installed-pwa");

  const showInstallButtons = () => installButtons.forEach(button => { button.hidden = false; });
  const hideInstallButtons = () => installButtons.forEach(button => { button.hidden = true; });

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    deferredPrompt = event;
    showInstallButtons();
  });

  installButtons.forEach(button => button.addEventListener("click", async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      hideInstallButtons();
      return;
    }
    if (ios && !standalone) {
      window.alert("iPhone·iPad에서는 Safari의 공유 버튼을 누른 뒤 ‘홈 화면에 추가’를 선택해 주세요.");
    }
  }));

  if (ios && !standalone) showInstallButtons();
  window.addEventListener("appinstalled", hideInstallButtons);

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/app-sw.js", { scope: "/" }).catch(() => undefined);
  }
})();
