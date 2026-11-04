
import requests

from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Banco de dados
from app.core.database import obter_db

# Autenticação e autorização
from app.core.security import (
    autenticar_usuario,
    exigir_admin,
)

# Repositório de chamados
from app.repositories.chamados import (
    criar_chamado,
    listar_chamados,
    buscar_chamado,
    salvar_prioridade,
    listar_auditoria,
)

# Schemas
from app.schemas.chamado import (
    RespostaIA,
    NovoChamado,
    ClassificacaoChamado,
    ChamadoCriar,
    ChamadoResposta,
    DadosPrioridade,
    ResultadoPrioridade,
    AuditoriaResposta,
)

# Serviços
from app.services.validacao import validar_resposta
from app.services.ia import analisar_chamado_json
from app.services.chamados import classificar_chamado_salvo
from app.services.motor_decisao import avaliar_prioridade


app = FastAPI(
    title="AI Corporate Assistant",
    description="API corporativa de classificação de chamados com IA.",
    version="0.12.0",
)


# ==========================================================
# 1. STATUS DA APLICAÇÃO
# ==========================================================

@app.get("/")
def inicio():
    return {
        "mensagem": "AI Corporate Assistant funcionando!"
    }


# ==========================================================
# 2. VALIDAÇÃO DE RESPOSTAS
# ==========================================================

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


# ==========================================================
# 3. CLASSIFICAÇÃO DIRETA COM OLLAMA
# Requer autenticação: admin ou analyst
# ==========================================================

@app.post("/classificar")
def classificar_chamado(
    chamado: NovoChamado,
    perfil: str = Depends(autenticar_usuario),
):
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
        TypeError,
    ):
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter uma resposta válida da IA."
        )


# ==========================================================
# 4. CADASTRAR CHAMADO
# Requer autenticação: admin ou analyst
# ==========================================================

@app.post(
    "/chamados",
    response_model=ChamadoResposta,
    status_code=201,
)
def cadastrar_chamado(
    dados: ChamadoCriar,
    perfil: str = Depends(autenticar_usuario),
    db: Session = Depends(obter_db),
):
    return criar_chamado(
        db=db,
        descricao=dados.descricao,
    )


# ==========================================================
# 5. LISTAR CHAMADOS
# Requer autenticação: admin ou analyst
# ==========================================================

@app.get(
    "/chamados",
    response_model=list[ChamadoResposta],
)
def consultar_chamados(
    perfil: str = Depends(autenticar_usuario),
    db: Session = Depends(obter_db),
):
    return listar_chamados(db)


# ==========================================================
# 6. CLASSIFICAR CHAMADO EXISTENTE
# Requer autenticação: admin ou analyst
# ==========================================================

@app.post(
    "/chamados/{chamado_id}/classificar",
    response_model=ChamadoResposta,
)
def classificar_chamado_existente(
    chamado_id: int,
    perfil: str = Depends(autenticar_usuario),
    db: Session = Depends(obter_db),
):
    try:
        chamado = classificar_chamado_salvo(
            db,
            chamado_id,
        )

    except ValidationError:
        raise HTTPException(
            status_code=502,
            detail="A IA retornou dados inválidos",
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError,
    ):
        raise HTTPException(
            status_code=502,
            detail="Falha na classificação do chamado",
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Falha de acesso ao banco de dados",
        )

    if chamado is None:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado",
        )

    return chamado


# ==========================================================
# 7. AVALIAR E SALVAR PRIORIDADE
# Requer autorização: somente admin
# ==========================================================

@app.post(
    "/chamados/{chamado_id}/avaliar-prioridade",
    response_model=ResultadoPrioridade,
)
def avaliar_prioridade_chamado(
    chamado_id: int,
    dados: DadosPrioridade,
    perfil: str = Depends(exigir_admin),
    db: Session = Depends(obter_db),
):
    chamado = buscar_chamado(
        db,
        chamado_id,
    )

    if chamado is None:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado",
        )

    resultado = avaliar_prioridade(
        impacto=dados.impacto,
        bloqueia_trabalho=dados.bloqueia_trabalho,
        solicitacao_rotineira=dados.solicitacao_rotineira,
    )

    # Não altera o banco quando falta informação.
    if resultado["revisao_humana"]:
        return resultado

    try:
        salvar_prioridade(
            db=db,
            chamado=chamado,
            prioridade=resultado["prioridade"],
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível salvar a prioridade",
        )

    return resultado


# ==========================================================
# 8. CONSULTAR HISTÓRICO DE AUDITORIA
# Requer autorização: somente admin
# ==========================================================

@app.get(
    "/chamados/{chamado_id}/auditoria",
    response_model=list[AuditoriaResposta],
)
def consultar_auditoria(
    chamado_id: int,
    perfil: str = Depends(exigir_admin),
    db: Session = Depends(obter_db),
):
    chamado = buscar_chamado(
        db,
        chamado_id,
    )

    if chamado is None:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado",
        )

    return listar_auditoria(
        db=db,
        chamado_id=chamado_id,
    )
