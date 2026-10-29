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

def test_endpoint_prioridade_alta(client):
    criacao = client.post(
        "/chamados",
        json={"descricao": "Sistema corporativo indisponível"}
    )

    assert criacao.status_code == 201
    chamado_id = criacao.json()["id"]

    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["prioridade"] == "alta"
    assert dados["revisao_humana"] is False


def test_endpoint_prioridade_revisao(client):
    criacao = client.post(
        "/chamados",
        json={"descricao": "Problema de acesso ao sistema"}
    )

    assert criacao.status_code == 201
    chamado_id = criacao.json()["id"]

    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": None,
            "bloqueia_trabalho": None,
            "solicitacao_rotineira": None
        }
    )

    assert resposta.status_code == 200
    assert resposta.json()["prioridade"] is None
    assert resposta.json()["revisao_humana"] is True


def test_endpoint_prioridade_chamado_inexistente(client):
    resposta = client.post(
        "/chamados/999999/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert resposta.status_code == 404

from unittest.mock import patch


def test_classificacao_preserva_prioridade(client):
    # Cadastra o chamado
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema indisponível para toda a equipe"
        }
    )

    assert criacao.status_code == 201
    chamado_id = criacao.json()["id"]

    # Define a prioridade pelas regras de negócio
    decisao = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert decisao.status_code == 200
    assert decisao.json()["prioridade"] == "alta"

    # Simula uma classificação posterior do Ollama
    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value={
            "categoria": "suporte",
            "prioridade": "baixa",
            "resumo": "Sistema indisponível para a equipe"
        }
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert resposta.status_code == 200

    # Verifica a prioridade persistida
    consulta = client.get("/chamados")

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["prioridade"] == "alta"
    assert chamado["categoria"] == "suporte"

def test_revisao_nao_apaga_prioridade(client):
    # 1. Criar um chamado
    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema indisponível para a equipe"
        }
    )

    assert criacao.status_code == 201
    chamado_id = criacao.json()["id"]

    # 2. Definir prioridade pelas regras
    primeira = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert primeira.status_code == 200
    assert primeira.json()["prioridade"] == "alta"

    # 3. Tentar avaliar sem informações suficientes
    segunda = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": None,
            "bloqueia_trabalho": None,
            "solicitacao_rotineira": None
        }
    )

    assert segunda.status_code == 200
    assert segunda.json()["revisao_humana"] is True
    assert segunda.json()["prioridade"] is None

    # 4. Confirmar que o banco preservou a prioridade
    consulta = client.get("/chamados")

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["prioridade"] == "alta"
