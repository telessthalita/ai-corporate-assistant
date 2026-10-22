
from typing import Literal

Prioridade = Literal["baixa", "media", "alta"]


def definir_prioridade(
    impacto: str,
    bloqueia_trabalho: bool,
    solicitacao_rotineira: bool
) -> Prioridade | None:

    if impacto == "critico":
        return "alta"

    if bloqueia_trabalho:
        return "media"

    if solicitacao_rotineira and impacto == "baixo":
        return "baixa"

    return None


def decidir_encaminhamento(prioridade):
    if prioridade is None:
        return "Revisão humana necessária"

    return f"Prioridade definida: {prioridade}"
