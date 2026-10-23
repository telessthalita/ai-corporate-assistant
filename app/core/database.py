import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não encontrada no .env"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


def testar_conexao():
    with engine.connect() as conexao:
        resultado = conexao.execute(
            text("SELECT 1")
        )

        return resultado.scalar_one()


def obter_db():
    with SessionLocal() as db:
        yield db
