# Sistema de Sons — Design de Referência

Este documento registra o comportamento pretendido de cada som em `/sounds`,
para orientar a implementação de cada sistema à medida que for sendo
construído. Nem todos os sons têm lógica implementada ainda — a coluna
"Status" indica o que já está funcionando.

| Arquivo | Onde toca | Gatilho | Status |
|---|---|---|---|
| `critical.wav` | **Localmente**, na máquina que roda o bot (não no canal — o bot ainda nem conectou) | Python < 3.12, ou dependência do `requirements.txt` faltando, ao iniciar (`main.py`, `main_gui.py`, `web_ui.py`) | ✅ Implementado (`startup_check.py`) |
| `wake_up.wav` | Canal | Bot estava dormindo (ou desistiu dos lembretes) e alguém interagiu com ele — acordou | ✅ Implementado |
| `sleep.wav` | Canal | 20 minutos sem nenhuma atividade real no canal/PM — bot foi dormir | ✅ Implementado |
| `message.wav` | Canal | A cada ciclo de 20 minutos sem atividade, toca como um lembrete "mágico" de que o bot está esperando. Após **30 ciclos (10 horas)** sem atividade, o bot passa a ficar permanentemente "acordado" e esse som para de tocar — nesse ponto passa a ser o `wake_up.wav`/estado acordado que vale | ✅ Implementado |
| `notify1.wav` a `notify4.wav` | Canal | Notificações do agendador de tarefas: `notify1`=maintenance, `notify2`=restart, `notify3`=shutdown, `notify4`=disconnect (mapeamento definido nesta implementação — avise se quiser trocar) | ✅ Implementado (agendador diário simples, em memória) |
| `appear.wav` (era `online.wav`) | Canal | Ativado por voz: alguém disse a palavra de ativação (ex: "Abby, ...") — modo de escuta de voz ligou | ⏳ Depende do sistema de reconhecimento de voz |
| `disappear.wav` (era `offline.wav`) | Canal | 3 segundos de silêncio no canal após ativação por voz — modo de escuta desligou | ⏳ Depende do sistema de reconhecimento de voz |
| `toggle.wav` | Canal | Alternância de modo/funcionalidade (ex: ligar/desligar o futuro "modo tradutor", que traduzirá mensagens automaticamente entre idiomas) | ✅ Implementado |
| `update_found.wav` | Canal + mensagem de canal + mensagem global (broadcast) | Auto-atualizador encontrou uma versão nova disponível no GitHub | Ativo a partir da v0.3.2 |
| `updating.wav` | Canal, em loop contínuo enquanto dura | Auto-atualizador começou a baixar uma atualização (acompanhado de mensagem de canal/global avisando) | ✅ Implementado na v0.3.2 |
| `startup.wav` (era `welcome.wav`) | **No navegador** (Web UI), não no canal | Alguém entra/loga no painel de controle web do bot | ✅ Implementado |

## Notas de design
- `critical.wav`, `notify*.wav` e `update_found.wav`/`updating.wav` tocam fora
  do fluxo normal de chat — os dois primeiros fora do canal (local/scheduler),
  o auto-atualizador toca tanto no canal quanto como aviso global pra todo
  mundo no servidor.
- `startup.wav` é o único que toca fora do TeamTalk inteiramente — é som de
  interface web, então precisa de um `<audio>` no HTML da Web UI, não da API
  do TeamTalk.
- O ciclo de sono/despertar (`wake_up`, `sleep`, `message`) é a base do
  sistema de reconhecimento de voz combinado com o chat livre por texto —
  faz sentido implementar junto quando a voz entrar em cena.
