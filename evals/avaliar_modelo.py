
import json
from pathlib import Path

from app.services.ia import analisar_chamado_json
from app.schemas.chamado import ClassificacaoChamado


ARQUIVO = Path(__file__).with_name(
    "chamados_avaliacao.json"
)


def avaliar():
    casos = json.loads(
        ARQUIVO.read_text(encoding="utf-8")
    )

    acertos = 0
    erros = 0
    falhas = 0
    resultados = []

    for caso in casos:
        try:
            resposta = analisar_chamado_json(
                caso["texto"]
            )

            classificacao = (
                ClassificacaoChamado.model_validate(
                    resposta
                )
            )

            prevista = classificacao.categoria
            esperada = caso["categoria_esperada"]
            resultados.append({
                "esperada": esperada,
                "prevista": prevista,
            })
            if prevista == esperada:
                acertos += 1
                resultado = "ACERTO"
            else:
                erros += 1
                resultado = "ERRO"

            print(
                f"Caso {caso['id']}: "
                f"esperada={esperada} | "
                f"prevista={prevista} | "
                f"{resultado}",
                flush=True
            )

        except Exception as erro:
            falhas += 1
            print(
                f"Caso {caso['id']}: "
                f"FALHA ({type(erro).__name__})",
                flush=True
            )

    total = len(casos)

    if total == 0:
        print("Dataset vazio.")
        return

    print("\n--- RESULTADO FINAL ---")
    print(f"Total: {total}")
    print(f"Acertos: {acertos}")
    print(f"Erros: {erros}")
    print(f"Falhas: {falhas}")
    print(f"Acurácia geral: {acertos / total * 100:.1f}%")

    
    print("\n--- MÉTRICAS POR CATEGORIA ---")

    categorias = [
        "suporte",
        "financeiro",
        "comercial"
    ]

    for categoria in categorias:
        vp = sum(
            1 for item in resultados
            if item["esperada"] == categoria
            and item["prevista"] == categoria
        )

        fp = sum(
            1 for item in resultados
            if item["esperada"] != categoria
            and item["prevista"] == categoria
        )

        fn = sum(
            1 for item in resultados
            if item["esperada"] == categoria
            and item["prevista"] != categoria
        )

        precisao = vp / (vp + fp) if vp + fp else 0
        recall = vp / (vp + fn) if vp + fn else 0

        f1 = (
            2 * precisao * recall / (precisao + recall)
            if precisao + recall else 0
        )

        print(
            f"{categoria}: "
            f"Precisão={precisao:.1%} | "
            f"Recall={recall:.1%} | "
            f"F1={f1:.1%}"
        )
        
    print("\n--- MATRIZ DE CONFUSÃO ---")

    categorias = [
        "suporte",
        "financeiro",
        "comercial"
    ]

    print(
        f"{'Esperada / Prevista':<22}"
        + "".join(
            f"{categoria:>12}"
            for categoria in categorias
        )
    )

    for esperada in categorias:
        linha = []

        for prevista in categorias:
            quantidade = sum(
                1 for item in resultados
                if item["esperada"] == esperada
                and item["prevista"] == prevista
            )

            linha.append(quantidade)

        print(
            f"{esperada:<22}"
            + "".join(
                f"{valor:>12}"
                for valor in linha
            )
        )


    

if __name__ == "__main__":
    avaliar()
