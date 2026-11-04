
import json
import logging
import sys

from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):

    def format(self, record):
        dados = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "nivel": record.levelname,
            "logger": record.name,
            "mensagem": record.getMessage()
        }

        for campo in (
            "evento",
            "status",
            "duracao_ms"
        ):
            if hasattr(record, campo):
                dados[campo] = getattr(
                    record,
                    campo
                )

        if record.exc_info:
            dados["excecao"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            dados,
            ensure_ascii=False
        )


def configurar_logs():
    logger = logging.getLogger(
        "ai_corporate_assistant"
    )

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    logger.propagate = False

    return logger
