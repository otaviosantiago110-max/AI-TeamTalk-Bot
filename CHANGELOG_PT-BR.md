- Adicionado o comando `wsnd`, exclusivo para administradores em PM, para ligar/desligar o som de novo usuário.
## v0.3.3

- Atualizado o TeamTalk SDK de 5.15.0 para 5.19A (5.19.0.5170).
- Removido completamente o sistema de voz de IA desta base.
- Corrigido o nome final dos arquivos MP3 baixados do YouTube para usar apenas o título, sem identificadores aleatórios.

## v0.3.2 — Final

- Sistema de voz reconstruído com captura de áudio, processamento, transcrição e saída por etapas independentes.
- Entrada de voz fixada em 24 kHz mono.
- Saída de voz usa fila de áudio e `CLIENTEVENT_AUDIOINPUT` para controlar o preenchimento do buffer do TeamTalk.
- Identificação do cliente agora é versionada: `AI Bot v0.3.2`.

### v0.3.2

## v0.3.2 — Atualização do sistema

- Novo formato de versão de três componentes: `0.3.2`, `0.3.3`, etc.
- Auto-atualizador usa o pacote `AI-TeamTalk-Bot-v{TAG}.zip`.
- Compatibilidade mantida com versões legadas de quatro componentes na comparação de versões.
- Correção do sistema de voz quando o bot é iniciado pelo WebUI em modo código-fonte.
- Processamento correto dos eventos `CLIENTEVENT_USER_AUDIOBLOCK`.
- Versão do cliente exibida nas informações do servidor como `AI Bot v0.3.2 5.15.0`.
- Nome do pacote de atualização ajustado para `AI-TeamTalk-Bot-v0.3.2.zip`.

## v0.3.0.1 — Sistema de voz e correções do YouTube

- Sistema de voz integrado com captura de áudio do TeamTalk, transcrição via Whisper no Groq e respostas via Edge TTS.
- Ativação por frase de chamada multilíngue, com sessão de 3 segundos de inatividade.
- Sons `appear.wav` e `disappear.wav` usados na ativação e desativação.
- Arquivos baixados pelo `/dl` passam a usar o título do vídeo como nome do MP3, com sanitização para nomes inválidos no Windows.

# Changelog — AI TeamTalk Bot

## v0.3.0.0 — Grande atualização e consolidação da versão 3

### Novidades
- A linha **v0.2.x foi encerrada e arquivada**. A partir desta versão, o desenvolvimento ativo segue a linha **v0.3.x**.
- Consolidação dos sistemas atuais do bot na versão 3.
- YouTube ampliado com pausa, retomada, avanço, retrocesso, próxima, anterior, playlists e fila de reprodução.
- Novo comando `/dl`, que baixa somente o vídeo que está atualmente tocando, sem receber URL ou busca.
- Download de áudio com `yt-dlp.exe` e conversão para MP3 320 kbps / 48 kHz com `ffmpeg.exe`.
- Envio do arquivo baixado pelo TeamTalk, com comportamento específico para canal e PM.
- Pasta `tools/` preparada para os executáveis externos do YouTube.
- Manuais e documentação alinhados à versão **v0.3.0.0**.

### Observação de versão
A v0.3.0.0 representa uma mudança de linha de desenvolvimento, e não apenas um patch da série 0.2.x. As versões 0.2.x permanecem no histórico para referência e não representam mais a linha ativa.
## v0.2.0.7 — YouTube ampliado

- Controle de pausa e retomada da reprodução.
- Avanço e retrocesso por segundos.
- Fila de reprodução com próxima/anterior e avanço automático.
- Carregamento de playlists.
- Download para MP3 320 kbps/48 kHz e envio ao canal via TeamTalk.
- YouTube usa yt-dlp.exe e ffmpeg.exe externos em `tools/`.
- Preparação da API TeamTalk para controle de mídia com pausa e seek.

## v0.2.0.6 — Segundo estágio do auto-atualizador

### Novidades
- Adicionada preparação segura da instalação após o download do pacote da Release.
- O pacote é extraído fora do diretório da aplicação antes da instalação.
- A instalação automática é executada por um processo auxiliar separado, permitindo substituir os arquivos depois que o processo principal termina.
- O diretório atual da aplicação é preservado como backup durante a troca.
- Arquivos de dados do usuário (`config.ini`, `.env`, `site.db` e os arquivos de log) são preservados durante a atualização.
- O nome do executável instalado passa a ser mantido de forma estável, independentemente do nome do executável dentro do pacote baixado.
- A instalação só pode ser iniciada por uma aplicação compilada com PyInstaller.
- A extração rejeita caminhos inseguros no ZIP.
### Limitação
- O rollback automático após uma inicialização malsucedida ainda será implementado na próxima etapa.

## v0.2.0.5 — Primeiro estágio do auto-atualizador

### Novidades
- Adicionado verificador automático de novas versões publicadas nas GitHub Releases.
- As versões são identificadas pelas tags Git no formato `vX.Y.Z.W`.
- A verificação acontece ao conectar e depois a cada 15 minutos.
- Ao encontrar uma versão nova, o bot reproduz `update_found.wav` e pergunta no canal e por mensagem global se deve baixá-la.
- A confirmação aceita `Y` ou `N` e fica restrita aos administradores configurados.
- O download usa o pacote completo da Release e valida o SHA-256 quando o GitHub fornece o digest do asset.
- Durante o download, `updating.wav` é repetido continuamente no canal até a conclusão.
- O pacote baixado é validado e extraído para preparação da próxima etapa do sistema de atualização.

### Observação
- A substituição dos arquivos em execução, reinicialização e rollback automático ficam reservados para a próxima etapa do auto-atualizador.

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
- Conclusão do sistema de atualização, incluindo instalação, reinicialização e rollback.
- Sistema de voz.

> Este arquivo será atualizado a cada nova versão do projeto.
