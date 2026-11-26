"""
GUIAS DE CUIDADOS — Misticismo Verde

Gera, a partir de TODAS as plantas da loja (categoria "Plantas Vivas" no painel):
  - fonte/downloads/guia-de-cuidados-misticismo-verde.pdf   (guia completo, fica nos Downloads)
  - fonte/downloads/guias/guia-<id-do-produto>.pdf          (um guia por planta, botão na página dela)

Planta nova no painel entra sozinha. Os cuidados vêm dos mesmos textos do site
("Como usar: passos", "Experiência: itens" e "Cuidados") e dos campos do painel
"Guia: nome científico", "Guia: rega no verão/inverno amazônico" e "Guia: tóxica".
A Jiboia Neon e a Mini Espada têm páginas feitas à mão; os passos delas ficam em MANUAIS, abaixo.

Os PDFs são refeitos automaticamente pelo GitHub (.github/workflows/guias.yml) sempre que um
produto, uma foto de produto ou este gerador muda. Para gerar à mão:
    python3 guia/gerar_guia.py
Precisa de: Python com Pillow e Playwright (Chromium).
"""
import base64, glob, html, io, json, os, re, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS = os.path.join(RAIZ, 'fonte', 'downloads')
COMPLETO = os.path.join(DOWNLOADS, 'guia-de-cuidados-misticismo-verde.pdf')
PASTA_IND = os.path.join(DOWNLOADS, 'guias')
CATEGORIA = 'Plantas Vivas'

# Plantas com página feita à mão: os passos de cuidado ficam aqui (iguais aos da página).
MANUAIS = {
  'jiboianeon': dict(nome='Jiboia Neon', cient="Epipremnum aureum 'Neon'", intencao='Renovação e vitalidade',
       luz='Claridade intensa sem sol do meio-dia; com pouca luz, perde a cor neon', verao='a cada 4 a 6 dias', inverno='a cada 7 a 10 dias',
       porte='Ramos pendentes que crescem sem parar; pode podar à vontade', toxica=True,
       passos=[('Rega', 'Regue só quando o topo da terra estiver seco ao toque. O excesso de água é o erro mais comum e apodrece as raízes. Folhas amarelas e caídas = água demais; folhas murchas e secas = sede.'),
               ('Luz', 'A Neon precisa de mais luz do que a jiboia comum para manter o amarelo-limão: varanda coberta, perto de janela com cortina ou interior muito claro. Evite o sol direto do meio-dia, que queima as folhas.'),
               ('Umidade e ar-condicionado', 'A umidade de Belém é perfeita e não precisa borrifar as folhas. Tolera ar-condicionado, mas não deixe o vento frio bater direto nela.'),
               ('Terra e vaso', 'Substrato leve: terra vegetal com fibra de coco e um pouco de perlita ou areia grossa. Vaso sempre com furo; em vaso pendente, use prato para a água não escorrer. Troque de vaso a cada 1 a 2 anos.'),
               ('Limpeza e poda', 'Passe um pano úmido nas folhas a cada 15 dias. Pode livremente para controlar o tamanho; cada ramo cortado enraíza num copo de água em 2 a 3 semanas.'),
               ('Folhas verde-escuras', 'Se as folhas novas nascerem verde-escuras, é falta de luz: leve para um lugar mais claro (sem sol forte) e a cor neon volta nas próximas folhas.')],
       alerta='Tóxica se mastigada: tem cristais de oxalato de cálcio, que irritam boca e garganta de pessoas, cães e gatos. Em vaso pendente ou prateleira alta, fica fora do alcance.'),
  'miniespada': dict(nome='Espada Mini de São Jorge', cient="Dracaena trifasciata 'Hahnii'", intencao='Proteção',
       luz='Da meia-sombra à luz indireta intensa; evite o sol do meio-dia', verao='a cada 7 a 10 dias', inverno='a cada 10 a 15 dias',
       porte='Roseta compacta, de crescimento lento; vasos de 10 a 15 cm', toxica=True,
       passos=[('Rega — o cuidado mais importante', 'Regue só com a terra completamente seca. No ar úmido de Belém a terra demora a secar, e o risco é regar demais. Por estar num vaso pequeno, ela seca mais rápido que a Espada grande.'),
               ('Época de chuva', 'No inverno amazônico, reduza a rega pela metade e confira a terra antes de cada rega. Não deixe o vaso tomando chuva nem água parada no prato: apodrece a raiz e cria mosquito.'),
               ('Luz', 'Aceita desde pouca luz até sol, mas em Belém o ideal é meia-sombra ou claridade forte sem sol direto do meio-dia, que queima as folhas.'),
               ('Terra e vaso', 'Terra que escoe rápido: 2 partes de terra vegetal para 1 de areia grossa ou perlita. Vaso com furo. Troque a terra a cada 2 anos.'),
               ('Sinais de alerta', 'Folhas amarelas e moles = água demais. Folhas enrugadas e secas = sede. Não precisa borrifar: folha molhada no calor favorece fungos.'),
               ('Multiplicação', 'Separe as mudinhas que nascem ao lado da planta-mãe na hora de trocar de vaso, ou plante pedaços de folha de 5 cm em pé na terra úmida.')],
       alerta='Tóxica se mastigada: contém saponinas, que podem causar vômito e salivação em cães e gatos. Deixe fora do alcance de animais e crianças pequenas.'),
}

