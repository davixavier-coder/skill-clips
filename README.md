# Clipper do GTA 6

Uma skill grátis pro Claude Code que transforma lives longas de streamers em cortes verticais prontos pra postar.

Você manda o link de uma live (YouTube, Twitch ou Kick), ou pede as maiores lives de GTA 6 do dia, e recebe:

- o corte vertical (1080×1920): câmera do streamer em cima, jogo embaixo
- título de gancho e legenda palavra por palavra
- um `.txt` com a legenda do post, as hashtags e o crédito da live

## O que ela faz, em 4 passos

1. **Baixa só o áudio.** Uma live de 4 horas fica com algumas centenas de MB, não um vídeo gigante.
2. **Escuta a live inteira no seu computador.** Escreve tudo que o streamer fala e marca onde ele ficou alto
   (grito, surto) e, no YouTube, onde o chat acelerou.
3. **A IA lê 12 minutos por vez e dá nota pra cada momento.** É rigorosa: o que precisa de contexto ou começa
   com enrolação vai pro lixo.
4. **Monta os cortes.** Baixa só os minutos escolhidos, acha a câmera do streamer sozinha e coloca a legenda.

## Instalação

Você precisa do **Claude Code** (pode ser com a sua assinatura do Claude ou de graça, com o Ollama).

### Jeito de graça (Ollama) — precisa de 16 GB de memória ou mais

1. Baixe o Ollama em https://ollama.com/download e abra. Clique em **Continue** e depois em
   **"No thanks, I'll use Ollama locally"** (não precisa de conta).
2. Abra as **Settings** do Ollama (no Mac: menu Ollama → Settings…) e arraste o **Context length** de 4k para **64k**.
3. Feche o navegador e os outros programas (a IA usa quase toda a memória).
4. Abra o terminal (Mac: Command + Espaço → "Terminal"; Windows: Iniciar → "Windows PowerShell") e digite:
   ```
   mkdir cortes-gta
   cd cortes-gta
   ollama launch claude --model qwen3.5
   ```
   Com 32 GB ou mais, use `qwen3.5:27b`. Na primeira vez ele baixa a IA (~7,6 GB): o **Yes** já vem marcado, é só Enter.
5. Na pergunta "Is this a project you trust?", aperte a **seta pra baixo** até **"Yes, I trust this folder"** e Enter
   (a opção marcada de início é "No, exit"). Avisos amarelos como "isn't recognized" e "Not logged in" são normais.

### Com a assinatura do Claude

Baixe o app em https://claude.com/download (plano Pro ou maior), entre na aba **Code** e escolha uma pasta.
Sem terminal. Os cortes saem mais rápido e as escolhas ficam bem melhores.

### Colocando a skill

Cole no Claude Code:

> instala essa skill e monta o clipper do GTA 6: https://github.com/davixavier-coder/skill-clips

Ou baixe esta skill (botão verde **Code → Download ZIP**), descompacte, arraste a pasta pra dentro do Claude Code e
fale a mesma frase. Quando ele perguntar "Do you want to…", aperte Enter.

Ele confere o que falta no seu computador, instala sozinho (inclusive o ffmpeg) e avisa quando tá pronto.

## Usando

- "corta essa live: LINK"
- "acha as maiores lives de GTA 6 de hoje e corta"
- "faz 5 cortes dessa live: LINK"

Os cortes ficam na pasta `clipper-gta6/cortes` da sua pasta de usuário.

## Precisa ter

- Mac, Windows ou Linux
- Python 3.10 ou mais novo (se faltar, o Claude te guia)
- ffmpeg: a skill baixa sozinha
- uns 2 GB livres pros modelos de escuta, mais o áudio das lives

## Respeite os streamers

Corte só quem libera cortes e mantenha o crédito que vem no `.txt` de cada corte.
