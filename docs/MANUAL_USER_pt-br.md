# Manual do Usuário — AI TeamTalk Bot

> Versão: **v0.3.2** — versão 3 do bot, com os sistemas atuais ativados.

Este manual é para qualquer pessoa que queira usar o bot no servidor TeamTalk.

## Como conversar com o bot

- **No PM:** comandos são digitados sem `/`.
- **No canal:** comandos são digitados com `/` na frente.
- Mensagens livres no canal também podem conversar com a IA quando o modo normal estiver ativo.

## Modo de sono

Se ninguém interagir com o bot por **20 minutos**, ele entra em modo de sono e passa a ignorar mensagens até ser acordado por uma menção ao apelido.

## Comandos básicos

| Comando | O que faz |
|---|---|
| `h` / `/h` | Mostra a ajuda de comandos. |
| `ping` / `/ping` | Verifica se o bot está respondendo. |
| `info` / `/info` | Mostra informações do bot e do servidor. |
| `whoami` / `/whoami` | Mostra suas informações de usuário. |
| `rights` / `/rights` | Mostra as permissões do bot. |
| `cn <novo apelido>` / `/cn <novo apelido>` | Muda o apelido do bot. |
| `cs <novo status>` / `/cs <novo status>` | Muda o status do bot. |

## Inteligência Artificial

| Comando | O que faz |
|---|---|
| `c <pergunta>` / `/c <pergunta>` | Envia uma pergunta para a IA. |
| `ch` / `/ch` | Inicia um novo chat, limpando o histórico. |
| `cl` / `/cl` | Limpa o histórico do chat atual. |
| `n` / `/n` | Encerra o chat atual. |

## YouTube

| Comando | O que faz |
|---|---|
| `yt <busca ou link>` / `/yt <busca ou link>` | Pesquisa ou abre um vídeo e inicia a reprodução. |
| `ytstop` / `/ytstop` | Para a reprodução e limpa a fila. |
| `ytpause` / `/ytpause` | Pausa. |
| `ytresume` / `/ytresume` | Continua. |
| `ytforward [segundos]` / `/ytforward [segundos]` | Avança o tempo; padrão 10 segundos. |
| `ytback [segundos]` / `/ytback [segundos]` | Retrocede o tempo; padrão 10 segundos. |
| `ytnext` / `/ytnext` | Próximo vídeo. |
| `ytprev` / `/ytprev` | Vídeo anterior. |
| `ytplaylist <link>` / `/ytplaylist <link>` | Carrega uma playlist na fila. |
| `ytclear` / `/ytclear` | Limpa a fila. |
| `dl` / `/dl` | Baixa **o vídeo que está tocando atualmente**; não recebe URL ou busca. |

O `/dl` baixa o áudio com `yt-dlp.exe`, converte para MP3 **320 kbps / 48 kHz** com `ffmpeg.exe` e envia o arquivo pelo TeamTalk.

## Enquetes

| Comando | O que faz |
|---|---|
| `poll "Pergunta" "Opção A" "Opção B" ...` / `/poll ...` | Cria uma enquete. |
| `vote <id> <número>` / `/vote <id> <número>` | Vota em uma enquete ativa. |
| `results <id>` / `/results <id>` | Mostra os resultados. |

## Idioma

O idioma das respostas é definido pelo administrador.

---
*Manual do usuário — AI TeamTalk Bot v0.3.3*