e = html.escape
def sem_tags(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))).strip()
def b64(caminho, mime): return f'data:{mime};base64,' + base64.b64encode(open(caminho, 'rb').read()).decode()

def foto(rel):
    """Recorta a faixa de título dos cards e devolve só a planta."""
    from PIL import Image
    im = Image.open(os.path.join(RAIZ, 'fonte', rel.lstrip('/'))).convert('RGB')
    w, h = im.size
    if abs(h / w - 1.25) < 0.02:   # cards 1080x1350 com faixa de título em cima
        im = im.crop((0, round(h * 0.215), w, round(h * 0.915)))
    im.thumbnail((700, 700))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=78); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

def plantas_da_loja():
    lista = []
    for arq in glob.glob(os.path.join(RAIZ, 'conteudo', 'produtos', '*.json')):
        d = json.load(open(arq, encoding='utf-8'))
        if d.get('categoria') != CATEGORIA: continue
        pid = os.path.basename(arq)[:-5]
        p = dict(MANUAIS.get(pid, {}), id=pid, ordem=d.get('ordem') or 999)
        ficha = {i.get('nome', ''): i.get('descricao', '') for i in d.get('experiencia_itens') or []}
        p.setdefault('nome', d.get('titulo_pagina') or d.get('nome', pid))
        p.setdefault('cient', d.get('guia_nome_cientifico') or '')
        p.setdefault('intencao', re.sub(r'^\W+', '', d.get('loja_intencao', '')).strip())
        p.setdefault('luz', ficha.get('Luz', ''))
        p.setdefault('porte', ficha.get('Porte', ''))
        p.setdefault('verao', d.get('guia_rega_verao') or ficha.get('Rega', 'Pelo teste do dedo'))
        p.setdefault('inverno', d.get('guia_rega_inverno') or 'Menos que no verão; confira a terra antes')
        cuid = sem_tags(d.get('cuidados', ''))
        if 'toxica' not in p:
            p['toxica'] = d['guia_toxica'] if 'guia_toxica' in d else ('tóxica' in cuid.lower() and 'sem toxicidade' not in cuid.lower())
        p.setdefault('passos', [(s.get('modo', ''), sem_tags(s.get('descricao', ''))) for s in d.get('ritual_passos') or []])
        p.setdefault('alerta', re.split(r'Os usos espirituais', cuid)[0].strip())
        p['img'] = d.get('imagem') or f'/imagens/produtos/img-produto-{pid}.jpg'
        if not p['passos']:
            print('AVISO: sem passos de cuidado, fora do guia:', pid); continue
        lista.append(p)
    return sorted(lista, key=lambda p: (p['ordem'], p['nome']))

