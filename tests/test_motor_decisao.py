
import pytest

from app.services.motor_decisao import avaliar_prioridade


@pytest.mark.parametrize(
    "impacto, bloqueia, rotineira, esperada",
    [
        ("critico", True, False, "alta"),
        ("moderado", True, False, "media"),
        ("baixo", False, True, "baixa")
    ]
)
def test_prioridade_definida(
    impacto, bloqueia, rotineira, esperada
):
    resultado = avaliar_prioridade(
        impacto,
        bloqueia,
        rotineira
    )

    assert resultado["prioridade"] == esperada
    assert resultado["revisao_humana"] is False


def test_informacoes_insuficientes():
    resultado = avaliar_prioridade(
        impacto=None,
        bloqueia_trabalho=None,
        solicitacao_rotineira=None
    )

    assert resultado["prioridade"] is None
    assert resultado["revisao_humana"] is True


def test_regra_nao_aplicavel():
    resultado = avaliar_prioridade(
        impacto="moderado",
        bloqueia_trabalho=False,
        solicitacao_rotineira=False
    )

    assert resultado["prioridade"] is None
    assert resultado["revisao_humana"] is True
