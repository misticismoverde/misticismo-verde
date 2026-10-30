"""
MONTAGEM DO SITE MISTICISMO VERDE
=================================
O Cloudflare roda este arquivo a cada alteração salva no painel.
Ele junta as páginas fixas (pasta fonte/) com o conteúdo editável (pasta conteudo/)
e grava o site pronto na pasta site/ (que é a pasta publicada).

Para testar no computador:  python3 construir.py
Não é preciso mexer aqui para editar produtos, plantas ou artigos: use o painel.
"""
import datetime, glob, json, os, re, shutil, sys, unicodedata
from html import escape
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.abspath(__file__))
SITE_DIR, CONTEUDO, SAIDA = (os.path.join(RAIZ, p) for p in ('fonte', 'conteudo', 'site'))
SITE = 'https://misticismoverde.com.br'
WHATS = '5591996324631'
CNPJ = '63.040.689/0001-06'
HOJE = datetime.date.today().isoformat()
AVISOS = []

CAT_PROD = {'sais': 'Sais Rituais', 'amuletos': 'Amuletos', 'plantas': 'Plantas Vivas', 'difusores': 'Difusores'}
CAT_PLANTA = {'protecao': 'Proteção', 'limpeza': 'Limpeza', 'amor': 'Amor', 'prosperidade': 'Prosperidade',
              'cura': 'Cura', 'amazonica': 'Amazônica'}
ROMANOS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
OG_PADRAO = '/imagens/geral/og-misticismo-verde.jpg'


# ───────────────────────── utilidades ─────────────────────────
def t(s): return escape(str(s or ''), quote=False)
def a(s): return escape(str(s or ''), quote=True)

def slug(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def chave(valor, mapa):
    """Aceita a chave interna ('sais') ou o rótulo do painel ('Sais Rituais')."""
    v = str(valor or '').strip()
    if v in mapa: return v
    for k, rot in mapa.items():
        if slug(rot) == slug(v): return k
    return slug(v)

def ref_id(v):
    """Referências do painel podem vir como id, caminho do arquivo ou objeto."""
    if isinstance(v, dict): v = v.get('id') or v.get('path') or v.get('value') or ''
    v = os.path.basename(str(v or ''))
    return slug(re.sub(r'\.json$', '', v))

def lista(v):
    if v is None or v == '': return []
    return v if isinstance(v, list) else [v]

def preco_txt(v):
    try: n = float(str(v).replace('R$', '').replace('.', '').replace(',', '.')) if isinstance(v, str) else float(v)
    except ValueError: return str(v)
    return 'R$ ' + f'{n:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def preco_num(v):
    try: return f'{float(v):.2f}' if not isinstance(v, str) else f'{float(v.replace("R$", "").replace(".", "").replace(",", ".")):.2f}'
    except ValueError: return '0.00'

def img(caminho, prefixo):
    c = str(caminho or '').strip()
    if not c: return ''
    if c.startswith('http'): return c
    c = re.sub(r'^(\.\./)+', '', c)
    c = re.sub(r'^/?(site|fonte)/', '', c)
    return prefixo + c.lstrip('/')

def img_abs(caminho):
    c = img(caminho, '')
    return c if c.startswith('http') else SITE + '/' + c

def whats(msg): return f'https://wa.me/{WHATS}?text={quote(msg)}'

def ler(p): return open(p, encoding='utf-8').read()
def gravar(rel, html):
    p = os.path.join(SAIDA, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(html)

def carregar(pasta):
    itens = []
    for f in sorted(glob.glob(os.path.join(CONTEUDO, pasta, '*.json'))):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except json.JSONDecodeError as e:
            AVISOS.append(f'Arquivo com erro e ignorado: {pasta}/{os.path.basename(f)} ({e})'); continue
        if d.get('rascunho'): continue
        d['_id'] = slug(os.path.splitext(os.path.basename(f))[0])
        itens.append(d)
    return itens

def trocar_el(html, el_id, novo):
    """Troca um elemento (identificado pelo id) do modelo pelo HTML pronto."""
    m = re.search(r'<(\w+)\b[^>]*\bid="%s"[^>]*>' % re.escape(el_id), html)
    if not m: return html
    tag = m.group(1).lower()
    if tag in ('img', 'input', 'br'): return html[:m.start()] + novo + html[m.end():]
    fim = html.find('</%s>' % tag, m.end())
    return html[:m.start()] + novo + html[fim + len(tag) + 3:]

def entre(html, ini, fim, novo):
    i = html.index(ini); j = html.index(fim, i) + len(fim)
    return html[:i] + novo + html[j:]


# ───────────────────────── cabeçalho (Google) ─────────────────────────
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "Misticismo Verde", "url": SITE + "/",
       "logo": SITE + "/imagens/geral/logo-mv.png", "email": "misticismoverde@gmail.com", "taxID": CNPJ,
       "telephone": "+55-91-99632-4631", "founder": {"@type": "Person", "name": "Thai Terrear"},
       "address": {"@type": "PostalAddress", "addressLocality": "Belém", "addressRegion": "PA", "addressCountry": "BR"},
       "sameAs": ["https://instagram.com/misticismoverde", "https://www.tiktok.com/@misticismoverde"]}

def url_limpa(rel): return SITE + '/' if rel == 'index.html' else SITE + '/' + rel[:-5]

def cabecalho(html, rel, m):
    url = url_limpa(rel)
    imagem = img_abs(m.get('img') or OG_PADRAO)
    titulo = m['title'] if 'Misticismo Verde' in m['title'] else m['title'] + ' | Misticismo Verde'
    tipo = m.get('tipo')
    g = []
    if m.get('mig'):
        itens = [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}]
        for i, (nome, alvo) in enumerate(m['mig'], start=2):
            itens.append({"@type": "ListItem", "position": i, "name": nome, "item": (SITE + '/' + alvo) if alvo else url})
        g.append({"@type": "BreadcrumbList", "itemListElement": itens})
    if tipo == 'produto':
        p = m['prod']
        g.append({"@type": "Product", "name": p['nome'], "description": m['desc'], "image": [imagem],
                  "brand": {"@type": "Brand", "name": "Misticismo Verde"}, "url": url,
                  "offers": {"@type": "Offer", "price": preco_num(p.get('preco')), "priceCurrency": "BRL", "url": url,
                             "availability": "https://schema.org/SoldOut" if p.get('esgotado') else "https://schema.org/InStock",
                             "itemCondition": "https://schema.org/NewCondition",
                             "seller": {"@type": "Organization", "name": "Misticismo Verde"}}})
    elif tipo in ('artigo', 'planta'):
        art = {"@type": "Article", "headline": (m.get('h1') or m['title'])[:110], "description": m['desc'],
               "image": [imagem], "inLanguage": "pt-BR", "mainEntityOfPage": url,
               "author": {"@type": "Person", "name": "Thai Terrear", "url": SITE + "/sobre"},
               "publisher": {"@type": "Organization", "name": "Misticismo Verde",
                             "logo": {"@type": "ImageObject", "url": SITE + "/imagens/geral/logo-mv.png"}}}
        if m.get('data'): art["datePublished"] = m['data']
        if tipo == 'planta': art["about"] = {"@type": "Thing", "name": m['h1'], "alternateName": m.get('latin', '')}
        g.append(art)
    bloco = '\n'.join([
        f'<title>{t(titulo)}</title>',
        f'<meta name="description" content="{a(m["desc"])}">',
        f'<link rel="canonical" href="{url}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#050f07">',
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="Misticismo Verde">',
        f'<meta property="og:type" content="{"product" if tipo == "produto" else ("article" if tipo in ("artigo", "planta") else "website")}">',
        f'<meta property="og:title" content="{a(titulo)}">',
        f'<meta property="og:description" content="{a(m["desc"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{imagem}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ] + (['<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + '</script>'] if g else []))
    html = re.sub(r'\s*<title>.*?</title>', '', html, count=1, flags=re.S)
    html = re.sub(r'\s*<meta\s+(name|property)="(description|robots|theme-color|og:[^"]*|twitter:[^"]*)"[^>]*>', '', html)
    html = re.sub(r'\s*<link rel="canonical"[^>]*>', '', html)
    html = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', html, flags=re.S)
    vp = re.search(r'<meta name="viewport"[^>]*>', html)
    return html[:vp.end()] + '\n' + bloco + html[vp.end():]

