
from servico_ia import analisar_chamado

chamados = [
    ("Não consigo acessar meu e-mail.", "suporte"),
    ("Preciso da segunda via da fatura.", "financeiro"),
    ("Gostaria de solicitar um orçamento.", "comercial"),
    ("O sistema apresenta erro no login.", "suporte")
]

acertos = 0

for texto, esperado in chamados:
    resultado = analisar_chamado(texto).strip().lower()

    acertou = resultado == esperado

    if acertou:
        acertos += 1

    print(f"\nChamado: {texto}")
    print(f"Esperado: {esperado}")
    print(f"Obtido: {resultado}")
    print(f"Resultado: {'PASSOU' if acertou else 'FALHOU'}")

print(f"\nTotal: {acertos}/{len(chamados)} acertos")
