from app.services.ia import analisar_chamado_json

chamados = [
    ("Não consigo acessar meu e-mail.", "suporte"),
    ("Preciso da segunda via da fatura.", "financeiro"),
    ("Quero solicitar um orçamento.", "comercial"),
    ("Meu computador não está ligando.", "suporte"),
    ("Preciso solicitar um reembolso.", "financeiro"),
    ("Gostaria de conhecer os planos comerciais.", "comercial"),
    ("O sistema apresenta erro no login.", "suporte"),
    ("A nota fiscal veio com valor incorreto.", "financeiro"),
    ("Quero negociar um novo contrato.", "comercial"),
    ("Não consigo conectar à internet.", "suporte"),
]

acertos = 0

for numero, (texto, esperado) in enumerate(
    chamados, start=1
):
    resposta = analisar_chamado_json(texto)
    obtido = resposta["categoria"].strip().lower()

    correto = obtido == esperado

    if correto:
        acertos += 1

    print(f"\nCaso {numero}")
    print(f"Chamado: {texto}")
    print(f"Esperado: {esperado}")
    print(f"Obtido: {obtido}")
    print("PASSOU" if correto else "FALHOU")

total = len(chamados)
acuracia = acertos / total * 100

print(f"\nResultado: {acertos}/{total}")
print(f"Acurácia: {acuracia:.1f}%")
