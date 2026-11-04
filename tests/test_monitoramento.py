
from unittest.mock import patch

from app.services.ia import analisar_chamado_monitorado
from app.core.logging_config import JSONFormatter

import json
import logging

import pytest
import requests

from unittest.mock import patch

from app.core.monitoramento import logger

def test_classificacao_monitorada():
    resposta_simulada = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso"
    }

    with patch(
        "app.services.ia.analisar_chamado_json",
        return_value=resposta_simulada
    ) as modelo:
        resultado = analisar_chamado_monitorado(
            "Não consigo acessar meu e-mail."
        )

    assert resultado == resposta_simulada
    modelo.assert_called_once_with(
        "Não consigo acessar meu e-mail.",
        prompt_base=None
    )


def test_classificacao_monitorada_registra_falha(caplog):
    from app.core.monitoramento import logger
    from app.services.ia import analisar_chamado_monitorado

    erro = requests.exceptions.ConnectionError(
        "Ollama indisponível"
    )

    with patch(
        "app.services.ia.analisar_chamado_json",
        side_effect=erro
    ):
        with patch.object(logger, "error") as log_erro:
            with pytest.raises(requests.exceptions.ConnectionError):
                analisar_chamado_monitorado(
                    "Não consigo acessar o sistema."
                )

    log_erro.assert_called_once()

    argumentos = log_erro.call_args.kwargs

    assert argumentos["extra"]["evento"] == "classificacao_ia"
    assert argumentos["extra"]["status"] == "erro"
    assert argumentos["extra"]["duracao_ms"] >= 0

def test_api_classificacao_gera_log(client_analyst):
    resposta_ia = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso"
    }

    with patch(
        "app.main.analisar_chamado_json",
        return_value=resposta_ia
    ):
        with patch.object(logger, "info") as log_info:
            resposta = client_analyst.post(
                "/classificar",
                json={
                    "texto": "Não consigo acessar meu e-mail."
                }
            )

    assert resposta.status_code == 200

    log_info.assert_called_once()

    evento = log_info.call_args.kwargs["extra"]

    assert evento["evento"] == "classificacao_ia"
    assert evento["status"] == "sucesso"
    assert isinstance(evento["duracao_ms"], (int, float))
    assert evento["duracao_ms"] >= 0
def test_logger_gera_json_valido():
    formatter = JSONFormatter()

    registro = logging.LogRecord(
        name="ai_corporate_assistant",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Operação finalizada com sucesso",
        args=(),
        exc_info=None,
    )

    registro.evento = "classificacao_ia"
    registro.status = "sucesso"
    registro.duracao_ms = 125.5

    mensagem = formatter.format(registro)
    dados = json.loads(mensagem)

    assert dados["nivel"] == "INFO"
    assert dados["evento"] == "classificacao_ia"
    assert dados["status"] == "sucesso"
    assert dados["duracao_ms"] == 125.5
    assert "timestamp" in dados
