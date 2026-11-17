---
name: clipper-gta6
description: Clipper do GTA 6 — transforma lives longas de streamers (YouTube, Twitch ou Kick) em cortes verticais prontos pra postar, com a câmera do streamer em cima, o jogo embaixo, título de gancho, legenda palavra por palavra e a legenda do post com hashtags. Use quando a pessoa disser "monta o clipper do GTA 6", "instala essa skill", "corta essa live", "faz cortes dessa live", "acha as maiores lives de GTA 6 de hoje e corta", ou colar um link de live pedindo cortes.
---

# Clipper do GTA 6

Você (a IA) faz só uma parte do trabalho: **ler a fala da live e escolher os momentos**. Todo o resto — baixar,
escutar, achar a câmera, montar o vídeo e a legenda — é feito pelos scripts desta pasta, no computador da pessoa.

Fale com a pessoa em português simples. Ela não é programadora: diga o que está acontecendo em uma frase, sem jargão.

## Como rodar os comandos

O comando é sempre `clip.py`, dentro da pasta `scripts/` desta skill:

- Mac / Linux: `python3 "<pasta da skill>/scripts/clip.py" COMANDO`
- Windows: `python "<pasta da skill>\scripts\clip.py" COMANDO`

Depois do primeiro `instalar`, o `clip.py` usa sozinho o ambiente próprio dele (`~/clipper-gta6/ambiente`).
Tudo que ele cria fica em `~/clipper-gta6/` (no Windows, `C:\Users\NOME\clipper-gta6\`).

Os passos de escutar e montar demoram (uma live de 4 horas leva uns minutos pra escutar). Rode esses comandos com
tempo limite longo (até 60 min) ou em segundo plano, e avise a pessoa que está rodando.

## 0. "Instala essa skill" / "monta o clipper do GTA 6"

1. Se esta pasta ainda não estiver na pasta de skills, copie a pasta inteira desta skill para
   `~/.claude/skills/clipper-gta6` (Windows: `%USERPROFILE%\.claude\skills\clipper-gta6`). Crie a pasta `skills` se não existir.
2. Rode `clip.py instalar`. Ele confere o Python, cria o ambiente, instala os pacotes, baixa sozinho o ffmpeg (se o
   computador não tiver), o detector de rosto e os modelos de escuta. A pessoa não instala nada na mão.
3. Só o **Python** pode faltar (precisa do 3.10 ou mais novo; o `python3` que vem no Mac é o 3.9):
   - Windows: rode `winget install -e --id Python.Python.3.12 --scope user`, peça pra pessoa fechar e abrir o
     terminal (ou o app do Claude) e continue.
   - Mac: rode `open https://www.python.org/downloads/` e diga: "Abri o site do Python. Clica no botão amarelo
     'Download Python', abre o arquivo e vai em Continuar, Concordar e Instalar. Ele pede a senha do teu Mac. Me
     avisa quando terminar." Depois use o `python3` novo
     (`/Library/Frameworks/Python.framework/Versions/3.*/bin/python3`).
4. Rode `clip.py instalar` de novo até aparecer **TUDO PRONTO**. Diga: "Pronto, o clipper tá instalado. É só me
   mandar o link de uma live ou pedir as maiores lives de GTA 6 de hoje."

## 1. "Acha as maiores lives de GTA 6 de hoje"

Rode `clip.py buscar` (padrão: 7 lives). Mostre a lista para a pessoa (título, canal, duração, views) e pergunte
quais cortar — ou corte as 3 primeiras se ela já pediu pra cortar direto.

## 2. "Corta essa live" — o fluxo completo

Para cada link (YouTube, Twitch ou Kick):

### 2.1 Preparar
`clip.py preparar LINK` (aceita vários links de uma vez). Ele baixa só o áudio, escuta tudo, marca os gritos e os
picos de chat e separa a fala em blocos de 12 minutos em `~/clipper-gta6/trabalho/NOME-DA-LIVE/blocos/`.
Se a live não for em português nem em inglês, passe `--idioma` (ex.: `--idioma es`).

### 2.2 Escolher os momentos (esta é a sua parte)
Leia **um bloco por vez** (`bloco_01.txt`, `bloco_02.txt`…). Para cada bloco, escreva o arquivo
`momentos/bloco_NN.json` (mesmo número do bloco), mesmo que vazio (`[]`).

Cada linha do bloco é `[hh:mm:ss] fala`. As marcas ajudam:
- `[ALTO +12dB]` — o streamer ficou muito mais alto que o normal ali (grito, surto, susto).
- `[CHAT 3.1x]` — o chat do YouTube andou 3 vezes mais rápido que o normal: alguma coisa aconteceu.
Marca sozinha não é momento. Confirme pela fala.

**O que vale um corte** (o que as pessoas compartilham):
- primeira reação a algo do jogo (ver o mapa, um personagem, um gráfico pela primeira vez)
- descoberta absurda ou detalhe que ninguém tinha visto
- surto, grito, raiva, susto
- falha engraçada, bug, morte ridícula
- opinião forte ou polêmica ("isso aqui tá pior que o GTA 5")
- história ou piada que fecha sozinha

**Seja rigoroso. Jogue fora:**
- o que precisa de contexto de antes pra fazer sentido
- o que começa com enrolação ("é…", "então…", "tipo assim", "voltando…", "uh, so yeah")
- leitura de doação, propaganda, conversa sobre a própria live, pausa, tela de carregamento
- fala picada ou que a transcrição não deixa entender

**Nota de 0 a 100.** 90+ = qualquer pessoa para de rolar o feed. 70–89 = bom. Abaixo de 60, nem escreva.
Normalmente um bloco tem de 0 a 3 momentos bons — não invente pra encher.

**Duração:** de 20 a 60 segundos. Comece 1–2 segundos antes da frase ou do grito que prende (nunca no meio de uma
palavra) e termine logo depois da reação/conclusão.

Formato de `momentos/bloco_NN.json`:

```json
[
  {
    "inicio": "01:12:03",
    "fim": "01:12:41",
    "nota": 88,
    "tipo": "primeira reação",
    "titulo": "ELE NÃO ACREDITOU NO TAMANHO DO MAPA",
    "porque": "grita ao ver o mapa inteiro; fecha sozinho sem precisar de contexto",
    "post": "O tamanho do mapa do GTA 6 deixou ele sem palavras 😳 #gta6 #gtavi #gta #cortes #streamer"
  }
]
```

- `titulo`: o gancho que vai escrito no vídeo. Curto (até ~45 letras), em MAIÚSCULAS, na língua da live, sem
  spoiler do final. Use o nome ou apelido do streamer quando ajudar ("CASIMIRO NÃO ACREDITOU…").
- `post`: legenda do post, 1–2 frases + 4 a 6 hashtags (sempre `#gta6`).

### 2.3 Ficar com os melhores
`clip.py escolher NOME-DA-LIVE` (padrão: 3 cortes; `--manter 5` pra mais). Ele junta todos os blocos, ordena pela
nota e tira os que se sobrepõem. Conte pra pessoa: "Achei N momentos possíveis e fiquei com os 3 melhores: …".

### 2.4 Montar os cortes
`clip.py fazer NOME-DA-LIVE`. Ele baixa só os minutos escolhidos, acha a câmera do streamer (a caixinha com o rosto)
e monta o vídeo 1080×1920: câmera em cima, jogo embaixo, título de gancho, legenda palavra por palavra. Se não achar
câmera, usa o jogo inteiro no meio com fundo desfocado.

Saída: `~/clipper-gta6/cortes/NOME-DA-LIVE/corte_01.mp4` + `corte_01.txt` (legenda do post + crédito da live).
Diga onde estão e que é só postar.

## Várias lives de uma vez
Passe todos os links no mesmo `preparar`, leia os blocos de todas e rode `escolher` e `fazer` para cada uma.
7 lives ≈ 21 cortes, um dia inteiro de postagem.

## Problemas comuns
- `clip.py status` mostra em que passo cada live está (dá pra continuar de onde parou; nada é refeito).
- Erro de download: atualize com `clip.py instalar` (ele atualiza o yt-dlp) e tente de novo.
- Live do YouTube "trancada por idade" ou só pra membros: não dá pra baixar sem login — escolha outra live.
- Escolheu um momento ruim: apague-o do `momentos/bloco_NN.json`, rode `escolher` de novo e depois `fazer`.
  Para refazer um corte, apague a pasta `trabalho/NOME/corte_NN/`.

## Respeito aos streamers
Corte só de streamers que permitem cortes (muitos têm canal oficial de cortes e liberam). O `.txt` de cada corte já
traz o crédito com o link da live — mantenha na postagem.