def resumir(s, n=158):
    s = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', str(s or ''))).strip()
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


# ───────────────────────── casca das páginas novas ─────────────────────────
FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
          '<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">')

def nav(px, ativo):
    itens = [('index.html', 'Início'), ('sobre.html', 'Sobre'), ('loja.html', 'Loja'), ('artigos.html', 'Artigos'), ('biblioteca.html', 'Biblioteca Viva')]
    lis = ''.join(f'<li><a href="{px}{h}"{" class=\"ativo\"" if h == ativo else ""}>{n}</a></li>' for h, n in itens)
    return f'''<nav id="navbar">
  <a href="{px}index.html" class="nav-logo">
    <svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="0.8" opacity="0.5"/><path d="M20 4 C20 4 28 12 28 22 C28 30 20 36 20 36 C20 36 12 30 12 22 C12 12 20 4 20 4Z" fill="none" stroke="currentColor" stroke-width="1"/><path d="M20 36 L20 14" stroke="currentColor" stroke-width="0.8" opacity="0.6"/><path d="M20 22 C16 18 10 20 10 20" stroke="currentColor" stroke-width="0.8" opacity="0.5"/><path d="M20 18 C24 14 30 16 30 16" stroke="currentColor" stroke-width="0.8" opacity="0.5"/></svg>
    Misticismo Verde
  </a>
  <button class="hamburger" id="hamburger" aria-label="Abrir menu"><span></span><span></span><span></span></button>
  <ul class="nav-links" id="navLinks">{lis}<li><a href="{px}contato.html" class="nav-cta">Contato</a></li></ul>
</nav>'''

