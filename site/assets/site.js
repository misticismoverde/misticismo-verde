// ═══════════════════════════════════════════════════
// MISTICISMO VERDE — JS COMPARTILHADO
// ═══════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", function () {

  // ── MENU (celular) ─────────────────────────────────────
  var btnMenu = document.getElementById("mvMenuBtn");
  var menu = document.getElementById("mvMenu");
  if (btnMenu && menu) {
    btnMenu.addEventListener("click", function () {
      var aberto = menu.classList.toggle("aberto");
      btnMenu.setAttribute("aria-expanded", aberto ? "true" : "false");
    });
  }

  // ── SONS DA FLORESTA: só tocam quando a pessoa aperta o botão ──
  var som = document.getElementById("mvSom");
  var audio = document.getElementById("florestAudio");
  if (som && audio) {
    var rotulo = som.querySelector("span");
    var tocando = false, timer = null;
    function volume(alvo, passo, fim) {
      clearInterval(timer);
      timer = setInterval(function () {
        audio.volume = Math.max(0, Math.min(1, audio.volume + passo));
        if ((passo > 0 && audio.volume >= alvo) || (passo < 0 && audio.volume <= alvo)) {
          clearInterval(timer); if (fim) fim();
        }
      }, 80);
    }
    som.addEventListener("click", function () {
      if (!tocando) {
        audio.volume = 0;
        audio.play().then(function () {
          tocando = true; som.classList.add("tocando");
          som.setAttribute("aria-label", "Desligar sons da floresta");
          if (rotulo) rotulo.textContent = "Desligar sons";
          volume(0.45, 0.025);
        }).catch(function () {});
      } else {
        volume(0, -0.03, function () {
          audio.pause(); tocando = false; som.classList.remove("tocando");
          som.setAttribute("aria-label", "Ligar sons da floresta");
          if (rotulo) rotulo.textContent = "Sons da floresta";
        });
      }
    });
  }

  // ── ESC FECHA JANELAS ─────────────────────────────────
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.aberto").forEach(function (m) { m.classList.remove("aberto"); });
      if (menu) menu.classList.remove("aberto");
      document.body.style.overflow = "";
    }
  });
});

// ── COPIAR E-MAIL (página de contato) ─────────────────────
function copiarEmail() {
  var email = "misticismoverde@gmail.com";
  var el = document.getElementById("emailTexto");
  function feito() { if (el) { el.textContent = "✓ Copiado!"; setTimeout(function () { el.textContent = email; }, 2000); } }
  if (navigator.clipboard) { navigator.clipboard.writeText(email).then(feito); }
  else {
    var tmp = document.createElement("input"); tmp.value = email; document.body.appendChild(tmp);
    tmp.select(); document.execCommand("copy"); document.body.removeChild(tmp); feito();
  }
}
