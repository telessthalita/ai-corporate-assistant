
import pytest

from app.services.revisao import precisa_revisao


@pytest.mark.parametrize(
    "texto, esperado",
    [
        (
            "Minha conta foi bloqueada "
            "depois de uma tentativa de pagamento.",
            True
        ),
        (
            "Não consigo acessar minhas faturas.",
            True
        ),
        (
            "Preciso da segunda via do boleto.",
            False
        ),
        (
            "Quero contratar um novo plano.",
            False
        ),
        (
            "Não consigo acessar meu e-mail.",
            False
        )
    ]
)
def test_precisa_revisao(texto, esperado):
    assert precisa_revisao(texto) is esperado
