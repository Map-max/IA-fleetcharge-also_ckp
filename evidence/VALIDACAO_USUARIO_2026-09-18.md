# Validacao manual informada pelo usuario - 18/09/2026

Origem: execucao no Windows pelo usuario e respostas copiadas nesta conversa.
Este registro foi transcrito pelo assistente; nao e um log automatico nem uma
nova execucao do modelo. Python 3.12 (64-bit); interface em 127.0.0.1:7860.

## Consulta e analise estruturada

Pergunta: Qual e a margem minima de seguranca do modo Equilibrado?
Resposta recebida: 2 horas; inviabilidade restrita ao cenario V2.
O JSON apresentado continha os oito campos esperados: tema, resumo,
modo_citado, dados_faltantes, alertas, proximo_passo, natureza e
requer_decisao_humana. Natureza: analise_consultiva_nao_validada; decisao humana: true.

Observacao: proximo_passo sugeriu avaliar ajuste da MMS. Isso e inadequado
como acao operacional do Equilibrado V1. Os dois prompts foram reforcados
nesta revisao para manter MMS obrigatoria e distinguir nova versao da regra.
Esse reforco ainda nao foi testado com o modelo real; nao afirmar correcao comprovada.

## Memoria: cinco interacoes na mesma conversa

| Turno | Entrada enviada conforme roteiro | Resposta relatada (resumo) |
|---|---|---|
| 1 | Estou simulando a frota Atlas. | Reconheceu Atlas e pediu dados. |
| 2 | O veiculo de referencia e o T01. | Registrou T01. |
| 3 | A saida prevista dele e as 19h. | Registrou 19h e manteve T01. |
| 4 | O modo escolhido e o Equilibrado V1. | Reconheceu MMS de 2 horas. |
| 5 | Qual frota, veiculo e saida informei? Ate que horario ele deve terminar a recarga? | Atlas, T01, saida 19h e termino ate 17h. |

Resultado: retencao correta dos fatos neste caso manual. Nao prova viabilidade
da sessao, resistencia a contextos longos ou comportamento de poda.
O script app/demo_memory.py nao foi executado neste registro; nao existe
demo_memory.json recebido. Nao confundir este roteiro de cinco turnos com
as seis interacoes previstas naquele script.

## Contexto crescente

O usuario executou app.context_rot e forneceu context_rot.md, preservado
sem alteracao neste diretorio. O relatorio registra 3/3 acertos em cada nivel
de 1985, 3985 e 7985 tokens estimados: nove respostas, sem erros.
Conclusao: degradacao nao observada nesta amostra.

O usuario informou que context_rot.json foi gerado no seu computador, mas
nao o enviou. Respostas brutas, prompts e metadados ainda nao foram conferidos.
O requisito de demonstrar degradacao continua pendente; nao fabricar falhas.

## Pendencias de entrega

- Adicionar o context_rot.json original do mesmo experimento.
- Preencher demais integrantes/RMs (grupo de 3-4), confirmar dominio e prazo.
- Revalidar o reforco de MMS na interface, se for usar esta versao atualizada.
- Resolver com o professor a ausencia de degradacao ou ampliar o experimento
  de modo controlado, preservando todos os resultados e contabilizando chamadas.
- Criar/publicar repositorio e enviar ZIP no Teams: ainda nao realizados.
