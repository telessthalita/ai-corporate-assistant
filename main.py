

import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError

from validacao import validar_resposta
from schemas import ClassificacaoChamado
from servico_ia import analisar_chamado_json
from fastapi import Depends
from sqlalchemy.orm import Session

from database import obter_db
from repositorio_chamados import criar_chamado, listar_chamados
from schemas import ChamadoCriar, ChamadoResposta

app = FastAPI()


class RespostaIA(BaseModel):
    confianca: float = Field(
        strict=True,
        ge=0,
        le=1
    )

    categoria: str


@app.get("/")
def inicio():
    return {
        "mensagem": "AI Corporate Assistant funcionando!"
    }


@app.post("/validar")
def validar(dados: RespostaIA):

    resultado = validar_resposta({
        "confianca": dados.confianca
    })

    return {
        "categoria": dados.categoria,
        "confianca": dados.confianca,
        "resultado": resultado
    }


import requests
from pydantic import BaseModel


class NovoChamado(BaseModel):
    texto: str


@app.post("/classificar")
def classificar_chamado(chamado: NovoChamado):
    try:
        dados = analisar_chamado_json(chamado.texto)

        classificacao = (
            ClassificacaoChamado.model_validate(dados)
        )

        return classificacao.model_dump()

    except ValidationError:
        raise HTTPException(
            status_code=502,
            detail="A IA retornou dados inválidos."
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError
    ):
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter uma resposta válida da IA."
        )


@app.post(
    "/chamados",
    response_model=ChamadoResposta,
    status_code=201
)
def cadastrar_chamado(
    dados: ChamadoCriar,
    db: Session = Depends(obter_db)
):
    return criar_chamado(
        db=db,
        descricao=dados.descricao
    )


@app.get(
    "/chamados",
    response_model=list[ChamadoResposta]
)
def consultar_chamados(
    db: Session = Depends(obter_db)
):
    return listar_chamados(db)