RODAPE = '<footer class="rodape-pg">Misticismo Verde · Guia de cuidados · misticismoverde.com.br</footer>'

def pagina_planta(p, n=None, logo=''):
    ficha = [('Luz', p['luz']), ('Rega no verão amazônico', p['verao']), ('Rega no inverno amazônico', p['inverno']),
             ('Porte', p['porte']), ('Animais e crianças', 'Tóxica se mastigada' if p['toxica'] else 'Não consta como tóxica para cães e gatos (ASPCA)')]
    ficha = [(a, b) for a, b in ficha if b]
    passos = ''.join(f'<div class="passo"><h4>{e(m)}</h4><p>{e(t)}</p></div>' for m, t in p['passos'])
    sobre = f'{n:02d} · {e(p["intencao"])}' if n else f'Guia de cuidados · {e(p["intencao"])}'
    selo = f'<img class="selo" src="{logo}" alt="">' if logo else ''
    alerta = f'<div class="caixa-alerta"><b>{"⚠ Atenção" if p["toxica"] else "ℹ Bom saber"}</b> {e(p["alerta"])}</div>' if p['alerta'] else ''
    return f'''<section class="pg planta">
  <header class="topo-planta"><div><p class="sobre">{sobre}</p><h2>{e(p["nome"])}</h2><p class="cient">{e(p["cient"])}</p></div>{selo}</header>
  <div class="ficha-wrap">
    <img class="foto" src="{foto(p["img"])}" alt="">
    <dl class="ficha">{''.join(f'<div class="{"alerta-ficha" if a == "Animais e crianças" and p["toxica"] else ""}"><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in ficha)}</dl>
  </div>
  <h3>Como cuidar em Belém e região</h3>
  <div class="passos">{passos}</div>
  {alerta}
  {RODAPE}
</section>'''

