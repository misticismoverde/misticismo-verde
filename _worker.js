// ═══════════════════════════════════════════════════════
//  MISTICISMO VERDE — Worker com Sitemap Dinâmico
//  Para adicionar uma página nova: inclua uma linha
//  no array PAGINAS abaixo e faça o deploy normalmente.
// ═══════════════════════════════════════════════════════

const DOMINIO = "https://misticismoverde.com.br";

// ── LISTA DE PÁGINAS ────────────────────────────────────
// Adicione novas páginas aqui quando criar conteúdo novo
const PAGINAS = [
  { url: "/",                          prioridade: "1.0", freq: "weekly"  },
  { url: "/biblioteca.html",           prioridade: "0.9", freq: "weekly"  },
  { url: "/produto-limpeza.html",      prioridade: "0.8", freq: "monthly" },
  { url: "/produto-protecao.html",     prioridade: "0.8", freq: "monthly" },
  { url: "/produto-prosperidade.html", prioridade: "0.8", freq: "monthly" },
  { url: "/produto-forca.html",        prioridade: "0.8", freq: "monthly" },
  { url: "/produto-amor.html",         prioridade: "0.8", freq: "monthly" },
  { url: "/produto-muiraquita.html",   prioridade: "0.8", freq: "monthly" },
  { url: "/artigo-muiraquita.html",    prioridade: "0.8", freq: "monthly" },
  { url: "/artigo-absorcao-energia.html", prioridade: "0.8", freq: "monthly" },
  { url: "/produto-coruja.html", prioridade: "0.8", freq: "monthly" },
  { url: "/produto-difusor.html", prioridade: "0.8", freq: "monthly" },


];
// ────────────────────────────────────────────────────────

function gerarSitemap() {
  const hoje = new Date().toISOString().split("T")[0];

  const urls = PAGINAS.map(p => `
  <url>
    <loc>${DOMINIO}${p.url}</loc>
    <lastmod>${hoje}</lastmod>
    <changefreq>${p.freq}</changefreq>
    <priority>${p.prioridade}</priority>
  </url>`).join("");

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}
</urlset>`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Interceptar /sitemap.xml — gerar dinamicamente
    if (url.pathname === "/sitemap.xml") {
      return new Response(gerarSitemap(), {
        headers: {
          "Content-Type": "application/xml; charset=UTF-8",
          "Cache-Control": "public, max-age=3600",
        },
      });
    }

    // Todo o resto — servir os arquivos estáticos normalmente
    return env.ASSETS.fetch(request);
  },
};
