# Manual do Administrador — AI TeamTalk Bot

> Versão: **v0.3.2** — versão 3 do bot.

Este manual cobre os comandos exclusivos de administrador. Administradores também podem usar os comandos do manual do usuário.

## Controle do bot
| Comando | O que faz |
|---|---|
| `lock` | Trava o bot para usuários não-admin. |
| `block <comando>` | Bloqueia um comando. |
| `unblock <comando>` | Desbloqueia um comando. |
| `rs` | Reinicia o bot. |
| `q` | Encerra o bot. |

## Configuração de IA
| Comando | O que faz |
|---|---|
| `gapi <chave>` | Define a chave da API do Groq. |
| `list_groq_models` / `lgm` | Lista os modelos disponíveis. |
| `set_groq_model <modelo>` / `sgm <modelo>` | Define o modelo ativo. |
| `instruct <instruções>` | Define as instruções permanentes da IA. |
| `setwelcomeinstruction <instruções>` | Define as instruções da mensagem de boas-vindas. |
| `tg_groq_pm` | Liga/desliga a IA no PM. |
| `tg_groq_chan` | Liga/desliga a IA no canal. |
| `tgmmode` | Alterna o modo da mensagem de boas-vindas. |
| `tg_context_history` | Liga/desliga o histórico de contexto. |
| `set_context_retention <minutos>` | Define o tempo de retenção do contexto. |

## Idioma e tradução
| Comando | O que faz |
|---|---|
| `set_language <idioma>` | Define o idioma do bot. |
| `tg_translator` | Liga/desliga o modo tradutor. |
| `set_translate_lang <idioma>` | Define o idioma de destino. |

## Agendador de tarefas
| Comando | O que faz |
|---|---|
| `addtask <maintenance\|restart\|shutdown\|disconnect> <HH:MM>` | Agenda uma tarefa diária. |
| `deltask <id>` | Remove uma tarefa. |
| `listtasks` | Lista tarefas agendadas. |

Sons: `maintenance` → `notify1.wav`, `restart` → `notify2.wav`, `shutdown` → `notify3.wav`, `disconnect` → `notify4.wav`.

## Moderação
| Comando | O que faz |
|---|---|
| `addword <palavra>` | Adiciona palavra ao filtro. |
| `delword <palavra>` | Remove palavra do filtro. |
| `tfilter` | Liga/desliga o filtro. |
| `kick <apelido>` | Expulsa usuário do canal atual. |
| `ban <apelido>` | Bane usuário do servidor. |
| `unban <username>` | Remove banimento. |
| `listusers [canal]` | Lista usuários. |
| `listchannels` | Lista canais. |
| `move <apelido> <canal>` | Move usuário. |
| `admins` | Lista administradores e presença. |
| `jc <canal>[\|senha]` | Move o bot para outro canal. |

## Comunicação
| Comando | O que faz |
|---|---|
| `ct <mensagem>` | Envia mensagem para o canal atual. |
| `bm <mensagem>` | Envia broadcast para o servidor. |
| `jcl` | Liga/desliga avisos de entrada e saída. |
| `tg_chanmsg` | Liga/desliga mensagens no canal. |
| `tg_broadcast` | Liga/desliga broadcasts. |

## YouTube

O sistema de YouTube possui reprodução, fila, controle de tempo e download do vídeo atual. O comando de download é **`dl`**: não recebe URL nem busca.

| Comando | O que faz |
|---|---|
| `yt <busca ou link>` | Inicia ou substitui a reprodução. |
| `ytstop` | Para e limpa a fila. |
| `ytpause` | Pausa. |
| `ytresume` | Continua. |
| `ytforward [segundos]` | Avança; padrão 10 s. |
| `ytback [segundos]` | Retrocede; padrão 10 s. |
| `ytnext` | Próximo item. |
| `ytprev` | Item anterior. |
| `ytplaylist <link>` | Carrega playlist. |
| `ytclear` | Limpa a fila. |
| `dl` | Baixa o vídeo atualmente tocando e envia o MP3 para o TeamTalk. |

O áudio baixado é convertido para **MP3 320 kbps / 48 kHz** usando `yt-dlp.exe` e `ffmpeg.exe` da pasta `tools`.

## Painel Web

O painel web usa `host` e `port` na seção `[WebUI]` do `config.ini`.

## Sons

Consulte `docs/SOUNDS.md` para a tabela completa.

---
*Manual do administrador — AI TeamTalk Bot v0.3.2*
