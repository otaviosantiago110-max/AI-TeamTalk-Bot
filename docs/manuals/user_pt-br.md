# Manual do Usuário — AI TeamTalk Bot

> Versão: Alfa v0.2.0.0 — este bot ainda está em desenvolvimento ativo. Alguns comportamentos podem mudar.

Este manual é para qualquer pessoa que queira usar o bot no servidor TeamTalk. Não é preciso ser administrador para nada listado aqui.

## Como conversar com o bot (sem comando nenhum)

Você **não precisa digitar nenhum comando** para conversar com o bot. Basta mandar uma mensagem normal:

- **No PM:** qualquer mensagem que você mandar no privado vira uma pergunta para a IA.
- **No canal:** qualquer mensagem sem `/` na frente também vira uma pergunta para a IA — a não ser que o bot esteja "dormindo" (veja a seção **Modo de sono** abaixo), caso em que você precisa mencionar o apelido dele.

A resposta sempre volta pelo mesmo lugar de onde você mandou (PM responde no PM, canal responde no canal — nunca os dois ao mesmo tempo).

## Modo de sono

Se ninguém interagir com o bot por **20 minutos**, ele "dorme". Enquanto dorme:

- Ele **ignora completamente** qualquer mensagem — comandos, conversa, tudo — **exceto** se você mencionar o apelido dele em qualquer parte do texto.
- Mencionar o apelido acorda ele na hora, e a própria mensagem já é processada normalmente.
- A cada 20 minutos que ele fica sem ninguém interagir, ele solta um lembrete sonoro. Depois de **30 lembretes (10 horas)**, ele desiste e fica "acordado" sozinho, mas continua exigindo a menção até alguém realmente interagir.

## Convivendo com outros bots

Se o servidor tiver outros bots (por exemplo, um bot de música), este bot **ignora automaticamente**:
- Comandos conhecidos de outros bots (`/p`, `/pause`, `/resume`, `/stop`, `/next`, `/prev`, `/sf`, `/sb`, `/seek`, `/l`, `/v`, `/mute`, `/unmute`, `/r`, `/join`, `/leave`, `/playlist`, `/sunucu`, `/status`, `/adminhelp`)
- Qualquer mensagem enviada por um usuário cujo apelido termine em "bot" (assumindo que é outro bot, não uma pessoa)

## Comandos disponíveis

Comandos de **PM** funcionam sem precisar de `/` na frente. No **canal**, todos os comandos precisam do `/` na frente (exceto quando indicado).

### Informações e utilidades
| Comando | O que faz |
|---|---|
| `h` | Mostra a lista de comandos (essa ajuda). |
| `ping` | Verifica se o bot está respondendo. |
| `info` | Mostra o status do bot e do servidor. |
| `whoami` | Mostra suas informações de usuário no TeamTalk. |
| `rights` | Mostra as permissões que o bot tem no servidor. |
| `cn <novo apelido>` | Muda o apelido do bot. |
| `cs <novo status>` | Muda a mensagem de status do bot. |

### Inteligência Artificial (Groq)
| Comando | O que faz |
|---|---|
| *(mensagem livre)* | Conversa direto com a IA, sem precisar de comando. |
| `c <pergunta>` | Pergunta algo para a IA via PM. |
| `/c <pergunta>` | Pergunta algo para a IA no canal. |
| `ch` / `/ch` | Inicia um novo chat com a IA (apaga o histórico da conversa). |
| `cl` / `/cl` | Limpa o histórico da conversa atual, sem "reiniciar" o chat. |
| `n` / `/n` | Encerra o chat atual. |

### YouTube
| Comando | O que faz |
|---|---|
| `yt <busca ou link>` / `/yt` | Busca no YouTube (ou usa o link direto) e toca o áudio no canal. |
| `ytstop` / `/ytstop` | Para a reprodução atual. |

> O YouTube só toca um áudio por vez — se você pedir uma música nova, a atual para automaticamente.

| Comando | O que faz |
|---|---|

> Você também pode simplesmente perguntar isso na conversa livre, tipo "me conta uma citação" ou "que eventos têm hoje?" — a IA entende e busca essas informações sozinha.

### Enquetes
| Comando | O que faz |
|---|---|
| `poll "Pergunta" "Opção A" "Opção B" ...` | Cria uma nova enquete. |
| `vote <id> <número da opção>` | Vota em uma enquete ativa. |
| `results <id>` | Mostra o resultado de uma enquete. |

## Idioma

O bot responde em **português do Brasil por padrão**. Um administrador pode trocar para inglês com o comando `set_language`. O painel de controle web também segue o mesmo idioma configurado.
