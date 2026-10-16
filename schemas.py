
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ClassificacaoChamado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    categoria: Literal[
        "suporte",
        "financeiro",
        "comercial"
    ]

    prioridade: Literal[
        "baixa",
        "media",
        "alta"
    ]

    resumo: str = Field(min_length=5)
