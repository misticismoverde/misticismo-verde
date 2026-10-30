// ═══════════════════════════════════════════════════
// MISTICISMO VERDE — JS COMPARTILHADO
// ═══════════════════════════════════════════════════

// NAV scroll + hamburger
document.addEventListener("DOMContentLoaded", function () {
  var nav = document.getElementById("navbar");
  var hamburger = document.getElementById("hamburger");
  var navLinks = document.getElementById("navLinks");

  if (nav) {
    window.addEventListener("scroll", function () {
      nav.classList.toggle("scrolled", window.scrollY > 50);
    });
  }
  if (hamburger && navLinks) {
    hamburger.addEventListener("click", function () {
      navLinks.classList.toggle("aberto");
    });
    navLinks.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { navLinks.classList.remove("aberto"); });
    });
  }

  // ── SOM ──────────────────────────────────────────────────────
  var sb = document.getElementById("soundBtn");
  var audio = document.getElementById("florestAudio");
  var tocando = false;

  if (sb && audio) {
    function fadeIn() {
      audio.volume = 0;
      var t = setInterval(function () {
        audio.volume = Math.min(audio.volume + 0.025, 0.45);
        if (audio.volume >= 0.45) clearInterval(t);
      }, 80);
    }

    function fadeOut(cb) {
      var t = setInterval(function () {
        audio.volume = Math.max(audio.volume - 0.03, 0);
        if (audio.volume <= 0) {
          clearInterval(t);
          audio.pause();
          audio.currentTime = 0;
          if (cb) cb();
        }
      }, 70);
    }

    sb.addEventListener("click", function () {
      if (!tocando) {
        audio.play().then(function () {
          tocando = true;
          sb.textContent = "🔊";
          fadeIn();
        }).catch(function () {});
      } else {
        fadeOut(function () {
          tocando = false;
          sb.textContent = "🌿";
        });
      }
    });
  }

  // ── AUTOPLAY DO ÁUDIO ──────────────────────────────────────
  document.addEventListener('click', function iniciarAudio() {
    var audioEl = document.getElementById('florestAudio');
    var btn = document.getElementById('soundBtn');
    if (audioEl && audioEl.paused) {
      audioEl.play().then(function() {
        if (btn) btn.textContent = '🔊';
        tocando = true;
        audioEl.volume = 0;
        var t = setInterval(function() {
          audioEl.volume = Math.min(audioEl.volume + 0.025, 0.45);
          if (audioEl.volume >= 0.45) clearInterval(t);
        }, 80);
      }).catch(function(err) {});
    }
    document.removeEventListener('click', iniciarAudio);
  }, { once: true });

  document.addEventListener('scroll', function iniciarAudioScroll() {
    var audioEl = document.getElementById('florestAudio');
    var btn = document.getElementById('soundBtn');
    if (audioEl && audioEl.paused) {
      audioEl.play().then(function() {
        if (btn) btn.textContent = '🔊';
        tocando = true;
        audioEl.volume = 0;
        var t = setInterval(function() {
          audioEl.volume = Math.min(audioEl.volume + 0.025, 0.45);
          if (audioEl.volume >= 0.45) clearInterval(t);
        }, 80);
      }).catch(function(err) {});
    }
    document.removeEventListener('scroll', iniciarAudioScroll);
  }, { once: true });

  // ── ESC FECHA MODAIS ──────────────────────────────────────
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.aberto").forEach(function (m) {
        m.classList.remove("aberto");
      });
      document.body.style.overflow = "";
    }
  });

  // ── FOLHAS ANIMADAS ──────────────────────────────────────
  var canvas = document.createElement("canvas");
  canvas.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:999;";
  document.body.appendChild(canvas);
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  var ctx = canvas.getContext("2d");

  var folhas = [];
  for (var i = 0; i < 6; i++) {
    folhas.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: 14 + Math.random() * 8,
      speedY: 0.3 + Math.random() * 0.4,
      speedX: -0.2 + Math.random() * 0.4,
      rotation: Math.random() * 360,
      rotationSpeed: 0.3 + Math.random() * 1.2,
      opacity: 0.05 + Math.random() * 0.1
    });
  }

  function desenhar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    folhas.forEach(function (f) {
      ctx.save();
      ctx.translate(f.x, f.y);
      ctx.rotate(f.rotation * Math.PI / 180);
      ctx.font = f.size + 'px "Segoe UI Emoji","Apple Color Emoji",sans-serif';
      ctx.globalAlpha = f.opacity;
      ctx.fillText("🍃", 0, 0);
      ctx.restore();
      f.x += f.speedX;
      f.y += f.speedY;
      f.rotation += f.rotationSpeed;
      if (f.y > canvas.height) {
        f.y = -30;
        f.x = Math.random() * canvas.width;
      }
      if (f.x < -50) {
        f.x = canvas.width + 20;
      }
      if (f.x > canvas.width + 50) {
        f.x = -20;
      }
    });
    requestAnimationFrame(desenhar);
  }

  window.addEventListener("resize", function () {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

  desenhar();
});

// ── COPIAR E-MAIL ──────────────────────────────────────────
function copiarEmail() {
  var email = "misticismoverde@gmail.com";
  var el = document.getElementById("emailTexto");
  if (navigator.clipboard) {
    navigator.clipboard.writeText(email).then(function () {
      el.textContent = "✓ Copiado!";
      setTimeout(function () { el.textContent = email; }, 2000);
    });
  } else {
    var tmp = document.createElement("input");
    tmp.value = email;
    document.body.appendChild(tmp);
    tmp.select();
    document.execCommand("copy");
    document.body.removeChild(tmp);
    el.textContent = "✓ Copiado!";
    setTimeout(function () { el.textContent = email; }, 2000);
  }
}