
from fastapi import HTTPException
from app.core.security import exigir_admin
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.security import autenticar_usuario, exigir_admin

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




@pytest.fixture
def client_analyst(client):
    app.dependency_overrides[autenticar_usuario] = (
        lambda: "analyst"
    )

    try:
        yield client
    finally:
        app.dependency_overrides.pop(
            autenticar_usuario, None
        )


@pytest.fixture
def client_admin(client):
    app.dependency_overrides[autenticar_usuario] = (
        lambda: "admin"
    )
    app.dependency_overrides[exigir_admin] = (
        lambda: "admin"
    )

    try:
        yield client
    finally:
        app.dependency_overrides.pop(
            autenticar_usuario, None
        )
        app.dependency_overrides.pop(
            exigir_admin, None
        )
