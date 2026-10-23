from sqlalchemy.orm import Session

from app.repositories.chamados import (
    buscar_chamado,
    atualizar_classificacao
)
from app.schemas.chamado import ClassificacaoChamado
from app.services.ia import analisar_chamado_json


def classificar_chamado_salvo(
    db: Session,
    chamado_id: int
):
    chamado = buscar_chamado(db, chamado_id)

    if chamado is None:
        return None

    # Evita repetir classificações já realizadas
    if (
        chamado.status == "revisao"
        and chamado.categoria is not None
    ):
        return chamado

    # Chamada ao modelo local
    dados = analisar_chamado_json(chamado.descricao)

    # Não persistimos dados antes da validação
    classificacao = ClassificacaoChamado.model_validate(
        dados
    )

    return atualizar_classificacao(
        db=db,
        chamado=chamado,
        categoria=classificacao.categoria
    )
