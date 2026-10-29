
from app.core.database import Base, engine
from app.models.chamado import Chamado
from app.models.auditoria import AuditoriaChamado


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas com sucesso!")


if __name__ == "__main__":
    criar_tabelas()
