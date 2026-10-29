from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chamado import Chamado


def criar_chamado(
    db: Session,
    descricao: str
) -> Chamado:

    chamado = Chamado(descricao=descricao)

    db.add(chamado)

    db.commit()

    db.refresh(chamado)

    return chamado


def listar_chamados(
    db: Session
) -> list[Chamado]:

    consulta = (
        select(Chamado)
        .order_by(Chamado.id.desc())
        .limit(100)
    )

    return list(
        db.scalars(consulta).all()
    )

def buscar_chamado(db: Session, chamado_id: int):
    return db.get(Chamado, chamado_id)


def atualizar_classificacao(
    db: Session,
    chamado: Chamado,
    categoria: str
):
    chamado.categoria = categoria

    # A classificação da IA não altera prioridades existentes.
    #Somente o motor de regras pode definir esse campo.
    chamado.status = "revisao"

    try:
        db.commit()
        db.refresh(chamado)
    except Exception:
        db.rollback()
        raise

    return chamado

def salvar_prioridade(
    db: Session,
    chamado: Chamado,
    prioridade: str
) -> Chamado:
    chamado.prioridade = prioridade

    try:
        db.commit()
        db.refresh(chamado)
    except Exception:
        db.rollback()
        raise

    return chamado