def rodape_legal(px):
    return (f'<div class="rodape-legal" style="background:#050f07;text-align:center;padding:0 24px 30px;font-family:\'Cormorant Garamond\',Georgia,serif;'
            f'font-size:0.78rem;letter-spacing:0.06em;color:rgba(245,234,216,0.4);position:relative;z-index:2;">Misticismo Verde · CNPJ {CNPJ} · Belém, Pará · '
            f'<a href="{px}trocas-e-devolucoes.html" style="color:rgba(201,168,76,0.7);">Trocas e devoluções</a> · '
            f'<a href="{px}privacidade.html" style="color:rgba(201,168,76,0.7);">Privacidade</a></div>')

def pagina(px, ativo, corpo):
    ano = datetime.date.today().year
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Misticismo Verde</title>
<link rel="icon" type="image/png" href="{px}favicon.png">
{FONTES}
<link rel="stylesheet" href="{px}assets/style.css">
<link rel="stylesheet" href="{px}assets/paginas.css">
</head>
<body>

<button class="sound-btn" id="soundBtn" title="Sons da floresta">🌿</button>
<audio id="florestAudio" loop preload="none" src="{px}assets/floresta.mp3"></audio>

{nav(px, ativo)}

{corpo}

<footer>
  <div class="foot-logo">Misticismo Verde<span>Thai Terrear — Belém, Pará</span></div>
  <p class="foot-copy">© {ano} Misticismo Verde · misticismoverde.com.br</p>
  <a href="#" class="foot-link" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">↑ Voltar ao topo</a>
</footer>
{rodape_legal(px)}

