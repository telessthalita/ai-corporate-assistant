import math


def validar_resposta(resposta: dict, limite: float = 0.8) -> str:
    try:
        if isinstance(limite, bool) or not isinstance(limite, (int, float)):
            raise ValueError("Limite inválido")

        if not math.isfinite(limite) or not 0 <= limite <= 1:
            raise ValueError("Limite inválido")

        confianca = resposta["confianca"]

        if type(confianca) not in (int, float):
            raise ValueError("Confiança deve ser numérica")

        if not math.isfinite(confianca) or not 0 <= confianca <= 1:
            raise ValueError("Confiança fora do intervalo")

        return "Aprovado" if confianca >= limite else "Revisão necessária"

    except (KeyError, TypeError, ValueError) as erro:
        return f"Erro: {erro}"
