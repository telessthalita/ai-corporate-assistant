
import json
from pathlib import Path

from app.services.ia import analisar_chamado_json
from app.schemas.chamado import ClassificacaoChamado


RAIZ = Path(__file__).resolve().parent.parent
PASTA_PROMPTS = RAIZ / "prompts"

ARQUIVO_TESTE = (
    RAIZ / "evals" / "chamados_teste_independente.json"
)


def carregar_prompt(versao: str) -> str:
    caminho = PASTA_PROMPTS / f"classificacao_{versao}.txt"
    return caminho.read_text(encoding="utf-8")


def avaliar_versao(versao: str, casos: list[dict]) -> dict:
    prompt = carregar_prompt(versao)

    acertos = 0
    erros = 0
    falhas = 0

    print(f"\n--- PROMPT {versao.upper()} ---")

    for caso in casos:
        try:
            resposta = analisar_chamado_json(
                caso["texto"],
                prompt_base=prompt
            )

            classificacao = ClassificacaoChamado.model_validate(
                resposta
            )

            prevista = classificacao.categoria
            esperada = caso["categoria_esperada"]

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

    return {
        "versao": versao,
        "acertos": acertos,
        "erros": erros,
        "falhas": falhas,
        "acuracia": acertos / total * 100 if total else 0
    }


def comparar():
    casos = json.loads(
        ARQUIVO_TESTE.read_text(encoding="utf-8")
    )

    if not casos:
        print("Dataset vazio.")
        return

    resultado_v1 = avaliar_versao("v1", casos)
    resultado_v2 = avaliar_versao("v2", casos)

    print("\n--- COMPARAÇÃO FINAL ---")

    print(f"{'Métrica':<18} {'V1':>10} {'V2':>10}")

    for campo in ("acertos", "erros", "falhas"):
        print(
            f"{campo:<18} "
            f"{resultado_v1[campo]:>10} "
            f"{resultado_v2[campo]:>10}"
        )

    print(
        f"{'Acurácia':<18} "
        f"{resultado_v1['acuracia']:>9.1f}% "
        f"{resultado_v2['acuracia']:>9.1f}%"
    )


if __name__ == "__main__":
    comparar()
