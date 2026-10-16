
from validacao import validar_resposta


def test_confianca_alta():
    resposta = {"confianca": 0.92}

    resultado = validar_resposta(resposta)

    assert resultado == "Aprovado"
    

def test_confianca_baixa():
    resposta = {"confianca": 0.5}

    resultado = validar_resposta(resposta)

    assert resultado == "Revisão necessária"
    

def test_confianca_invalida():
    resposta = {"confianca": True}

    resultado = validar_resposta(resposta)

    assert resultado == "Erro: Confiança deve ser numérica"


def test_limite_personalizado():
    resposta = {"confianca": 0.75}
    limite = 0.7

    resultado = validar_resposta(resposta, limite)

    assert resultado == "Aprovado"
    


import pytest

@pytest.mark.parametrize(
    "confianca, esperado",
    [
        (0.92, "Aprovado"),
        (0.50, "Revisão necessária"),
        (True, "Erro: Confiança deve ser numérica"),
        (1.5, "Erro: Confiança fora do intervalo"),
        (0.8, "Aprovado"),
        ("0.92", "Erro: Confiança deve ser numérica"),
        (float("nan"), "Erro: Confiança fora do intervalo"),

    ]
)
def test_multiplos_cenarios(confianca, esperado):

    resposta = {"confianca": confianca}

    resultado = validar_resposta(resposta)

    assert resultado == esperado
