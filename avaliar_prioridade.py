
from servico_ia import analisar_chamado_json


casos = [
    (
        "O sistema de pagamentos está fora "
        "do ar para todos os clientes.",
        "alta"
    ),
    (
        "Não consigo acessar meu e-mail "
        "corporativo desde ontem.",
        "media"
    ),
    (
        "Gostaria de solicitar uma segunda "
        "via da nota fiscal.",
        "baixa"
    )
]

acertos = 0

for texto, esperado in casos:
    resposta = analisar_chamado_json(texto)
    obtido = resposta["prioridade"].strip().lower()

    correto = obtido == esperado
    acertos += int(correto)

    print(f"\nChamado: {texto}")
    print(f"Esperado: {esperado}")
    print(f"Obtido: {obtido}")
    print("PASSOU" if correto else "FALHOU")

print(f"\nPrioridades corretas: {acertos}/{len(casos)}")