CLIMA = """<section class="pg">
  <p class="sobre">Antes de tudo</p>
  <h2>O clima de Belém muda o jeito de cuidar</h2>
  <p class="intro">A maioria dos guias de plantas é escrita para o Sul e o Sudeste. Aqui é diferente: faz calor o ano inteiro, o ar é úmido e chove muito. Por isso, em Belém, quase sempre o perigo é <b>água demais</b>, não de menos. Em vez de estações de frio e calor, pense em duas épocas:</p>
  <div class="estacoes">
    <div class="est chuva"><h3>Inverno amazônico</h3><p class="meses">dezembro a maio · chuva mais forte de fevereiro a abril</p>
      <ul><li>Chove quase todo dia e a terra demora para secar.</li><li><b>Regue menos</b> e sempre confira a terra antes.</li><li>Tire os vasos da chuva direta: varanda coberta, não quintal aberto.</li><li>Fique de olho em folhas moles e manchas de fungo.</li></ul></div>
    <div class="est sol"><h3>Verão amazônico</h3><p class="meses">junho a novembro · menos chuva, sol mais forte</p>
      <ul><li>A terra seca mais rápido: as regas ficam mais frequentes.</li><li>O sol das 10h às 15h queima folhas, mesmo de plantas "de sol".</li><li>Boa época para trocar de vaso e fazer mudas.</li><li>Vaso preto ao sol esquenta e pode cozinhar a raiz.</li></ul></div>
  </div>
  <h3>As 6 regras de ouro</h3>
  <ol class="regras">
    <li><b>Faça o teste do dedo.</b> Enfie o dedo ou um palito de churrasco na terra. Saiu úmido? Espere. Saiu seco? Pode regar. Os dias indicados neste guia são só referência.</li>
    <li><b>Vaso sempre com furo.</b> Sem furo, a água fica parada no fundo e a raiz apodrece.</li>
    <li><b>Nada de água parada no pratinho.</b> Esvazie depois de regar: além de apodrecer a raiz, vira criadouro do mosquito da dengue.</li>
    <li><b>Fuja do sol do meio-dia.</b> Perto da linha do Equador, o sol das 10h às 15h é muito forte. Sol da manhã é bem-vindo.</li>
    <li><b>Regue a terra, não as folhas.</b> Regue de manhã, direto na terra. Folha molhada à noite, no calor úmido, favorece fungos.</li>
    <li><b>Ar-condicionado resseca.</b> Deixe a planta longe da saída de ar frio e, de vez em quando, passe um pano úmido nas folhas.</li>
  </ol>
"""
PRIMEIROS = """<section class="pg">
  <p class="sobre">Chegou em casa</p>
  <h2>Os primeiros dias com a sua planta</h2>
  <ul class="lista">
    <li><b>Escolha o lugar e deixe ela quietinha.</b> Leve a planta para o lugar definitivo e evite ficar mudando. Ela precisa de 1 a 2 semanas para se acostumar com a nova luz.</li>
    <li><b>Não troque de vaso logo de cara.</b> Espere pelo menos 2 semanas, a não ser que as raízes já estejam saindo pelo fundo.</li>
    <li><b>Não adube no primeiro mês.</b> A planta já vem com terra adubada; adubo em planta estressada pode queimar a raiz.</li>
    <li><b>Perder uma folha é normal.</b> Uma folha velha amarelando na primeira semana costuma ser só adaptação. Corte rente, com tesoura limpa.</li>
    <li><b>Regue pelo teste do dedo, não pelo calendário.</b></li>
  </ul>
  <h3>Sinais de alerta: o que a planta está dizendo</h3>
  <table class="sinais">
    <tr><th>O que você vê</th><th>Causa mais provável</th><th>O que fazer</th></tr>
    <tr><td>Folhas amarelas e moles, terra sempre molhada</td><td>Água demais</td><td>Espaçar as regas; conferir o furo do vaso; esvaziar o prato</td></tr>
    <tr><td>Base da folha mole, escura ou com cheiro azedo</td><td>Raiz ou caule apodrecendo</td><td>Cortar a parte podre, deixar secar 1 dia e replantar em terra seca</td></tr>
    <tr><td>Folhas murchas e caídas, terra seca</td><td>Sede</td><td>Regar até escorrer pelo furo; ela levanta em algumas horas</td></tr>
    <tr><td>Manchas marrons secas ou "queimadas"</td><td>Sol forte direto</td><td>Mudar para claridade sem sol do meio-dia</td></tr>
    <tr><td>Pontas das folhas secas</td><td>Ar seco (ar-condicionado) ou excesso de adubo</td><td>Afastar do ar frio; suspender o adubo; aparar só a ponta seca</td></tr>
    <tr><td>Folhas novas pequenas, ramos esticados e finos</td><td>Pouca luz</td><td>Levar para um lugar mais claro, sem sol forte</td></tr>
    <tr><td>Algodãozinho branco entre as folhas</td><td>Cochonilha</td><td>Limpar com cotonete com álcool; repetir em 1 semana</td></tr>
    <tr><td>Pontinhos e teias finas no verso da folha</td><td>Ácaros (ambiente seco e fechado)</td><td>Limpar com pano úmido e ventilar o ambiente</td></tr>
  </table>
  <footer class="rodape-pg">Misticismo Verde · Guia de cuidados · misticismoverde.com.br</footer>
</section>

"""
TERRA = """<section class="pg">
  <p class="sobre">Terra e vaso</p>
  <h2>A casa da sua planta</h2>
  <h3>A terra certa para cada planta</h3>
  <div class="duas">
    <div class="cartao"><h4>Folhagens</h4><p class="pq">Jiboia, Planta Flecha, Costela de Adão, Alocasias, palmeiras e outras folhagens</p><p>Terra vegetal misturada com fibra de coco ou casca de arroz carbonizada, para ficar leve e arejada. Na umidade de Belém, terra pura fica pesada e encharca.</p></div>
    <div class="cartao"><h4>Espadas e suculentas</h4><p class="pq">Espada de São Jorge, Mini Espada, cactos</p><p>Terra vegetal misturada com areia grossa (de meio a meio até 2 partes de terra para 1 de areia), para a água escorrer rápido.</p></div>
  </div>
  <h3>Quando e como trocar de vaso</h3>
  <ul class="lista">
    <li><b>Hora de trocar:</b> raízes saindo pelo furo, terra que seca em 1 dia ou planta tombando de tão grande.</li>
    <li><b>Tamanho:</b> o vaso novo deve ter só 2 a 5 cm a mais de diâmetro que o anterior. Vaso grande demais acumula água na terra que a raiz ainda não alcança.</li>
    <li><b>Melhor época:</b> início do verão amazônico (a partir de junho) ou dias sem chuva forte.</li>
  </ul>
  <ol class="regras">
    <li>Regue a planta na véspera: o torrão sai inteiro.</li>
    <li>Coloque uma camada fina de pedrisco ou argila expandida no fundo do vaso novo, se quiser, e um pouco de terra.</li>
    <li>Tire a planta virando o vaso e apertando as laterais. Solte com os dedos as raízes que estiverem enroladas.</li>
    <li>Acomode no vaso novo na mesma altura em que estava, sem enterrar o caule.</li>
    <li>Complete com terra, firme com os dedos e regue até escorrer pelo furo.</li>
    <li>Deixe na sombra clara por 1 semana, sem adubo.</li>
  </ol>
  <h3>Adubo</h3>
  <p>Pouco e com calma: uma adubação leve por mês nas folhagens que estão crescendo, e a cada 2 ou 3 meses nas espadas. Siga sempre a dose da embalagem; na dúvida, use menos. Não adube planta doente, recém-chegada ou recém-transplantada.</p>
  <footer class="rodape-pg">Misticismo Verde · Guia de cuidados · misticismoverde.com.br</footer>
</section>

"""
FINAL = """<section class="pg final">
  <img class="logo" src="@@LOGO@@" alt="">
  <h2>Ficou com alguma dúvida?</h2>
  <p class="sub">Mande uma foto da planta e do lugar onde ela está. A Thai responde e ajuda a descobrir o que ela precisa.</p>
  <div class="contatos"><p><b>WhatsApp</b> (91) 99632-4631</p><p><b>Instagram e TikTok</b> @misticismoverde</p><p><b>Site</b> misticismoverde.com.br</p><p><b>E-mail</b> misticismoverde@gmail.com</p></div>
  <p class="nota">Os significados e intenções citados vêm da tradição popular e espiritual brasileira. Eles convivem com a botânica, mas não são afirmações científicas nem substituem cuidados de saúde. Em caso de ingestão de planta por pessoa ou animal, procure um médico ou veterinário.</p>
  <p class="lema">Mantenha o verde, honre a sabedoria ancestral!</p>
</section>"""