<script src="{px}assets/site.js"></script>
</body>
</html>
'''

def migalhas(px, itens):
    partes = [f'<a href="{px}index.html">Início</a>'] + [f'<a href="{px}{h}">{t(r)}</a>' if h else t(r) for r, h in itens]
    return '<div class="migalhas" role="navigation" aria-label="Você está em">' + '<span>›</span>'.join(partes) + '</div>'

def cartoes(itens):
    return '<div class="relacionadas">' + ''.join(f'<a href="{h}"><b>{t(n)}</b><i>{t(s)}</i></a>' for h, n, s in itens) + '</div>'


# ───────────────────────── PRODUTOS ─────────────────────────
def montar_produtos(produtos):
    modelo = ler(os.path.join(RAIZ, 'modelos', 'produto.html'))
    por_id = {p['_id']: p for p in produtos}
    for p in produtos:
        p['_cat'] = chave(p.get('categoria'), CAT_PROD)
        p['_href'] = f'produtos/produto-{p["_id"]}.html'
        p['_preco'] = preco_txt(p.get('preco'))
        p['_img'] = p.get('imagem') or OG_PADRAO
        if not p.get('imagem'): AVISOS.append(f'Produto sem foto: {p.get("nome")}')
    produtos.sort(key=lambda p: (p.get('ordem') or 999, p.get('nome', '')))

    for p in produtos:
        rel = p['_href']
        meta = dict(title=p.get('seo_titulo') or p.get('nome', ''), desc=p.get('seo_descricao') or resumir(p.get('loja_resumo') or p.get('introducao')),
                    img=p['_img'], tipo='produto', prod=dict(nome=p.get('nome'), preco=p.get('preco'), esgotado=p.get('esgotado')),
                    mig=[('Loja', 'loja'), (p.get('nome', ''), None)])
        if p.get('pagina_propria'):
            caminho = os.path.join(SAIDA, rel)
            if not os.path.exists(caminho):
                AVISOS.append(f'"{p.get("nome")}" está marcado como página própria, mas {rel} não existe na pasta fonte/. Desmarque a opção para usar o modelo.')
                continue
            h = ler(caminho)
            h = re.sub(r'(<span data-mv="preco">)(.*?)(</span>)', lambda m: m.group(1) + p['_preco'] + m.group(3), h)
            gravar(rel, cabecalho(h, rel, meta))
            continue
        px = '../'
        nome_pg = p.get('titulo_pagina') or p.get('nome', '')
        wa = whats(f'Olá Thais! Gostaria de adquirir o {nome_pg}.')
        els = {
            'heroTitulo': f'<h1 class="hero-titulo" id="heroTitulo">{t(nome_pg)}</h1>',
            'heroEnergia': f'<p class="hero-energia" id="heroEnergia">{t(p.get("energia"))}</p>',
            'heroIntro': f'<p class="hero-intro" id="heroIntro">{t(p.get("introducao"))}</p>',
            'prodImg': f'<img class="prod-img" id="prodImg" src="{a(img(p["_img"], px))}" alt="{a(nome_pg)}">',
            'preco': f'<p class="preco" id="preco">{t(p["_preco"])}</p>',
            'precoDet': f'<p class="preco-det" id="precoDet">{t(p.get("detalhes"))}</p>',
            'btnHero': f'<a class="btn-comprar" id="btnHero" href="{a(wa)}" target="_blank" rel="noopener">💬 Comprar pelo WhatsApp</a>',
            'btnCta': f'<a class="btn-comprar" id="btnCta" href="{a(wa)}" target="_blank" rel="noopener">💬 Comprar pelo WhatsApp</a>',
            'pqTitulo': f'<h2 class="s-titulo" id="pqTitulo">{t(p.get("para_quem_titulo"))}</h2>',
            'pqTexto': f'<p id="pqTexto">{t(p.get("para_quem_texto"))}</p>',
            'pqLista': '<ul class="id-lista" id="pqLista">' + ''.join(f'<li>{t(x)}</li>' for x in lista(p.get('para_quem_lista'))) + '</ul>',
            'atTitulo': f'<h2 class="s-titulo" id="atTitulo">{t(p.get("atuacao_titulo"))}</h2>',
            'atCorpo': f'<div class="s-corpo" id="atCorpo">{p.get("atuacao_texto") or ""}</div>',
            'rTitulo': f'<h2 class="s-titulo" id="rTitulo">{t(p.get("ritual_titulo"))}</h2>',
            'rIntro': f'<p style="font-size:.97rem;line-height:1.85;color:rgba(245,234,216,.6);font-weight:300;font-style:italic;margin-bottom:30px" id="rIntro">{t(p.get("ritual_introducao"))}</p>',
            'rSteps': '<div id="rSteps">' + ''.join(
                f'<div class="ritual-step"><div class="r-num">{ROMANOS[i] if i < 10 else i + 1}</div><div><span class="r-modo">{t(s.get("modo"))}</span><p class="r-desc">{t(s.get("descricao"))}</p></div></div>'
                for i, s in enumerate(lista(p.get('ritual_passos')))) + '</div>',
            'intFrase': f'<div class="int-frase" id="intFrase">"{t(p.get("intencao_frase"))}"</div>',
            'expTitulo': f'<h2 class="s-titulo" id="expTitulo">{t(p.get("experiencia_titulo"))}</h2>',
            'expTexto': f'<p style="font-size:.97rem;line-height:1.85;color:rgba(245,234,216,.6);font-weight:300;margin-bottom:4px" id="expTexto">{t(p.get("experiencia_texto"))}</p>',
            'expGrid': '<div class="exp-grid" id="expGrid">' + ''.join(
                f'<div class="exp-item"><span class="exp-ico">{t(e.get("icone"))}</span><span class="exp-nome">{t(e.get("nome"))}</span><p class="exp-desc">{t(e.get("descricao"))}</p></div>'
                for e in lista(p.get('experiencia_itens'))) + '</div>',
            'cuidBox': f'<div class="cuid-box" id="cuidBox">{p.get("cuidados") or ""}</div>',
            'ancTitulo': f'<h2 class="s-titulo" id="ancTitulo">{t(p.get("conexao_titulo"))}</h2>',
            'ancCit': f'<div class="anc-cit" id="ancCit">{t(p.get("conexao_citacao"))}</div>',
            'ancTexto': f'<p class="s-corpo" id="ancTexto">{t(p.get("conexao_texto"))}</p>',
            'ctaTitulo': f'<h2 class="cta-titulo" id="ctaTitulo">{t(p.get("chamada_titulo"))}</h2>',
            'ctaTexto': f'<p class="cta-txt" id="ctaTexto">{t(p.get("chamada_texto"))}</p>',
        }
        outros = [q for q in produtos if q is not p and q['_cat'] == p['_cat']] + [q for q in produtos if q is not p and q['_cat'] != p['_cat']]
        outros = [q for q in outros if not q.get('esgotado')][:4]
        els['outrosGrid'] = '<div class="outros-grid" id="outrosGrid">' + ''.join(
            f'<a class="o-card" href="../{q["_href"]}"><img src="{a(img(q["_img"], px))}" alt="{a(q.get("nome"))}" class="o-img" loading="lazy"><div class="o-nome">{t(q.get("titulo_pagina") or q.get("nome"))}</div><div class="o-energia">{t(re.sub(r"^[^A-Za-zÀ-ÿ]+", "", q.get("loja_intencao") or ""))}</div></a>'
            for q in outros) + '</div>'
        if p.get('esgotado'):
            enc = whats(f'Olá Thais! Vi a peça {nome_pg}, que já foi vendida. Gostaria de encomendar uma parecida.')
            off = 'opacity:0.5;cursor:default;pointer-events:none;background:rgba(200,50,50,0.1);border-color:rgba(200,50,50,0.3);color:#ff6b6b;'
            els['btnHero'] = f'<a class="btn-comprar" id="btnHero" style="{off}">💬 Peça vendida</a>'
            els['btnCta'] = f'<a class="btn-comprar" id="btnCta" href="{a(enc)}" target="_blank" rel="noopener">💬 Encomendar uma peça parecida</a>'
            els['preco'] = f'<p class="preco" style="text-decoration:line-through;color:#ff6b6b;" id="preco">{t(p["_preco"])}</p>'
            els['precoDet'] = '<p class="preco-det" id="precoDet" style="color:#ff6b6b;">⚠️ Indisponível · Peça única vendida</p>'
        h = modelo
        for k, v in els.items(): h = trocar_el(h, k, v)
        if p.get('esgotado'):
            h = h.replace('<!--AVISO-ESGOTADO--><div class="hero">', '''<div style="background:rgba(200,50,50,0.08);border:1px solid rgba(200,50,50,0.2);padding:14px 24px;text-align:center;position:relative;z-index:2;margin:100px 60px 0 60px;border-radius:8px;">
  <p style="color:#ff6b6b;font-family:'Cinzel Decorative',serif;font-size:0.75rem;letter-spacing:0.15em;margin:0;">⚠️ PEÇA ÚNICA — JÁ FOI VENDIDA</p>
  <p style="color:rgba(255,107,107,0.6);font-size:0.85rem;font-style:italic;margin:4px 0 0;">Esta peça foi vendida, mas sua história e energia permanecem aqui.</p>
