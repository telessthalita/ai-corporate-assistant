
from unittest.mock import patch

import pytest
import requests

from app.core.monitoramento import monitorar_operacao


def test_timeout_ollama_gera_log_e_preserva_erro():
    def simular_timeout():
        raise requests.exceptions.Timeout(
            "Ollama demorou para responder"
        )

    with patch(
        "app.core.monitoramento.logger.error"
    ) as log_erro:

        with pytest.raises(requests.exceptions.Timeout):
            monitorar_operacao(
                "classificacao_ia",
                simular_timeout
            )

    log_erro.assert_called_once()

    evento = log_erro.call_args.kwargs["extra"]

    assert evento["evento"] == "classificacao_ia"
    assert evento["status"] == "erro"
    assert evento["duracao_ms"] >= 0
    
def test_timeout_ollama_preserva_chamado(
    client_analyst
):
    from unittest.mock import patch
    import requests

    client = client_analyst

    # 1. Cadastrar chamado
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema indisponível"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    # 2. Simular timeout do Ollama
    with patch(
        "app.services.chamados.analisar_chamado_json",
        side_effect=requests.exceptions.Timeout(
            "Ollama demorou para responder"
        )
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    # 3. API deve tratar a falha
    assert resposta.status_code == 502

    # 4. Verificar integridade do banco
    consulta = client.get("/chamados")

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["categoria"] is None
    assert chamado["prioridade"] is None
    assert chamado["status"] == "aberto"
    
def test_resposta_invalida_ia_preserva_chamado(
    client_analyst
):
    from unittest.mock import patch

    client = client_analyst

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Erro no sistema corporativo"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    # Simular resposta inválida da IA.
    resposta_invalida = {
        "categoria": "desconhecida",
        "prioridade": "urgente",
        "resumo": "Erro no sistema"
    }

    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value=resposta_invalida
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert resposta.status_code == 502

    # Garantir que os dados originais foram preservados.
    consulta = client.get("/chamados")

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["categoria"] is None
    assert chamado["prioridade"] is None
    assert chamado["status"] == "aberto"
    
def test_recuperacao_apos_falha_ollama(client_analyst):
    from unittest.mock import patch
    import requests

    client = client_analyst

    # 1. Criar chamado.
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Não consigo acessar meu e-mail"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    # 2. Simular falha temporária do Ollama.
    with patch(
        "app.services.chamados.analisar_chamado_json",
        side_effect=requests.exceptions.ConnectionError(
            "Ollama indisponível"
        )
    ):
        primeira = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert primeira.status_code == 502

    # 3. Simular recuperação da IA.
    resposta_ia = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Falha de acesso ao e-mail"
    }

    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value=resposta_ia
    ):
        segunda = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert segunda.status_code == 200

    # 4. Verificar estado final do chamado.
    consulta = client.get("/chamados")

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["categoria"] == "suporte"
    assert chamado["prioridade"] is None
    assert chamado["status"] == "revisao"
