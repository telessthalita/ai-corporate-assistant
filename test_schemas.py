
import pytest
from pydantic import ValidationError
from schemas import ClassificacaoChamado


def test_classificacao_valida():
    dados = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso ao e-mail"
    }

    resultado = ClassificacaoChamado.model_validate(dados)

    assert resultado.categoria == "suporte"


def test_categoria_invalida():
    dados = {
        "categoria": "outros",
        "prioridade": "media",
        "resumo": "Problema de acesso ao e-mail"
    }

    with pytest.raises(ValidationError):
        ClassificacaoChamado.model_validate(dados)