</div>
<div class="hero" style="padding-top:20px;">''')
        h = h.replace('<!--AVISO-ESGOTADO-->', '')
        h = h.replace('/*P*/{}/*FIM-P*/', json.dumps({'titulo': nome_pg, 'img': img(p['_img'], px)}, ensure_ascii=False))
        h = h.replace('Falar com Thais</a>', 'Tirar uma dúvida</a>')
        h = re.sub(r'© \d{4} Misticismo Verde', f'© {datetime.date.today().year} Misticismo Verde', h)
        gravar(rel, cabecalho(h, rel, meta))

    # loja
    js = []
    grade = ''
    for p in produtos:
        js.append({'id': p['_id'], 'categoria': p['_cat'], 'href': p['_href'], 'img': img(p['_img'], ''), 'badge': p.get('loja_selo', ''),
                   'intencao': p.get('loja_intencao', ''), 'nome': p.get('nome', ''), 'desc': p.get('loja_resumo', ''), 'preco': p['_preco'],
                   'tag': p.get('loja_intencao') or '✦', 'esgotado': bool(p.get('esgotado'))})
    js.append({'id': 'muiraquita-artigo', 'categoria': 'amuletos', 'href': 'artigos/artigo-muiraquita.html', 'img': 'imagens/geral/img-muiraquita-final.jpg',
               'badge': '📖 Leia mais', 'intencao': '🐸 Ancestralidade', 'nome': 'Quer saber mais sobre o Muiraquitã?',
               'desc': 'Leia o artigo completo sobre a lenda das Icamiabas e a história do amuleto.', 'preco': 'Ler artigo →', 'tag': ''})
    for p in js:
        esg = p.get('esgotado')
        btn = 'Ler' if p['tag'] == '' else ('Ver detalhes' if esg else 'Ver Detalhes')
        preco = p['preco'] + (' <span class="prod-preco-indisponivel">· Indisponível</span>' if esg else '')
        grade += (f'<a class="produto-card {"esgotado" if esg else ""}" href="{p["href"]}" data-categoria="{p["categoria"]}">'
                  f'<div class="prod-img-wrap"><img src="{a(p["img"])}" class="prod-img" alt="{a(p["nome"])}" loading="lazy"><div class="prod-overlay"></div>'
                  f'<span class="prod-badge">{"ESGOTADO" if esg else t(p["badge"])}</span></div><div class="prod-info"><div class="prod-intencao">{t(p["intencao"])}</div>'
                  f'<h3 class="prod-nome">{t(p["nome"])}</h3><p class="prod-desc">{t(p["desc"])}</p><div class="prod-footer"><span class="prod-preco">{preco}</span>'
                  f'<span class="prod-btn">{btn}</span></div></div></a>')
    grade += '<div class="prod-em-breve" data-categoria="todos"><div style="text-align:center;padding:36px;"><div style="font-size:1.8rem;margin-bottom:14px;opacity:0.3;">✦</div><p style="font-family:\'Cinzel Decorative\',serif;font-size:0.78rem;color:rgba(201,168,76,0.4);letter-spacing:0.1em;line-height:1.7;">Novos rituais<br>em breve</p></div></div>'
    h = ler(os.path.join(SAIDA, 'loja.html'))
    h = h.replace('/*PRODUTOS*/[]/*FIM-PRODUTOS*/', json.dumps(js, ensure_ascii=False))
    h = h.replace('<!--GRADE-->', grade)
    for c in ['todos'] + list(CAT_PROD):
        n = len(js) if c == 'todos' else len([p for p in js if p['categoria'] == c])
        h = re.sub(r'(id="cnt-%s">)\d*(<)' % c, r'\g<1>%d\2' % n, h)
    gravar('loja.html', h)
    return por_id


# ───────────────────────── PLANTAS ─────────────────────────
AVISO_PLANTA = ('As informações desta ficha descrevem usos tradicionais, populares e espirituais da planta. '
                'Não são indicações médicas e não substituem a orientação de um profissional de saúde.')

def montar_plantas(plantas, produtos):
    for p in plantas:
        p['_cats'] = [chave(c, CAT_PLANTA) for c in lista(p.get('categorias'))] or ['cura']
        p['_prod'] = ref_id(p.get('produto_sugerido'))
        if p['_prod'] and p['_prod'] not in produtos:
            AVISOS.append(f'Planta {p.get("nome")}: produto sugerido "{p["_prod"]}" não existe; sugestão ignorada.'); p['_prod'] = ''
    plantas.sort(key=lambda p: slug(p.get('nome', '')))
    for p in plantas:
        px = '../'
        cats = p['_cats']
        foto = f'<img class="art-capa" src="{a(img(p["foto"], px))}" alt="{a(p.get("nome"))} ({a(p.get("nome_cientifico"))})" loading="eager">' if p.get('foto') else ''
        ciencia = f'<section class="pl-sec"><h2><span>🔬</span> O que a ciência diz</h2>{p["o_que_a_ciencia_diz"]}</section>' if p.get('o_que_a_ciencia_diz') else ''
        if ciencia and not ciencia.count('<p'):
            ciencia = ciencia.replace('</h2>', '</h2><p>', 1).replace('</section>', '</p></section>')
        sug = ''
        if p['_prod']:
            q = produtos[p['_prod']]
            sug = (f'<section class="pl-sec"><h2><span>🌿</span> Para acompanhar este ritual</h2><div class="sugestao"><div><strong>{t(q.get("nome"))}</strong>'
                   f'<span>{t(p.get("produto_sugerido_texto"))}</span></div><a href="../{q["_href"]}" class="btn-whats" style="padding:9px 18px">Ver produto</a></div></section>')
        rel = [q for q in plantas if q is not p and q['_cats'][0] == cats[0]]
        rel += [q for q in plantas if q is not p and q not in rel and set(q['_cats']) & set(cats)]
        corpo = f'''<main class="pg-wrap">
  {migalhas(px, [("Biblioteca Viva", "biblioteca.html"), (p.get("nome"), None)])}
  <article>
    <header class="pl-topo">
      <span class="pl-ico" aria-hidden="true">{t(p.get("icone") or "🌿")}</span>
      <h1 class="pl-nome">{t(p.get("nome"))}</h1>
      <p class="pl-latin">{t(p.get("nome_cientifico"))}</p>
      <div class="pl-tags">{"".join(f'<span class="pl-tag">{CAT_PLANTA.get(c, c)}</span>' for c in cats)}</div>
      <p class="pl-ess">{t(p.get("essencia"))}</p>
    </header>
    {foto}
    <section class="pl-sec"><h2><span>🌱</span> Identificação</h2>
      <table class="pl-ident">
        <tr><th>Nome popular</th><td>{t(p.get("nome"))}</td></tr>
        <tr><th>Nome científico</th><td><em>{t(p.get("nome_cientifico"))}</em></td></tr>
        <tr><th>Intenções na tradição</th><td>{", ".join(CAT_PLANTA.get(c, c) for c in cats)}</td></tr>
      </table>
    </section>
    <section class="pl-sec"><h2><span>✨</span> Essência espiritual</h2><p>{t(p.get("essencia_completa"))}</p></section>
    {ciencia}
    <section class="pl-sec"><h2><span>🔮</span> Usos na medicina tradicional e na espiritualidade</h2><p>Na medicina tradicional, popular e indígena, e nas práticas espirituais, a planta é associada a:</p><ul>{"".join(f"<li>{t(u)}</li>" for u in lista(p.get("usos")))}</ul></section>
    <section class="pl-sec"><h2><span>🕯️</span> Como usar</h2>{"".join(f'<h3>{t(m.get("modo"))}</h3><p>{t(m.get("descricao"))}</p>' for m in lista(p.get("modos_de_uso")))}</section>
    <section class="pl-sec"><h2><span>🌙</span> Ritual simples</h2><div class="caixa-ritual"><p>{t(p.get("ritual"))}</p></div></section>
    <section class="pl-sec"><h2><span>⚠️</span> Cuidados</h2><div class="caixa-cuidado"><p>{t(p.get("cuidados"))}</p><p style="margin:10px 0 0;font-size:0.92rem;opacity:0.85">{t(AVISO_PLANTA)}</p></div></section>
    <section class="pl-sec"><h2><span>🌿</span> Conexão ancestral</h2><p>{t(p.get("conexao_ancestral"))}</p></section>
    <section class="pl-sec"><h2><span>🧿</span> Intenção guiada</h2><div class="caixa-intencao">“{t(p.get("intencao"))}”</div></section>
    {sug}
    <div class="acoes">
      <a href="{a(whats(f'Olá Thais! Estou estudando {p.get("nome")} na Biblioteca Viva e gostaria de conversar!'))}" class="btn-whats" target="_blank" rel="noopener">💬 Conversar sobre esta planta</a>
      <a href="../biblioteca.html" class="btn-sec-out">← Voltar à Biblioteca</a>
    </div>
  </article>
  <section class="pl-sec" style="margin-top:56px"><h2><span>✦</span> Outras plantas da Biblioteca</h2>{cartoes([(q["_id"] + ".html", q.get("nome"), q.get("nome_cientifico")) for q in rel[:6]])}</section>
