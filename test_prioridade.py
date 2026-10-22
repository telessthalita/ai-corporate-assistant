
import pytest

from prioridade import definir_prioridade


@pytest.mark.parametrize(
    "impacto, bloqueia, rotineira, esperado",
    [
        ("critico", True, False, "alta"),
        ("moderado", True, False, "media"),
        ("baixo", False, True, "baixa"),
        ("desconhecido", False, False, None),
    ]
)
def test_definir_prioridade(
    impacto, bloqueia, rotineira, esperado
):
    resultado = definir_prioridade(
        impacto=impacto,
        bloqueia_trabalho=bloqueia,
        solicitacao_rotineira=rotineira
    )

    assert resultado == esperado


from prioridade import decidir_encaminhamento


def test_revisao_humana():
    resultado = decidir_encaminhamento(None)

    assert resultado == "Revisão humana necessária"


def test_prioridade_definida():
    resultado = decidir_encaminhamento("alta")

    assert resultado == "Prioridade definida: alta"
