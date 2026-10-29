import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.schemas.chamado import DadosPrioridade, ResultadoPrioridade
from app.services.motor_decisao import avaliar_prioridade
from app.repositories.chamados import buscar_chamado
from app.repositories.chamados import salvar_prioridade

from app.core.database import obter_db
from app.repositories.chamados import (
    criar_chamado,
    listar_chamados
)
from app.schemas.chamado import (
    ChamadoCriar,
    ChamadoResposta,
    ClassificacaoChamado,
    NovoChamado,
    RespostaIA
)
from app.services.chamados import classificar_chamado_salvo
from app.services.ia import analisar_chamado_json
from app.services.validacao import validar_resposta

app = FastAPI(title="AI Corporate Assistant")


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


@app.post(
    "/chamados/{chamado_id}/classificar",
    response_model=ChamadoResposta
)
def classificar_chamado_existente(
    chamado_id: int,
    db: Session = Depends(obter_db)
):
    try:
        chamado = classificar_chamado_salvo(
            db, chamado_id
        )

    # ValidationError herda de ValueError, por isso vem antes
    except ValidationError:
        raise HTTPException(
            status_code=502,
            detail="A IA retornou dados inválidos"
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError
    ):
        raise HTTPException(
            status_code=502,
            detail="Falha na classificação do chamado"
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Falha de acesso ao banco de dados"
        )

    if chamado is None:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado"
        )

    return chamado


@app.post(
    "/chamados/{chamado_id}/avaliar-prioridade",
    response_model=ResultadoPrioridade
)
def avaliar_prioridade_chamado(
    chamado_id: int,
    dados: DadosPrioridade,
    db: Session = Depends(obter_db)
):
    chamado = buscar_chamado(db, chamado_id)

    if chamado is None:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado"
        )

  
    resultado = avaliar_prioridade(
        impacto=dados.impacto,
        bloqueia_trabalho=dados.bloqueia_trabalho,
        solicitacao_rotineira=dados.solicitacao_rotineira
    )

    if resultado["revisao_humana"]:
        return resultado

    try:
        salvar_prioridade(
            db=db,
            chamado=chamado,
            prioridade=resultado["prioridade"]
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível salvar a prioridade"
        )

    return resultado
