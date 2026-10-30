# Site Misticismo Verde — como funciona

## Editar o site (dia a dia)

1. Entre em **https://app.pagescms.org** e clique em **Sign in with GitHub**.
2. Escolha o repositório **misticismoverde/misticismo-verde**.
3. No menu da esquerda aparecem **Produtos**, **Biblioteca Viva (plantas)** e **Artigos**.
4. Clique no item, altere o que quiser e aperte **Save**.
5. Em cerca de 1 a 2 minutos o Cloudflare publica a mudança sozinho.

### O que dá para fazer pelo painel

| Quero… | Onde |
|---|---|
| Mudar um preço | Produtos → abrir o produto → **Preço (R$)** |
| Marcar uma peça como vendida | Produtos → marcar **Esgotado / vendido** |
| Cadastrar produto novo | Produtos → **Add an entry**. Preencha também os campos "Página:" para montar a página completa |
| Mudar a ordem na loja | Produtos → **Posição na loja** (1 aparece primeiro) |
| Nova planta na Biblioteca | Biblioteca Viva → **Add an entry** |
| Pôr foto numa planta | Abrir a planta → **Foto da planta** |
| Escrever um artigo | Artigos → **Add an entry**. Preencha a **Data** para ele aparecer primeiro |
| Guardar um artigo sem publicar | Marque **Rascunho** |

Fotos podem ser enviadas direto do celular: o site reduz o tamanho automaticamente.

### Cuidados com o texto

- Nos campos "Google: título" e "Google: descrição", diga claramente **o que é** e **onde** (Belém/PA).
- Usos de plantas: escreva como **uso tradicional** ("na medicina tradicional, é usada para…"), nunca como promessa de cura, principalmente em páginas de produto.

## O que NÃO se edita pelo painel

Página inicial, Sobre, Contato, Trocas, Privacidade e as páginas feitas à mão (muiraquitã, coruja, difusor, jiboia, espada e 5 artigos) ficam na pasta `fonte/`. Para mudar algo nelas, peça ajuda.

## Como o site é montado (parte técnica)

- `fonte/` — páginas fixas, imagens, estilos (edite aqui, nunca em `site/`).
- `conteudo/` — produtos, plantas e artigos (o que o painel edita).
- `modelos/produto.html` — modelo das páginas de produto.
- `construir.py` — junta tudo e grava o site pronto em `site/` (pasta publicada; é refeita a cada montagem).

Publicação: Cloudflare Workers (projeto `wild-voice-16a6`), ligado a este repositório. Comando da build: `python3 construir.py`; comando de implantação: `npx wrangler deploy`; a pasta publicada é definida em `wrangler.jsonc` (`site/`).
