# Manual do Administrador — Ai Bot (TeamTalk)

> Versão do bot: **Alfa pública v0.2.0** — ainda em desenvolvimento, pode conter instabilidades.

Este manual cobre os comandos exclusivos de **administradores** (configurados em `admin_usernames` no `config.ini`, ou registrados como Super Admin/Admin na Web UI). Para comandos de usuário comum, veja `MANUAL_USUARIO_pt-br.md`.

Todos os comandos abaixo são usados **por PM** — nenhum deles funciona no canal com `/`.

> ⚠️ **Achado durante a revisão deste manual:** o comando `setwelcomeinstruction` (mensagem de boas-vindas com IA) está registrado no código como comando comum, não exige admin. Provavelmente é um descuido — avise se quiser que isso seja corrigido.

## Controle do bot

| Comando | O que faz |
|---|---|
| `lock` | Trava o bot: ignora todos os comandos não-admin até ser destravado (rodar `lock` de novo). |
| `block <comando>` | Bloqueia um comando específico para todo mundo. |
| `unblock <comando>` | Desbloqueia um comando bloqueado. |
| `rs` | Reinicia o bot. |
| `q` | Encerra o bot. |

## Idioma e IA

| Comando | O que faz |
|---|---|
| `set_language <pt_BR\|en>` | Define o idioma de **todas** as respostas do bot (chat e comandos). |
| `gapi <chave>` | Define a chave de API do Groq. |
| `list_groq_models` / `lgm` | Lista os modelos do Groq disponíveis. |
| `set_groq_model <modelo>` / `sgm <modelo>` | Define o modelo ativo do Groq (padrão: `openai/gpt-oss-120b`). |
| `instruct <texto>` | Define as instruções permanentes de sistema pra IA (personalidade, tom, regras). |
| `setwelcomeinstruction <texto>` | Define as instruções da mensagem de boas-vindas gerada por IA. |
| `set_context_retention <minutos>` | Define por quanto tempo o histórico de conversa fica guardado. |

## Alternâncias (ligar/desligar recursos)

| Comando | O que faz |
|---|---|
| `jcl` | Liga/desliga os avisos de entrada/saída de usuários no canal. |
| `tg_chanmsg` | Liga/desliga a capacidade do bot de mandar mensagens no canal. |
| `tg_broadcast` | Liga/desliga a capacidade do bot de mandar mensagens de broadcast. |
| `tg_groq_pm` | Liga/desliga a IA no PM. |
| `tg_groq_chan` | Liga/desliga a IA no canal. |
| `tgmmode` | Alterna entre mensagem de boas-vindas fixa (modelo) e gerada por IA. |
| `tfilter` | Liga/desliga o filtro de palavras. |
| `tg_context_history` | Liga/desliga a memória de contexto das conversas. |
| `tg_debug_logging` | Liga/desliga o log de depuração (mais detalhado). |

## Moderação e usuários

| Comando | O que faz |
|---|---|
| `addword <palavra>` | Adiciona uma palavra ao filtro. |
| `delword <palavra>` | Remove uma palavra do filtro. |
| `listusers [caminho_do_canal]` | Lista os usuários de um canal (ou do canal atual, se não especificar). |
| `listchannels` | Lista todos os canais do servidor. |
| `admins` | Lista os administradores configurados e quem está online agora. |
| `kick <apelido>` | Expulsa um usuário do canal atual do bot. |
| `ban <apelido>` | Bane um usuário do servidor. |
| `unban <usuário>` | Remove o banimento de um usuário. |
| `move <apelido> <caminho_do_canal>` | Move um usuário para outro canal. |

> O filtro de palavras também expulsa automaticamente (se o bot tiver permissão) após **3 avisos** pra o mesmo usuário.

## Canal

| Comando | O que faz |
|---|---|
| `jc <caminho_do_canal>[\|senha]` | Faz o bot entrar em outro canal. |
| `ct <mensagem>` | Manda uma mensagem no canal atual do bot. |
| `bm <mensagem>` | Manda uma mensagem de broadcast pra todo o servidor. |

## Agendador de tarefas

Agenda tarefas **diárias recorrentes**. As tarefas ficam **só na memória** — não sobrevivem a um reinício do bot (precisa readicionar depois de reiniciar).

| Comando | O que faz |
|---|---|
| `addtask <maintenance\|restart\|shutdown\|disconnect> <HH:MM>` | Agenda uma tarefa diária, no horário de 24h. |
| `deltask <id>` | Remove uma tarefa agendada. |
| `listtasks` | Lista as tarefas agendadas. |

Sons de notificação: `maintenance`→`notify1.wav`, `restart`→`notify2.wav`, `shutdown`→`notify3.wav`, `disconnect`→`notify4.wav`.

## Modo tradutor

Quando ativado, **qualquer mensagem livre** (sem comando) é traduzida em vez de conversada com a IA.

| Comando | O que faz |
|---|---|
| `tg_translator` | Liga/desliga o modo tradutor (toca `toggle.wav`). |
| `set_translate_lang <idioma>` | Define o idioma de destino da tradução (padrão: inglês). |

## Sistema de sons (referência rápida)

| Arquivo | Quando toca |
|---|---|
| `critical.wav` | Localmente, ao iniciar: Python < 3.12 ou dependência faltando. |
| `sleep.wav` | Bot entra em modo de sono (20 min sem atividade). |
| `message.wav` | A cada 20 min de sono, até 29 vezes (lembrete). |
| `wake_up.wav` | Bot acorda (por menção ao nome, ou após desistir dos lembretes). |
| `appear.wav` / `disappear.wav` | Reservados para o futuro sistema de voz (ativação/desativação). |
| `toggle.wav` | Alternância de modo (ex: tradutor). |
| `notify1-4.wav` | Notificações do agendador de tarefas. |
| `update_found.wav` / `updating.wav` | Reservados para o futuro auto-atualizador. |
| `startup.wav` | Toca no navegador ao entrar no painel de controle web. |

Veja `docs/SOUNDS.md` para o design completo.

## Configuração da Web UI

No `config.ini`, seção `[WebUI]`:
- `host` — endereço que o painel web escuta (padrão `0.0.0.0`, ou seja, todas as interfaces).
- `port` — porta do painel web (padrão `5000`).

> Mudar esses valores exige **reiniciar o processo do `web_ui.py`** pra valer.

## Pendências conhecidas (para versões futuras)

- **Auto-atualizador**: verificar/baixar novas versões do GitHub automaticamente. *(Adiado — ainda instável.)*
- **Reconhecimento de voz**: ativação por palavra-chave falada, comandos por voz. *(A implementar depois — é a parte mais complexa tecnicamente.)*

---
*Manual gerado para o Ai Bot — Alfa pública v0.2.0.0