</main>'''
        rel_path = f'plantas/{p["_id"]}.html'
        meta = dict(title=p.get('seo_titulo') or f'{p.get("nome")} ({p.get("nome_cientifico")}): usos, banho e cuidados',
                    desc=p.get('seo_descricao') or resumir(f'{p.get("nome")} ({p.get("nome_cientifico")}): {p.get("essencia")}'),
                    img=p.get('foto') or OG_PADRAO, tipo='planta', h1=p.get('nome'), latin=p.get('nome_cientifico'),
                    mig=[('Biblioteca Viva', 'biblioteca'), (p.get('nome'), None)])
        gravar(rel_path, cabecalho(pagina(px, 'biblioteca.html', corpo), rel_path, meta))

    # biblioteca: dados da página interativa + índice com links
    js = []
    for p in plantas:
        d = {'id': p['_id'], 'ico': p.get('icone') or '🌿', 'nome': p.get('nome', ''), 'latin': p.get('nome_cientifico', ''),
             'tags': p['_cats'], 'cats': p['_cats'], 'ess': p.get('essencia', ''), 'essComp': p.get('essencia_completa', ''),
             'usos': lista(p.get('usos')), 'modos': [{'m': m.get('modo', ''), 'd': m.get('descricao', '')} for m in lista(p.get('modos_de_uso'))] or [{'m': '', 'd': ''}],
             'ritual': p.get('ritual', ''), 'cuid': p.get('cuidados', ''), 'anc': p.get('conexao_ancestral', ''), 'int': p.get('intencao', '')}
        if p['_prod']:
            q = produtos[p['_prod']]
            d['prod'] = {'n': q.get('nome', ''), 'd': p.get('produto_sugerido_texto', ''), 'l': q['_href']}
        js.append(d)
    h = ler(os.path.join(SAIDA, 'biblioteca.html'))
    h = h.replace('/*PLANTAS*/[]/*FIM-PLANTAS*/', json.dumps(js, ensure_ascii=False).replace('</', '<\\/'))
    itens = '\n'.join(f'    <li><a href="plantas/{p["_id"]}.html">{t(p.get("nome"))}</a> <em>{t(p.get("nome_cientifico"))}</em></li>' for p in plantas)
    h = h.replace('<!--INDICE-PLANTAS-->', f'''<section class="indice-plantas" id="indice">
  <h2>Índice da Biblioteca Viva</h2>
  <p>Todas as {len(plantas)} plantas, em ordem alfabética. Cada uma tem sua ficha completa.</p>
  <ul>
{itens}
  </ul>
