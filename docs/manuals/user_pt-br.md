# Manual do Usuário — AI TeamTalk Bot

> Versão: **v0.3.2** — versão 3 do bot, com os sistemas atuais ativados.

Este manual é para qualquer pessoa que queira usar o bot no servidor TeamTalk.

## Como conversar com o bot

- **No PM:** comandos são digitados sem `/`.
- **No canal:** comandos são digitados com `/` na frente.
- Mensagens livres no canal também podem conversar com a IA quando o modo normal estiver ativo.

## Modo de sono

Se ninguém interagir com o bot por **20 minutos**, ele entra em modo de sono e passa a ignorar mensagens até ser acordado por uma menção ao apelido.

## Convivendo com outros bots

O bot ignora comandos conhecidos de outros bots de música e mensagens identificadas como vindas de outros bots, evitando conflitos.

## Informações e utilidades

| Comando | O que faz |
|---|---|
| `h` / `/h` | Mostra a ajuda. |
| `ping` / `/ping` | Verifica se o bot está respondendo. |
| `info` / `/info` | Mostra o status do bot e informações do servidor. |
| `whoami` / `/whoami` | Mostra suas informações no TeamTalk. |
| `rights` / `/rights` | Mostra as permissões do bot. |
| `cn <novo apelido>` / `/cn <novo apelido>` | Muda o apelido do bot. |
| `cs <novo status>` / `/cs <novo status>` | Muda o status do bot. |

## Inteligência Artificial

| Comando | O que faz |
|---|---|
| *(mensagem livre)* | Conversa diretamente com a IA. |
| `c <pergunta>` / `/c <pergunta>` | Pergunta algo para a IA. |
| `ch` / `/ch` | Inicia um novo chat. |
| `cl` / `/cl` | Limpa o histórico atual. |
| `n` / `/n` | Encerra o chat atual. |

## YouTube

O YouTube possui uma fila interna para controlar vários vídeos.

| Comando | O que faz |
|---|---|
| `yt <busca ou link>` / `/yt <busca ou link>` | Pesquisa ou abre um vídeo e começa a reprodução. |
| `ytstop` / `/ytstop` | Para a reprodução e limpa a fila. |
| `ytpause` / `/ytpause` | Pausa o vídeo atual. |
| `ytresume` / `/ytresume` | Continua o vídeo pausado. |
| `ytforward [segundos]` / `/ytforward [segundos]` | Avança o tempo; padrão de 10 segundos. |
| `ytback [segundos]` / `/ytback [segundos]` | Retrocede o tempo; padrão de 10 segundos. |
| `ytnext` / `/ytnext` | Próximo vídeo. |
| `ytprev` / `/ytprev` | Vídeo anterior. |
| `ytplaylist <link>` / `/ytplaylist <link>` | Adiciona uma playlist à fila. |
| `ytclear` / `/ytclear` | Limpa a fila. |
| `dl` / `/dl` | Baixa o vídeo que está tocando atualmente. |

### Download do vídeo atual

O comando `/dl` **não recebe URL, busca ou outro argumento**. Ele usa o vídeo que está atualmente em reprodução, baixa o áudio, converte para MP3 **320 kbps / 48 kHz** e envia o arquivo pelo TeamTalk.

- Usado no canal: envia para esse canal.
- Usado em PM: envia para o canal atual do bot.
- Sem vídeo tocando: nenhum download é iniciado.

## Enquetes

| Comando | O que faz |
|---|---|
| `poll "Pergunta" "Opção A" "Opção B" ...` / `/poll ...` | Cria uma enquete. |
| `vote <id> <número da opção>` / `/vote ...` | Vota. |
| `results <id>` / `/results ...` | Mostra os resultados. |

## Idioma

O idioma das respostas do bot é definido pelo administrador.

### Voz

O bot pode escutar o áudio dos usuários, reconhecer frases de chamada em idiomas suportados, transcrever com Whisper via Groq e responder por voz usando Edge TTS. A sessão termina após 3 segundos sem nova fala.
