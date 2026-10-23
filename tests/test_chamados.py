from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, obter_db
from app.main import app


@pytest.fixture
def client():
    engine_teste = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False
        },
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine_teste)

    SessaoTeste = sessionmaker(
        bind=engine_teste
    )

    def obter_db_teste():
        with SessaoTeste() as db:
            yield db

    app.dependency_overrides[obter_db] = obter_db_teste

    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.clear()
        engine_teste.dispose()


def test_criar_chamado(client):
    resposta = client.post(
        "/chamados",
        json={
            "descricao": "Erro no login do sistema"
        }
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["descricao"] == "Erro no login do sistema"
    assert dados["status"] == "aberto"
    assert dados["id"] is not None


def test_listar_chamados(client):
    client.post(
        "/chamados",
        json={
            "descricao": "Computador não liga"
        }
    )

    resposta = client.get("/chamados")

    assert resposta.status_code == 200

    chamados = resposta.json()

    assert len(chamados) == 1
    assert chamados[0]["descricao"] == "Computador não liga"

def test_falha_ollama_preserva_chamado(client):
    # 1. Criar o chamado
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Não consigo acessar o e-mail"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    # 2. Simular falha do Ollama
    with patch(
        "app.services.chamados.analisar_chamado_json",
        side_effect=requests.exceptions.ConnectionError(
            "Ollama indisponível"
        )
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    # 3. Verificar o erro controlado
    assert resposta.status_code == 502

    # 4. Confirmar que o chamado continua salvo
    consulta = client.get("/chamados")

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["descricao"] == (
        "Não consigo acessar o e-mail"
    )

    assert chamado["categoria"] is None
    assert chamado["prioridade"] is None
    assert chamado["status"] == "aberto"


def test_nao_classificar_duas_vezes(client):
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Erro ao acessar o sistema"
        }
    )

    assert criacao.status_code == 201
    chamado_id = criacao.json()["id"]

    resposta_ia = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso ao sistema"
    }

    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value=resposta_ia
    ) as modelo:

        primeira = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

        segunda = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert primeira.status_code == 200
    assert segunda.status_code == 200

    # O modelo deve ser executado somente uma vez
    assert modelo.call_count == 1

    # As duas respostas devem representar o mesmo registro
    assert primeira.json()["id"] == segunda.json()["id"]
    assert segunda.json()["categoria"] == "suporte"