</section>''')
    h = re.sub(r'Fichas de \d+ plantas', f'Fichas de {len(plantas)} plantas', h)
    gravar('biblioteca.html', h)
    ini = ler(os.path.join(SAIDA, 'index.html'))
    gravar('index.html', re.sub(r'Biblioteca Viva com \d+ plantas', f'Biblioteca Viva com {len(plantas)} plantas', ini))
    return {p['_id']: p for p in plantas}


# ───────────────────────── ARTIGOS ─────────────────────────
FIXOS = [('artigo-muiraquita', 'Muiraquitã: a lenda viva da Amazônia'),
         ('artigo-absorcao-energia', 'Como reconhecer sinais de absorção energética'),
         ('artigo-tracos-invisivel', 'Traços do Invisível: os sete grafismos autorais'),
         ('artigo-jiboia-neon', 'Jiboia Neon: a planta que renova o lar')]

def data_br(iso):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    try:
        d = datetime.date.fromisoformat(str(iso)[:10]); return f'{d.day} de {meses[d.month - 1]} de {d.year}'
    except ValueError: return ''

def montar_artigos(artigos, produtos, plantas):
    com_data = sorted([x for x in artigos if x.get('data')], key=lambda x: str(x['data']), reverse=True)
    sem_data = sorted([x for x in artigos if not x.get('data')], key=lambda x: x.get('ordem') or 999)
    artigos[:] = com_data + sem_data
    for x in artigos:
        x['_slug'] = x['_id'] if x['_id'].startswith('artigo-') else 'artigo-' + x['_id']
    for x in artigos:
        px = '../'
        data = data_br(x.get('data'))
        meta_txt = ' &nbsp;·&nbsp; '.join(filter(None, ['Por Thai Terrear', data, f'{x.get("tempo_leitura")} minutos' if x.get('tempo_leitura') else '', t(x.get('temas'))]))
        prods = [produtos[i] for i in map(ref_id, lista(x.get('produtos_relacionados'))) if i in produtos]
        plts = [plantas[i] for i in map(ref_id, lista(x.get('plantas_relacionadas'))) if i in plantas]
        links = ''
        if prods: links += '<section class="pl-sec"><h2>✦ Produtos citados</h2>' + cartoes([('../' + q['_href'], q.get('nome'), q['_preco']) for q in prods]) + '</section>'
        if plts: links += '<section class="pl-sec"><h2>✦ Na Biblioteca Viva</h2>' + cartoes([(f'../plantas/{q["_id"]}.html', q.get('nome'), q.get('nome_cientifico')) for q in plts]) + '</section>'
        outros = [(y['_slug'] + '.html', y.get('titulo'), 'Artigo') for y in artigos if y is not x][:2] + [(s + '.html', n, 'Artigo') for s, n in FIXOS[:2]]
        links += '<section class="pl-sec"><h2>✦ Leia também</h2>' + cartoes(outros) + '</section>'
        capa = f'<img class="art-capa" src="{a(img(x["imagem"], px))}" alt="{a(x.get("titulo"))}" loading="eager">' if x.get('imagem') else ''
        nota = f'\n    <p class="nota">{t(x["nota"])}</p>' if x.get('nota') else ''
        corpo = f'''<main class="pg-wrap">
  {migalhas(px, [("Artigos", "artigos.html"), (x.get("titulo"), None)])}
  <article>
    <span class="art-tag">{t(x.get("categoria"))} · Misticismo Verde</span>
    <h1 class="art-titulo">{t(x.get("titulo"))}</h1>
    <p class="art-meta">{meta_txt}</p>
    {capa}
    <div class="art-corpo">{x.get("corpo") or ""}
    </div>{nota}
    <div class="assinatura">Thai Terrear<span>Misticismo Verde — Belém, Pará</span></div>
    <div class="acoes">
      <a href="{a(whats(f'Olá Thai! Li o artigo "{x.get("titulo")}" e gostaria de conversar!'))}" class="btn-whats" target="_blank" rel="noopener">💬 Falar com Thai</a>
      <a href="../artigos.html" class="btn-sec-out">← Todos os artigos</a>
    </div>
  </article>
  <div style="margin-top:56px">{links}</div>
