
import time

from app.core.logging_config import configurar_logs


logger = configurar_logs()


def monitorar_operacao(nome_operacao, funcao, *args, **kwargs):
    inicio = time.perf_counter()

    try:
        resultado = funcao(*args, **kwargs)

    except Exception:
        duracao_ms = round(
            (time.perf_counter() - inicio) * 1000,
            2
        )

        logger.error(
            "Operação finalizada com erro",
            extra={
                "evento": nome_operacao,
                "status": "erro",
                "duracao_ms": duracao_ms
            }
        )

        raise

    duracao_ms = round(
        (time.perf_counter() - inicio) * 1000,
        2
    )

    logger.info(
        "Operação finalizada com sucesso",
        extra={
            "evento": nome_operacao,
            "status": "sucesso",
            "duracao_ms": duracao_ms
        }
    )

    return resultado
