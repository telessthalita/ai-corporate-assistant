
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Chamado


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
