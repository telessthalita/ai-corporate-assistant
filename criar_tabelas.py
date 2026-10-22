
from database import Base, engine
from models import Chamado


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas com sucesso!")


if __name__ == "__main__":
    criar_tabelas()
