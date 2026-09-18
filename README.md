# CKP01 - Chatbot Profissional: Fleet Charge Intelligence

Prompt Engineering and Artificial Intelligence - FIAP - 2o semestre 2026.

**Prototipo em revisao, nao definitivo. Atualizado em 18/09/2026 com evidencias fornecidas pelo usuario. Ha pendencias de entrega abaixo.**

## Integrantes e entrega

| Integrante | Nome completo | RM |
|---|---|---|
| 1 | Matheus Anciães Patelli | 567261 |
| 2 | PREENCHER | PREENCHER |
| 3 | PREENCHER | PREENCHER |
| 4, se houver | PREENCHER ou remover linha | PREENCHER |

Grupo de 3-4 alunos. Somente o lider envia o ZIP pelo Teams ate 23:55 do dia da Aula 05. O PDF nao informa uma data de calendario: confirmar com a turma. A Aula 04 apresenta o trabalho; nao ha apresentacao ao vivo do grupo. Confirmar registro/exclusividade do dominio com o professor: o PDF diz que, em caso de dominios iguais, apenas o primeiro entregue e aceito.

## Dominio

Assistente consultivo para gerenciamento de recarga de frotas eletricas. Usuarios-alvo: gestores, operadores e equipes que precisam entender tarifas, energia, margens e estrategias. Escolhemos esse dominio para reaproveitar a camada conversacional no Fleet Charge Intelligence, sem atribuir ao chatbot o controle de equipamentos ou a certificacao de cronogramas.

O dominio deve ser mantido no CKP02 (RAG) e CKP03 (agente). Este e um novo pacote local, criado para o CKP01, sem Colab e sem reescrever o chatbot do primeiro semestre.

## Requisitos e estado real

| Requisito do PDF | Implementacao | Estado |
|---|---|---|
| ChatOllama com gemma4:cloud | app/chain.py, chave em .env | Usuario executou e recebeu resposta; metadados do provedor nao recebidos |
| ConversationChain + memoria | build_chat + TokenBuffer | Retencao observada em cinco interacoes manuais |
| LCEL com operador pipe | prompt \| llm \| PydanticOutputParser | Usuario apresentou JSON com oito campos esperados |
| Templates com system/human separados | app/prompts.py + ChatPromptTemplate | Implementado |
| XML tagging e persona | persona, dominio, regras, referencia, resposta | Implementado |
| Pydantic v2 >=4 campos | AnaliseConsulta, oito campos e validadores | Implementado |
| Memoria em >=5 turnos | Roteiro manual de cinco turnos; script opcional de seis | Registro em evidence/VALIDACAO_USUARIO_2026-09-18.md |
| Context rot real em tabela | app/context_rot.py | Nove acertos relatados; degradacao nao observada; JSON original pendente |
| Pacote local e Gradio | python -m app.main | Interface executada pelo usuario com respostas |
| Nomes e RMs | tabela acima | Pendente |
| Diferencial: tokens/metricas | tiktoken e acerto de quatro campos | Tabela recebida com tokens estimados e acertos |
| Diferencial: meta prompting | Nao implementado | Opcional, nao reivindicado |

Nao substituir as evidencias online por testes com respostas programadas. Nenhum resultado de degradacao foi inventado.

## Arquitetura das duas chains

1. Chat: `ConversationChain(ChatOllama, ConversationTokenBufferMemory, ChatPromptTemplate)`.
2. Analise: `ChatPromptTemplate | ChatOllama | PydanticOutputParser(AnaliseConsulta)`.

A segunda chain recebe a pergunta e o historico limitado da conversa. Exibe classificacao, resumo, modo citado, dados faltantes, alertas, proximo passo e indicacao obrigatoria de analise consultiva/decisao humana. Validacao Pydantic garante estrutura e dominios, nao verdade factual ou viabilidade de recarga.

