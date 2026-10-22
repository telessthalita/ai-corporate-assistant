
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, obter_db
from models import Chamado


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
