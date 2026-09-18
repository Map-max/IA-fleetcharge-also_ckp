"""Interface Gradio local. Nao cria links publicos nem controla carregadores."""
import gradio as gr
from langchain_core.messages import get_buffer_string
from .chain import build_chat, build_structured, build_llm


def new_session():
    llm = build_llm()
    return {'chat': build_chat(llm), 'structured': build_structured(llm)}


def respond(message, history, session):
    history = history or []
    if not message or not message.strip():
        return '', history, session, None, 'Digite uma pergunta.'
    if len(message) > 6000:
        return message, history, session, None, 'Use ate 6000 caracteres por mensagem.'
    try:
        session = session or new_session()
        answer = session['chat'].invoke({'input': message})['response']
    except Exception as exc:
        # Nao exibir objeto de erro que possa conter headers de autenticacao.
        return message, history, session, None, ('Nao foi possivel conversar (' +
            type(exc).__name__ + '). Verifique .env, conexao e o modelo exigido; consulte README.')
    updated = history + [{'role':'user', 'content':message},
                         {'role':'assistant', 'content':answer}]
    try:
        memory = get_buffer_string(session['chat'].memory.chat_memory.messages)
        analysis = session['structured'].invoke({'input':message, 'history':memory})
        return '', updated, session, analysis.model_dump(), 'Conversa e analise estruturada concluidas.'
    except Exception as exc:
        return '', updated, session, None, ('Conversa concluida; analise estruturada falhou (' +
                type(exc).__name__ + '). Nao foi substituida por dados inventados.')


def build_ui():
    with gr.Blocks(title='Fleet Charge - CKP01', analytics_enabled=False) as demo:
        gr.Markdown('# Assistente Fleet Charge Intelligence\n'
                    'Consulta e explicacao de recarga de frotas. '
                    '**Nao executa planejamento nem controla equipamentos.**')
        # Cada sessao do navegador possui sua propria memoria.
        session = gr.State(value=None)
        chat = gr.Chatbot(label='Conversa', height=380)
        message = gr.Textbox(label='Sua pergunta', placeholder='O que significa MMS de 2 horas?')
        with gr.Row():
            send = gr.Button('Enviar', variant='primary')
            clear = gr.Button('Nova conversa')
        status = gr.Markdown('Configure sua chave somente no .env local.')
        structured = gr.JSON(label='Analise estruturada - validada pelo schema, nao pelo motor')
        inputs, outputs = [message, chat, session], [message, chat, session, structured, status]
        # Serializar envio, Enter e limpeza evita disputar a mesma memoria.
        # No prototipo, a fila e compartilhada entre sessoes; prioriza consistencia.
        send.click(respond, inputs, outputs, concurrency_limit=1,
                   concurrency_id='conversation', trigger_mode='once')
        message.submit(respond, inputs, outputs, concurrency_limit=1,
                       concurrency_id='conversation', trigger_mode='once')
        clear.click(lambda: ('', [], None, None, 'Memoria reiniciada.'), outputs=outputs,
                    concurrency_limit=1, concurrency_id='conversation', queue=True)
    return demo


if __name__ == '__main__':
    build_ui().queue().launch(server_name='127.0.0.1', server_port=7860, share=False,
                              show_error=False)
