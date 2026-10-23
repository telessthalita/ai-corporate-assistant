from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_validar_sucesso():
    resposta = client.post(
        "/validar",
        json={
            "categoria": "suporte",
            "confianca": 0.92
        }
    )

    assert resposta.status_code == 200
    assert resposta.json()["resultado"] == "Aprovado"

def test_confianca_string():
    resposta = client.post(
        "/validar",
        json={
            "categoria": "suporte",
            "confianca": "0.92"
        }
    )

    assert resposta.status_code == 422


def test_confianca_fora_intervalo():
    resposta = client.post(
        "/validar",
        json={
            "categoria": "suporte",
            "confianca": 1.5
        }
    )

    assert resposta.status_code == 422
    
    


def test_classificar_chamado():
    resposta_simulada = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso ao e-mail"
    }

    with patch(
        "app.main.analisar_chamado_json",
        return_value=resposta_simulada
    ):
        resposta = client.post(
            "/classificar",
            json={
                "texto": "Não consigo acessar meu e-mail."
            }
        )

    assert resposta.status_code == 200

    assert resposta.json() == resposta_simulada
