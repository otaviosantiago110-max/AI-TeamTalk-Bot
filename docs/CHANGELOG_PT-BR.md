# Changelog — AI TeamTalk Bot

## v0.2.0.4 — Ajuste do timer de espera e lembretes sonoros

### Correções
- Corrigido o timer de inatividade para que `message.wav` seja reproduzido a cada ciclo de 20 minutos enquanto o bot aguarda atividade.
- O período de espera agora conta corretamente 30 ciclos de 20 minutos (10 horas).
- Ao completar os 30 ciclos, o bot permanece no estado de sono e reproduz `sleep.wav`.
- Mantido intacto o sistema existente de despertar por mensagem/menção e o som `wake_up.wav`.

## v0.2.0.3 — Ajuste do sistema de menção

### Correções
- Corrigido o sistema de menção para que ele seja aplicado somente às conversas livres com a IA.
- O modo tradutor volta a processar mensagens comuns do canal sem exigir a menção ao apelido do bot.
- Mantido o uso do apelido configurado como gatilho para as interações livres com a IA.

## v0.2.0.2 — Novo sistema de interação

### Novidades
- Alterado o apelido padrão do bot para `AI Bot`.
- O sistema de menção utiliza automaticamente o apelido definido nas configurações, permitindo nomes personalizados como `AI Bot`, `Gerenciamento Bot` ou `Bot Manager`.
- Adicionado o comando `ddev`, que exibe informações do programa, a versão atual e o desenvolvedor.
- Adicionado sistema de menção para interações de IA em mensagens comuns de canal.
- O bot agora ignora mensagens comuns no canal quando seu apelido não é mencionado, reduzindo respostas indesejadas e spam.
- Mensagens direcionadas ao bot podem usar o formato `Olá <apelido>, <mensagem>` ou `<apelido> <mensagem>`.
- O apelido usado na menção é removido do texto antes do processamento pela IA.

## v0.2.0.1 — Patch de estabilidade

### Correções
- Corrigido o gerenciamento da sessão de autenticação da WebUI para que o login seja realmente permanente.
- Aumentada a duração da sessão permanente da WebUI para 30 dias, renovada durante o uso.
- Corrigido o problema em que a configuração deixava de carregar e salvar após alguns minutos, exigindo novo login.

## v0.2.0.0 — Alpha

### Novidades
- Adicionado cadastro de novas contas pela WebUI.
- Adicionado o botão **Criar nova conta** na tela de login.
- Adicionado o som de inicialização `program_started.wav`.
- Melhorado o controle de inicialização, parada e reinicialização do bot.
- Adicionada recuperação automática do bot após encerramento inesperado.
- Melhorada a organização da configuração e do controlador da aplicação.
- Arquitetura preparada para futuras atualizações e para o sistema de voz.
- Separação entre a WebUI/controlador e o processo do bot TeamTalk.

## v0.3.0.0 — Planejado

### Em desenvolvimento
- Sistema de atualização.
- Sistema de voz.

> Este arquivo será atualizado a cada nova versão do projeto.