def documento(titulo, corpo):
    fontes = os.path.join(RAIZ, 'guia', 'fontes')
    ff = lambda fam, arq, peso, estilo='normal': f"@font-face{{font-family:'{fam}';src:url({b64(os.path.join(fontes, arq), 'font/woff2')}) format('woff2');font-weight:{peso};font-style:{estilo}}}"
    css_fontes = '\n'.join([ff('Poppins', f'poppins-latin-{w}-normal.woff2', w) for w in (300, 400, 500, 600)] +
                           [ff('Playfair Display', 'playfair-display-latin-500-normal.woff2', 500), ff('Playfair Display', 'playfair-display-latin-600-normal.woff2', 600),
                            ff('Playfair Display', 'playfair-display-latin-500-italic.woff2', 500, 'italic')])
    css = open(os.path.join(RAIZ, 'guia', 'guia.css'), encoding='utf-8').read()
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{e(titulo)}</title><style>{css_fontes}\n{css}</style></head><body>{corpo}</body></html>'

def versao():
    meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
    h = datetime.date.today(); return f'{meses[h.month - 1]} de {h.year}'

def guia_completo(plantas, logo):
    indice = ''.join(f'<li><span>{e(p["nome"])}</span><b>pág. {i + 4}</b></li>' for i, p in enumerate(plantas))
    capa = f'''<section class="pg capa">
  <img class="logo" src="{logo}" alt="Misticismo Verde">
  <p class="sobre">Misticismo Verde</p>
  <h1>Guia de cuidados<br>das plantas</h1>
  <p class="sub">Para a sua planta crescer bonita no calor e na umidade de Belém e da Amazônia</p>
  <ul class="capa-lista"><li>O clima de Belém e as duas estações</li><li>Regras de ouro e sinais de alerta</li><li>Uma página para cada planta da loja</li><li>Terra, vaso e troca de vaso</li></ul>
  <p class="lema">Mantenha o verde, honre a sabedoria ancestral!</p>
  <p class="versao">Thai Terrear · Belém (PA) · {len(plantas)} plantas · versão de {versao()}</p>
</section>'''
    clima = CLIMA + f'  <h3>Plantas deste guia</h3>\n  <ol class="indice">{indice}</ol>\n  {RODAPE}\n</section>\n'
    corpo = capa + clima + PRIMEIROS + ''.join(pagina_planta(p, i + 1) for i, p in enumerate(plantas)) + TERRA + FINAL.replace('@@LOGO@@', logo)
    return documento('Guia de cuidados das plantas — Misticismo Verde', corpo)

