import os
import unittest
from unittest.mock import MagicMock, patch
from google.genai import errors

from app import (
    ErroAplicacao,
    carregar_configuracao,
    chamar_modelo,
    preparar_solicitacao,
    tratar_resposta,
    validar_entrada,
)


class TestFluxoLocalLLM(unittest.TestCase):
    """Testes unitários da lógica local sem chamadas reais à API."""

    def test_validar_entrada_valida(self):
        resultado = validar_entrada("  Reunião amanhã às 10h  ")
        self.assertEqual(resultado, "Reunião amanhã às 10h")

    def test_validar_entrada_vazia(self):
        with self.assertRaises(ErroAplicacao) as contexto:
            validar_entrada("    ")
        self.assertIn("Entrada inválida", str(contexto.exception))

    def test_preparar_solicitacao(self):
        prompt = preparar_solicitacao("Entrega do relatório sexta-feira")
        self.assertIn("Entrega do relatório sexta-feira", prompt)

    @patch("app.load_dotenv")
    @patch.dict(os.environ, {"API_KEY": ""}, clear=True)
    def test_carregar_configuracao_credencial_ausente(self, _mock_dotenv):
        with self.assertRaises(ErroAplicacao) as contexto:
            carregar_configuracao("config.json")
        self.assertIn("Credencial ausente", str(contexto.exception))

    def test_tratar_resposta_simulada_valida(self):
        resposta_simulada = MagicMock()
        resposta_simulada.text = "  Tipo: Lembrete | Data: Amanhã  "
        resultado = tratar_resposta(resposta_simulada)
        self.assertEqual(resultado, "Tipo: Lembrete | Data: Amanhã")

    def test_tratar_resposta_simulada_vazia(self):
        resposta_vazia = MagicMock()
        resposta_vazia.text = "   "
        with self.assertRaises(ErroAplicacao) as contexto:
            tratar_resposta(resposta_vazia)
        self.assertIn("Resposta vazia", str(contexto.exception))

    def test_chamar_modelo_erro_simulado_timeout(self):
        cliente_mock = MagicMock()
        cliente_mock.models.generate_content.side_effect = TimeoutError("Tempo esgotado")
        config_teste = {
            "modelo": "gemini-3.5-flash",
            "temperatura": 0.2,
            "max_output_tokens": 100,
            "instrucao_sistema": "Teste",
        }

        with self.assertRaises(ErroAplicacao) as contexto:
            chamar_modelo(cliente_mock, "Oi", config_teste)
        self.assertIn("Timeout", str(contexto.exception))

    def test_chamar_modelo_erro_simulado_credencial_invalida(self):
        cliente_mock = MagicMock()
        cliente_mock.models.generate_content.side_effect = errors.APIError(
            403, {"error": {"message": "API key not valid"}}
        )
        config_teste = {
            "modelo": "gemini-3.5-flash",
            "temperatura": 0.2,
            "max_output_tokens": 100,
            "instrucao_sistema": "Teste",
        }

        with self.assertRaises(ErroAplicacao) as contexto:
            chamar_modelo(cliente_mock, "Oi", config_teste)
        self.assertIn("Credencial inválida", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()