from app.core.database import Base, engine
import app.models.chamado  # noqa: F401 (registra o modelo no Base)


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas com sucesso!")


if __name__ == "__main__":
    criar_tabelas()