def guia_individual(p, logo):
    corpo = pagina_planta(p, logo=logo) + CLIMA + f'  {RODAPE}\n</section>\n' + PRIMEIROS + TERRA + FINAL.replace('@@LOGO@@', logo)
    return documento(f'Guia de cuidados: {p["nome"]} — Misticismo Verde', corpo)

def main():
    from playwright.sync_api import sync_playwright
    plantas = plantas_da_loja()
    from PIL import Image
    im = Image.open(os.path.join(RAIZ, 'fonte', 'imagens', 'geral', 'logo-mv.png')).convert('RGBA'); im.thumbnail((480, 480))
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); logo = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
    os.makedirs(PASTA_IND, exist_ok=True)
    trabalhos = [(COMPLETO, guia_completo(plantas, logo))] + [(os.path.join(PASTA_IND, f'guia-{p["id"]}.pdf'), guia_individual(p, logo)) for p in plantas]
    validos = {os.path.basename(c) for c, _ in trabalhos}
    for velho in glob.glob(os.path.join(PASTA_IND, '*.pdf')):   # planta que saiu da loja
        if os.path.basename(velho) not in validos: os.remove(velho); print('removido:', os.path.basename(velho))
    tmp = os.path.join(RAIZ, 'guia', '_guia.html')
    with sync_playwright() as pw:
        nav = pw.chromium.launch(); pg = nav.new_page()
        for caminho, doc in trabalhos:
            open(tmp, 'w', encoding='utf-8').write(doc)
            pg.goto('file://' + tmp); pg.wait_for_timeout(300)
            pg.pdf(path=caminho, format='A4', print_background=True, margin=dict(top='0', bottom='0', left='0', right='0'))
            print('gerado:', os.path.relpath(caminho, RAIZ), f'({os.path.getsize(caminho) // 1024} KB)')
        nav.close()
    os.remove(tmp)

if __name__ == '__main__':
    main()
