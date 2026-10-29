
from app.services.prioridade import definir_prioridade


def avaliar_prioridade(
    impacto: str | None,
    bloqueia_trabalho: bool | None,
    solicitacao_rotineira: bool | None
) -> dict:

    # Informações insuficientes exigem revisão humana.
    if (
        impacto is None
        or bloqueia_trabalho is None
        or solicitacao_rotineira is None
    ):
        return {
            "prioridade": None,
            "revisao_humana": True,
            "motivo": "Informações insuficientes"
        }

    prioridade = definir_prioridade(
        impacto=impacto,
        bloqueia_trabalho=bloqueia_trabalho,
        solicitacao_rotineira=solicitacao_rotineira
    )

    if prioridade is None:
        return {
            "prioridade": None,
            "revisao_humana": True,
            "motivo": "Nenhuma regra aplicável"
        }

    return {
        "prioridade": prioridade,
        "revisao_humana": False,
        "motivo": "Prioridade definida por regra"
    }
