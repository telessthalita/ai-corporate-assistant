
import pytest

from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.chamado import Chamado
from app.models.auditoria import AuditoriaChamado
from app.repositories.chamados import salvar_prioridade


def test_rollback_se_auditoria_falhar():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    try:
        with Session(engine) as db:
            chamado = Chamado(
                descricao="Sistema indisponível",
                prioridade="baixa"
            )

            db.add(chamado)
            db.commit()

            chamado_id = chamado.id

        # Simula falha do banco ao inserir a auditoria.
        def bloquear_auditoria(
            conn, cursor, statement, parameters, context,
            executemany
        ):
            if (
                statement.lstrip().upper().startswith("INSERT")
                and "auditoria_chamados" in statement.lower()
            ):
                raise IntegrityError(
                    statement,
                    parameters,
                    Exception("Falha simulada na auditoria")
                )

        event.listen(
            engine,
            "before_cursor_execute",
            bloquear_auditoria
        )

        with Session(engine) as db:
            chamado = db.get(Chamado, chamado_id)

            with pytest.raises(IntegrityError):
                salvar_prioridade(db, chamado, "alta")

        event.remove(
            engine,
            "before_cursor_execute",
            bloquear_auditoria
        )

        # Nova sessão: verifica o estado persistido.
        with Session(engine) as db:
            chamado = db.get(Chamado, chamado_id)

            auditorias = db.scalars(
                select(AuditoriaChamado)
            ).all()

            assert chamado.prioridade == "baixa"
            assert auditorias == []

    finally:
        engine.dispose()
