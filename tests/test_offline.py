"""Offline structural tests; fake outputs do not validate Gemma behavior."""
import json
import subprocess
import sys
import unittest

from langchain_classic.chains import ConversationChain
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.runnables import RunnableSequence

from app.chain import MODEL, build_chat, build_structured
from app.memory_manager import build_memory, token_ids
from app.schemas import AnaliseConsulta


def fake(responses=None):
    return FakeListChatModel(responses=responses or ['Resposta simulada.'],
                             custom_get_token_ids=token_ids)


def payload():
    return dict(tema='margem', resumo='Consulta sobre a margem de seguranca.',
                modo_citado='equilibrado', dados_faltantes=['Horario de saida'],
                alertas=['Nao ha verificacao de cronograma.'],
                proximo_passo='Solicitar os dados ao gestor.',
                natureza='analise_consultiva_nao_validada',
                requer_decisao_humana=True)


class OfflineTests(unittest.TestCase):
    def test_conversation_chain_retains_six_short_turns(self):
        chain = build_chat(fake(), limit=1200)
        self.assertIsInstance(chain, ConversationChain)
        for index in range(6):
            chain.invoke({'input': f'Pergunta curta {index}'})
        messages = chain.memory.chat_memory.messages
        self.assertEqual(len(messages), 12)
        self.assertEqual(messages[0].content, 'Pergunta curta 0')
        self.assertEqual(messages[-2].content, 'Pergunta curta 5')

    def test_six_long_turns_prune_to_1200_proxy_tokens(self):
        model = fake(['Resposta extensa ' + 'energia ' * 300])
        chain = build_chat(model, limit=1200)
        for index in range(6):
            chain.invoke({'input': f'MARCADOR_{index} ' + 'recarga ' * 300})
        messages = chain.memory.chat_memory.messages
        text = '\n'.join(m.content for m in messages)
        self.assertLessEqual(model.get_num_tokens_from_messages(messages), 1200)
        self.assertNotIn('MARCADOR_0', text)
        self.assertIn('MARCADOR_5', text)
        self.assertLess(len(messages), 12)

    def test_sessions_have_independent_memory(self):
        first, second = build_chat(fake()), build_chat(fake())
        first.invoke({'input': 'IDENTIFICADOR_SESSAO_A'})
        second.invoke({'input': 'IDENTIFICADOR_SESSAO_B'})
        self.assertIsNot(first.memory, second.memory)
        self.assertNotIn('IDENTIFICADOR_SESSAO_A', str(second.memory.chat_memory.messages))
        self.assertNotIn('IDENTIFICADOR_SESSAO_B', str(first.memory.chat_memory.messages))

    def test_lcel_parses_valid_fake_json(self):
        chain = build_structured(fake([json.dumps(payload())]))
        self.assertIsInstance(chain, RunnableSequence)
        result = chain.invoke({'input': 'Qual a MMS?', 'history': ''})
        self.assertIsInstance(result, AnaliseConsulta)
        self.assertEqual(result.natureza, 'analise_consultiva_nao_validada')

    def test_lcel_rejects_invalid_fake_json(self):
        invalid_values = ['nao e JSON', '{}',
                          json.dumps(dict(payload(), requer_decisao_humana=False)),
                          json.dumps(dict(payload(), cronograma_validado=True))]
        for value in invalid_values:
            with self.subTest(value=value):
                chain = build_structured(fake([value]))
                with self.assertRaises(OutputParserException):
                    chain.invoke({'input': 'Pergunta', 'history': ''})

    def test_schema_has_at_least_four_required_fields(self):
        schema = AnaliseConsulta.model_json_schema()
        self.assertGreaterEqual(len(schema['required']), 4)
        self.assertFalse(schema['additionalProperties'])

    def test_memory_limit_domain(self):
        for invalid in (799, 1501):
            with self.assertRaises(ValueError):
                build_memory(fake(), invalid)

    def test_model_literal_is_preserved(self):
        self.assertEqual(MODEL, 'gemma4:cloud')

    def test_gradio_build_does_not_construct_cloud_client(self):
        # Native UI dependencies run separately so a crash remains a test failure.
        script = '''
from unittest.mock import patch
from app.main import build_ui
with patch('app.main.build_llm', side_effect=AssertionError('Cloud disabled')):
    demo = build_ui()
assert demo.config['components']
demo.close()
'''
        result = subprocess.run([sys.executable, '-X', 'faulthandler', '-c', script],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr[-4000:])


if __name__ == '__main__':
    unittest.main(verbosity=2)