Foram usados `langchain-classic` para as classes legadas exigidas literalmente pelo enunciado e `langchain-core`/`langchain-ollama` para LCEL e ChatOllama. ConversationChain e memorias classicas podem emitir avisos de deprecacao da biblioteca; foram mantidas para cumprir o metodo pedido. O requisito de nao usar modelos deprecated nao autoriza trocar o modelo exigido por conta propria.

## Como executar no Windows (PowerShell)

Python 3.12 foi usado na verificacao local. Abra o terminal nesta pasta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m app.main
```

Preencha a chave no arquivo local .env. Nao cole a chave em chats, codigo, README ou Teams. Se .env ja existir, preserve-o: nao execute novamente o Copy-Item.

Abra http://localhost:7860 . O servidor escuta somente em 127.0.0.1 e nao cria link publico. A interface pode abrir sem chave; o envio de mensagens exige autenticacao. A execucao Python e local, mas a inferencia ocorre no Ollama Cloud e requer internet.

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp -n .env.example .env
# Edite .env com um editor local.
.venv/bin/python -m app.main
```

### Modelo e evidencia de execucao

O PDF exige literalmente `gemma4:cloud` e OLLAMA_API_KEY. Por isso o codigo fixa esse identificador, usa ChatOllama com `https://ollama.com` e envia a chave no header Authorization. Nao ha fallback para outro modelo.

Em 18/09/2026, o usuario executou a aplicacao e apresentou respostas do chat e da analise estruturada. Isso fornece evidencia manual de funcionamento nessa execucao. Nao recebemos metadados brutos para auditar a identidade do modelo servido; o identificador no codigo continua inalterado. Consulte o registro em evidence/VALIDACAO_USUARIO_2026-09-18.md.

## Justificativa da memoria

Usamos **ConversationTokenBufferMemory de 1200 tokens estimados**, dentro da faixa 800-1500. Ela guarda o contexto recente sem exigir uma chamada adicional para resumir, reduzindo historico enviado e evitando que um resumo gerado altere numeros importantes. Ao exceder o limite, remove mensagens antigas; isso pode apagar fatos relevantes. Nao e memoria permanente ou banco de dados da frota.

O limite e do historico, nao do prompt total (system, pergunta e esquema tambem consomem tokens). `tiktoken` com `cl100k_base` e um proxy consistente, nao o tokenizer nativo do Gemma. Os tokens realmente informados pelo provedor, quando presentes, ficam nas evidencias. A primeira contagem pode baixar o vocabulario do tiktoken.

A poda ocorre ao salvar cada turno. Uma mensagem atual longa pode aumentar o prompt antes dessa poda. O limite de 1200 nao e um teto rigido para a requisicao completa.

Cada sessao Gradio possui memoria propria. Nova conversa descarta a memoria daquela sessao. O historico visivel pode conter mensagens ja removidas do contexto enviado ao modelo. Se uma chamada falhar, a interface informa a falha sem inventar JSON validado.

Enviar, Enter e Nova conversa compartilham uma fila serializada para evitar alteracoes simultaneas da memoria. Neste prototipo a fila tambem e compartilhada entre sessoes; nao e dimensionamento de producao multiusuario.

## Demonstracao real da memoria

Ja existe registro manual de cinco interacoes em `evidence/VALIDACAO_USUARIO_2026-09-18.md`. Para produzir adicionalmente um log automatico de seis turnos, o comando opcional abaixo faz novas chamadas ao modelo; nao e uma execucao ja realizada:

```powershell
.\.venv\Scripts\python.exe -m app.demo_memory --output evidence/demo_memory.json
```

O roteiro usa seis turnos sinteticos sobre Atlas, T01 e saida19:00. Salva perguntas, respostas e memoria. Leia as respostas para confirmar retencao de contexto; verificacao lexical auxiliar nao substitui avaliacao semantica. Se falhar, corrigir a causa e repetir com NOVO nome de arquivo. Nao sobrescrever tentativas anteriores. Seis turnos curtos demonstram retencao, mas podem nao atingir o limite de poda.