</main>'''
        rel = f'artigos/{x["_slug"]}.html'
        meta = dict(title=x.get('seo_titulo') or x.get('titulo', ''), desc=x.get('seo_descricao') or resumir(x.get('resumo') or x.get('corpo')),
                    img=x.get('imagem') or OG_PADRAO, tipo='artigo', h1=x.get('titulo'), data=str(x.get('data') or '')[:10],
                    mig=[('Artigos', 'artigos'), (x.get('titulo', ''), None)])
        gravar(rel, cabecalho(pagina(px, 'artigos.html', corpo), rel, meta))
    cards = ''
    for x in artigos:
        cards += f'''
  <a class="artigo" href="artigos/{x["_slug"]}.html">
    <img src="{a(img(x.get("imagem") or OG_PADRAO, ""))}" class="artigo-img" alt="{a(x.get("titulo"))}" loading="lazy" decoding="async">
    <div class="artigo-body">
      <span class="artigo-tag">{t(x.get("categoria"))}</span>
      <h3 class="artigo-titulo">{t(x.get("titulo"))}</h3>
      <p class="artigo-resumo">{t(x.get("resumo"))}</p>
      <span class="leia-mais">Ler artigo →</span>
    </div>
    <div class="artigo-foot"><span>{x.get("tempo_leitura") or 5} min</span><span>{t(x.get("palavras_chave"))}</span></div>
  </a>
'''
    h = ler(os.path.join(SAIDA, 'artigos.html'))
    gravar('artigos.html', h.replace('<!--ARTIGOS-PAINEL-->', cards))


# ───────────────────────── sitemap e imagens ─────────────────────────
def sitemap():
    pags = sorted(os.path.relpath(f, SAIDA).replace(os.sep, '/') for f in glob.glob(os.path.join(SAIDA, '**', '*.html'), recursive=True))
    def prio(p):
        if p == 'index.html': return '1.0'
        if p in ('privacidade.html', 'trocas-e-devolucoes.html'): return '0.3'
        if '/' not in p: return '0.9'
        return '0.8' if p.startswith('produtos/') else '0.7'
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in sorted(pags, key=lambda p: (-float(prio(p)), p)):
        linhas.append(f'  <url><loc>{url_limpa(p)}</loc><lastmod>{HOJE}</lastmod><priority>{prio(p)}</priority></url>')
    open(os.path.join(SAIDA, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(linhas + ['</urlset>']) + '\n')
    return len(pags)

def otimizar_imagens():
    """Fotos enviadas pelo painel costumam vir enormes do celular: aqui elas são reduzidas."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        AVISOS.append('Pillow não instalado: imagens não foram otimizadas.'); return 0
    n = 0
    for f in glob.glob(os.path.join(SAIDA, 'imagens', '**', '*'), recursive=True):
        ext = f.lower().rsplit('.', 1)[-1]
        if ext not in ('jpg', 'jpeg', 'png', 'webp') or os.path.getsize(f) < 450_000: continue
        try:
            im = ImageOps.exif_transpose(Image.open(f))
            im.thumbnail((1400, 1400), Image.LANCZOS)
            if ext in ('jpg', 'jpeg'): im.convert('RGB').save(f, 'JPEG', quality=80, optimize=True, progressive=True)
            elif ext == 'png': im.save(f, optimize=True)
            else: im.save(f, quality=80)
            n += 1
        except Exception as e:
            AVISOS.append(f'Não consegui otimizar {os.path.relpath(f, SAIDA)}: {e}')
    return n


def main():
    if os.path.exists(SAIDA): shutil.rmtree(SAIDA)
    shutil.copytree(SITE_DIR, SAIDA)
    produtos = montar_produtos(carregar('produtos'))
    plantas = montar_plantas(carregar('plantas'), produtos)
    artigos = carregar('artigos')
    montar_artigos(artigos, produtos, plantas)
    n_img = otimizar_imagens()
    n = sitemap()
    print(f'Site montado: {n} páginas ({len(produtos)} produtos, {len(plantas)} plantas, {len(artigos)} artigos do painel). Imagens otimizadas: {n_img}.')
    for av in AVISOS: print('AVISO:', av)

if __name__ == '__main__':
    main()
