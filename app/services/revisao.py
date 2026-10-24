
def precisa_revisao(texto: str) -> bool:
    texto = texto.lower()

    termos_acesso = [
        "acessar",
        "acesso",
        "entrar",
        "bloqueada",
        "bloqueado",
        "login"
    ]

    termos_financeiros = [
        "pagamento",
        "boleto",
        "fatura",
        "cobrança",
        "mensalidade"
    ]

    tem_acesso = any(
        termo in texto
        for termo in termos_acesso
    )

    tem_financeiro = any(
        termo in texto
        for termo in termos_financeiros
    )

    return tem_acesso and tem_financeiro