## Context rot

```powershell
.\.venv\Scripts\python.exe -m app.context_rot --output evidence/context_rot.json --repetitions 3
```

O programa usa tres contextos de aproximadamente2000/4000/8000 tokens totais estimados, tres repeticoes cada (nove chamadas). Memoria do chat continua1200: sao parametros distintos. System prompt, pergunta, fatos relevantes e gabarito permanecem constantes; aumentam apenas os distratores. O experimento nao poda os fatos localmente. Mede extracao de quatro campos, salva respostas brutas, erros, latencias e metadados, e gera uma tabela Markdown.

**O usuario executou o experimento e forneceu `evidence/context_rot.md`.** Foram registrados 3/3 acertos em cada nivel de 1985, 3985 e 7985 tokens estimados, sem erros: degradacao nao observada nesta amostra. O JSON original ainda deve ser acrescentado para conferir respostas brutas e metadados. Nao repetir automaticamente o teste ja realizado.

O requisito de demonstrar degradacao real permanece pendente. Discutir uma extensao controlada ou a interpretacao com o professor. Nao remover fatos, inventar erros ou escolher apenas tentativas ruins para fabricar a conclusao. Falha de rede/autenticacao e perda por poda nao sao prova de context rot. Tres repeticoes sao exploratorias, nao uma conclusao estatistica robusta.

## Uso futuro no Fleet Charge Intelligence

- CKP01: consulta, explicacao e coleta estruturada de necessidades.
- CKP02: recuperar documentos/versionamentos aprovados com RAG; nao implementado aqui.
- CKP03: propor integracao com ferramentas do motor deterministico e exigir verificacao/decisao humana; nao implementado aqui.

O prompt carrega um resumo fixo do estado do projeto de16/09/2026. Nao consulta GitHub nem arquivos do motor automaticamente. Os resultados de inviabilidade do V2 sao contexto documental, nao calculados por este chatbot. Requisitos tecnicos GoodWe nao foram publicados e nao devem ser inventados.

## Testes e entrega

Testes de engenharia, sem inferencia real:

Nove testes locais passaram na preparacao, incluindo construcao da interface. Foi fixado NumPy2.2.6 apos falha de carregamento binario da versao instalada inicialmente. Consulte `evidence/TESTES_OFFLINE.md`, um registro historico anterior aos testes online do usuario. Nesta atualizacao nao foram repetidos testes nem chamadas ao modelo. O reforco nos prompts para impedir sugestao de ajuste operacional da MMS ainda requer verificacao online.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Antes de entregar:

1. Preencher nomes/RMs e confirmar dominio e data da Aula05.
2. Conferir o reforco da regra MMS no chat e no JSON da versao atualizada.
3. Acrescentar o context_rot.json original e resolver a pendencia de degradacao com o professor; preservar a evidencia manual de memoria ja registrada.
4. Conferir que nenhum arquivo contem chave ou dados pessoais reais de operadores.
5. Gerar o ZIP com `python package_submission.py`. O empacotador inclui somente app/, tests/, evidence/, README, requirements e .env.example, excluindo caches e .env. Inspecionar o ZIP antes de o lider enviar.

O ZIP atualizado preserva as evidencias recebidas, mas ainda nao e uma entrega final completa. Inclui .gitignore para publicar os fontes com exclusao de credenciais e ambiente virtual. Meta prompting e opcional e nao foi reivindicado como bonus.

## Fontes

- Enunciado fornecido: CKP01_2Semestre_Chatbot_Profissional.pdf, prof. Jorge Luiz Gomes.
- [ChatOllama, LangChain](https://docs.langchain.com/oss/python/integrations/chat/ollama).
- [Ollama Cloud: autenticacao e identificadores](https://docs.ollama.com/cloud).
- [Gemma4 e tags publicadas](https://ollama.com/library/gemma4).

Nenhuma publicacao no GitHub ou entrega no Teams foi realizada para este trabalho.
