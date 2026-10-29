from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.chamado import Chamado

from app.models.auditoria import AuditoriaChamado

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

    prioridade_anterior = chamado.prioridade

    # Evita registrar uma alteração inexistente
    if prioridade_anterior == prioridade:
        return chamado

    chamado.prioridade = prioridade

    auditoria = AuditoriaChamado(
        chamado_id=chamado.id,
        acao="prioridade_alterada",
        valor_anterior=prioridade_anterior,
        valor_novo=prioridade,
        origem="motor_regras",
        motivo="Prioridade definida por regras de negócio"
    )

    db.add(auditoria)

    try:
        # Uma única confirmação para as duas alterações
        db.commit()
        db.refresh(chamado)

    except Exception:
        db.rollback()
        raise

    return chamado


def listar_auditoria(
    db: Session,
    chamado_id: int
) -> list[AuditoriaChamado]:

    consulta = (
        select(AuditoriaChamado)
        .where(AuditoriaChamado.chamado_id == chamado_id)
        .order_by(
            AuditoriaChamado.criado_em.asc(),
            AuditoriaChamado.id.asc()
        )
    )

    return list(db.scalars(consulta).all())
