# Registro de verificacao local - 17/09/2026

**Nao e evidencia de comportamento do Gemma nem de context rot real.**

Comando executado a partir da pasta do projeto, com Python3.12 e as dependencias fixadas:

```text
python -m unittest discover -s tests -v
Ran 9 tests in 2.843s
OK
```

Casos aprovados:

1. ConversationChain conserva seis turnos curtos no historico.
2. Interface Gradio e construida sem instanciar o cliente cloud.
3. Pipeline LCEL converte JSON simulado valido em objeto Pydantic.
4. Pipeline rejeita saidas simuladas invalidas, campos extras e decisao humana falsa.
5. Limites de memoria fora de800–1500 sao rejeitados.
6. Modelo literal gemma4:cloud preservado.
7. Schema tem oito campos obrigatorios e proibe extras.
8. Duas sessoes nao compartilham historico.
9. Seis turnos longos removem mensagens antigas e respeitam1200 tokens proxy apos salvar.

Testes usam FakeListChatModel, somente dentro de tests/. Aplicacao normal usa ChatOllama. Nao inferir retencao semantica, qualidade ou autenticacao a partir destes resultados.

Na primeira tentativa, Gradio encontrou SIGBUS ao importar NumPy2.5.3. NumPy foi substituido por2.2.6 no ambiente isolado e a bateria completa acima passou. O restante do projeto Fleet Charge nao foi alterado.

Avisos de deprecacao de ConversationChain/ConversationTokenBufferMemory sao esperados: foram preservadas as classes exigidas pelo enunciado, via langchain-classic.

Verificacao adicional realmente executada: servidor Gradio iniciado em127.0.0.1:7860, pagina consultada com HTTP200 (60996 bytes) e servidor encerrado. Nenhuma mensagem foi enviada ao modelo. Isso verifica inicializacao local, nao conversa real.

A auditoria final identificou concorrencia entre Enviar/Enter/reset. Foi corrigida com concurrency_id compartilhado e limite1. Verificacao posterior de construcao da UI confirmou os tres eventos no mesmo grupo; nao foi um teste real de carga multiusuario. A contagem da demonstracao foi alinhada ao metodo de tokens do proprio objeto de memoria, ainda com proxy tiktoken.

Pendente: teste real de conexao/modelo, demo_memory.json com respostas reais, context_rot.json e tabela de observacoes reais. Nenhuma evidencia online foi fabricada.
