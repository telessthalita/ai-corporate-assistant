
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

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


class ChamadoCriar(BaseModel):
    descricao: str = Field(
        min_length=5,
        max_length=2000
    )


class ChamadoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: str
    categoria: str | None
    prioridade: str | None
    status: str
    criado_em: datetime
