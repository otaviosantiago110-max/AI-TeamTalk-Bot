# Manual do Administrador — AI TeamTalk Bot

> Versão: Alfa v0.2.0.0 — este bot ainda está em desenvolvimento ativo. Alguns comportamentos podem mudar.

Este manual cobre os comandos exclusivos de administrador. Administradores também podem usar todos os comandos do [manual do usuário](user_pt-br.md). Só usuários configurados como admin (via `admin_usernames` no `config.ini`, ou pela lista de admins) podem usar os comandos abaixo — qualquer outra pessoa que tentar recebe um aviso de "não autorizado".

## Controle do bot
| Comando | O que faz |
|---|---|
| `lock` | Trava o bot — ele passa a ignorar todos os comandos de não-admins. |
| `block <comando>` | Bloqueia um comando específico para todo mundo. |
| `unblock <comando>` | Desbloqueia um comando bloqueado. |
| `rs` | Reinicia o bot. |
| `q` | Encerra o bot completamente. |

## Configuração de IA
| Comando | O que faz |
|---|---|
| `gapi <chave>` | Define a chave de API do Groq. |
| `list_groq_models` / `lgm` | Lista os modelos do Groq disponíveis. |
| `set_groq_model <modelo>` / `sgm <modelo>` | Define o modelo ativo (ex: `openai/gpt-oss-120b`). |
| `instruct <instruções>` | Define as instruções permanentes de comportamento da IA. |
| `setwelcomeinstruction <instruções>` | Define as instruções da mensagem de boas-vindas gerada por IA. |
| `tg_groq_pm` | Liga/desliga a IA no PM. |
| `tg_groq_chan` | Liga/desliga a IA no canal. |
| `tgmmode` | Alterna o modo da mensagem de boas-vindas (modelo fixo vs. gerada por IA). |
| `tg_context_history` | Liga/desliga a memória de contexto da conversa. |
| `set_context_retention <minutos>` | Define por quanto tempo o histórico de contexto é mantido. |

## Sistema de idiomas
| Comando | O que faz |
|---|---|
| `set_language <pt_BR\|en>` | Define o idioma em que o bot responde (afeta o chat e o painel web). Aceita variações como "pt", "português", "en-US", "inglês". |

## Tradutor
| Comando | O que faz |
|---|---|
| `tg_translator` | Liga/desliga o modo tradutor. Quando ligado, **qualquer mensagem livre** (sem comando) é traduzida em vez de virar uma conversa com a IA. |
| `set_translate_lang <idioma>` | Define o idioma de destino da tradução (ex: "inglês", "espanhol"). |

## Agendador de tarefas
| Comando | O que faz |
|---|---|
| `addtask <maintenance\|restart\|shutdown\|disconnect> <HH:MM>` | Agenda uma tarefa diária recorrente no horário informado (24h). |
| `deltask <id>` | Remove uma tarefa agendada pelo ID. |
| `listtasks` | Lista todas as tarefas agendadas. |

> As tarefas agendadas são salvas no `config.ini` automaticamente e sobrevivem a reinícios do bot. Cada tipo de tarefa tem um som de notificação: `maintenance`→`notify1.wav`, `restart`→`notify2.wav`, `shutdown`→`notify3.wav`, `disconnect`→`notify4.wav`.

## Moderação e filtro de palavras
| Comando | O que faz |
|---|---|
| `addword <palavra>` | Adiciona uma palavra ao filtro. |
| `delword <palavra>` | Remove uma palavra do filtro. |
| `tfilter` | Liga/desliga o filtro de palavras. |
| `kick <apelido>` | Expulsa um usuário do canal atual do bot. |
| `ban <apelido>` | Bane um usuário do servidor. |
| `unban <username>` | Remove o banimento de um usuário. |

> O filtro avisa o usuário a cada palavra proibida detectada; após **3 avisos**, o bot tenta expulsar automaticamente (se tiver permissão).

## Gerenciamento de usuários e canais
| Comando | O que faz |
|---|---|
| `listusers [caminho do canal]` | Lista os usuários de um canal (ou do canal atual, se não especificado). |
| `listchannels` | Lista todos os canais do servidor. |
| `move <apelido> <caminho do canal>` | Move um usuário para outro canal. |
| `admins` | Lista os admins configurados e quem está online. |
| `jc <caminho do canal>[\|senha]` | Faz o bot entrar em outro canal. |

## Comunicação
| Comando | O que faz |
|---|---|
| `ct <mensagem>` | Envia uma mensagem para o canal atual do bot. |
| `bm <mensagem>` | Envia uma mensagem de broadcast para todo o servidor. |
| `jcl` | Liga/desliga os avisos de entrada/saída de usuários. |
| `tg_chanmsg` | Liga/desliga a capacidade do bot de mandar mensagens no canal. |
| `tg_broadcast` | Liga/desliga a capacidade do bot de mandar broadcasts. |

## Depuração
| Comando | O que faz |
|---|---|
| `tg_debug_logging` | Liga/desliga o log de depuração (grava mais detalhes no `bot.log`). |

## Sistema de sons

Veja [`docs/SOUNDS.md`](../SOUNDS.md) para a tabela completa de cada som e quando ele toca (sono/despertar, agendador, tradutor, painel web).

## Painel Web e "Gerenciador de Servidores"

O painel web (`web_ui.py`) tem seu próprio host/porta configuráveis, na seção `[WebUI]` do `config.ini` (`host` e `port`). Isso pode ser ajustado na tela de configuração inicial. **Trocar host/porta exige reiniciar o processo do `web_ui.py`** para valer — o servidor não troca de porta sozinho enquanto está rodando.

## O que ainda falta (roadmap)

- **Reconhecimento de voz** (ativação por palavra-chave + comandos falados) — ainda não implementado, é a parte mais complexa do projeto.
- **Auto-atualizador** (verificação de novas versões no GitHub) — adiado intencionalmente até o bot ficar mais estável.
