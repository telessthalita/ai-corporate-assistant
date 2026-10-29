from datetime import datetime
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


class RespostaIA(BaseModel):
    confianca: float = Field(
        strict=True,
        ge=0,
        le=1
    )

    categoria: str


class NovoChamado(BaseModel):
    texto: str


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

from typing import Literal


class DadosPrioridade(BaseModel):
    impacto: Literal["baixo", "moderado", "critico"] | None = None
    bloqueia_trabalho: bool | None = None
    solicitacao_rotineira: bool | None = None


class ResultadoPrioridade(BaseModel):
    prioridade: Literal["baixa", "media", "alta"] | None
    revisao_humana: bool
    motivo: str

