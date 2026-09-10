# Manual do Usuário — Ai Bot (TeamTalk)

> Versão do bot: **Alfa pública v0.2.0** — ainda em desenvolvimento, pode conter instabilidades.

Este manual cobre todos os comandos disponíveis para **qualquer usuário** do servidor. Para comandos administrativos, veja o `MANUAL_ADMIN_pt-br.md`.

## Como os comandos funcionam

- **Por PM (mensagem privada)**: digite o comando **sem barra**. Ex: `c oi, tudo bem?`
- **No canal**: digite o comando **com barra `/` na frente**. Ex: `/c oi, tudo bem?`
- Nem todo comando de PM está disponível no canal — os disponíveis no canal estão marcados abaixo com 🔊.

## Chat livre com IA (sem precisar de comando)

Você não precisa digitar `c` toda vez. Basta mandar uma mensagem qualquer (sem `/` na frente, no canal) que o bot responde usando IA — como se fosse uma conversa normal.

> ⚠️ Se o bot estiver **dormindo** (veja abaixo), ele ignora tudo até alguém mencionar o apelido dele na mensagem.

## Sistema de sono

Se ninguém interagir com o bot por **20 minutos**, ele "dorme" (toca um som indicando isso) e passa a **ignorar todas as mensagens**, exceto se você mencionar o apelido dele em qualquer parte do texto — aí ele acorda e responde normalmente. Se ele ficar 10 horas sem ninguém falar com ele, desiste de tentar chamar atenção e fica apenas "acordado e quieto" até alguém interagir.

## Comandos básicos

| Comando | O que faz |
|---|---|
| `h` 🔊 | Mostra a lista de comandos (esta ajuda). |
| `ping` | Verifica se o bot está respondendo. |
| `info` | Mostra o status do bot e informações do servidor. |
| `whoami` | Mostra suas informações de usuário. |
| `rights` | Mostra as permissões que o bot tem no servidor. |
| `cn <novo_apelido>` | Muda o apelido do bot. |
| `cs <novo_status>` | Muda a mensagem de status do bot. |

## Inteligência Artificial (Groq)

| Comando | O que faz |
|---|---|
| `c <pergunta>` 🔊 | Pergunta algo pra IA. No canal, responde só no canal; no PM, só no PM (nunca os dois juntos). |
| `ch` 🔊 | Inicia um chat novo, **apagando** o histórico da conversa anterior. |
| `cl` 🔊 | Limpa o histórico do chat atual, sem sair da conversa. |
| `n` 🔊 | Encerra o chat atual. |

## YouTube

| Comando | O que faz |
|---|---|
| `yt <busca ou link>` 🔊 | Busca no YouTube (ou usa o link direto) e **toca o áudio no canal**. |
| `ytstop` 🔊 | Para a reprodução atual. |

> O bot ignora comandos de *outros* bots que dividem o canal com ele (tipo `/p`, `/pause`, `/stop` de um bot de música), então não tem conflito entre os dois.


## Enquetes

| Comando | O que faz |
|---|---|
| `poll "Pergunta" "Opção A" "Opção B" ...` 🔊 | Cria uma nova enquete. |
| `vote <id_da_enquete> <número_da_opção>` 🔊 | Vota em uma enquete ativa. |
| `results <id_da_enquete>` 🔊 | Mostra os resultados de uma enquete. |

## Idioma

O idioma das respostas do bot (incluindo este manual) é o mesmo configurado pelo administrador. Se quiser saber qual é, use `info`.

---
*Manual gerado para o Ai Bot — Alfa pública v0.2.0.0
