
import requests

from unittest.mock import patch


# ==========================================================
# 1. CADASTRO DE CHAMADOS
# ==========================================================

def test_criar_chamado(client_analyst):
    client = client_analyst

    resposta = client.post(
        "/chamados",
        json={
            "descricao": "Erro no login do sistema"
        }
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["id"] is not None
    assert dados["descricao"] == "Erro no login do sistema"
    assert dados["status"] == "aberto"
    assert dados["categoria"] is None
    assert dados["prioridade"] is None


# ==========================================================
# 2. CONSULTA DE CHAMADOS
# ==========================================================

def test_listar_chamados(client_analyst):
    client = client_analyst

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Computador não liga"
        }
    )

    assert criacao.status_code == 201

    resposta = client.get("/chamados")

    assert resposta.status_code == 200

    chamados = resposta.json()

    assert len(chamados) == 1
    assert chamados[0]["descricao"] == "Computador não liga"


# ==========================================================
# 3. FALHA DO OLLAMA
# ==========================================================

def test_falha_ollama_preserva_chamado(client_analyst):
    client = client_analyst

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Não consigo acessar o e-mail"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    with patch(
        "app.services.chamados.analisar_chamado_json",
        side_effect=requests.exceptions.ConnectionError(
            "Ollama indisponível"
        )
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert resposta.status_code == 502

    consulta = client.get("/chamados")

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["categoria"] is None
    assert chamado["prioridade"] is None
    assert chamado["status"] == "aberto"


# ==========================================================
# 4. EVITAR CLASSIFICAÇÃO DUPLICADA
# ==========================================================

def test_nao_classificar_duas_vezes(client_analyst):
    client = client_analyst

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Erro ao acessar o sistema"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    resposta_ia = {
        "categoria": "suporte",
        "prioridade": "media",
        "resumo": "Problema de acesso ao sistema"
    }

    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value=resposta_ia
    ) as modelo:

        primeira = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

        segunda = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert primeira.status_code == 200
    assert segunda.status_code == 200

    assert modelo.call_count == 1
    assert primeira.json()["id"] == segunda.json()["id"]
    assert segunda.json()["categoria"] == "suporte"


# ==========================================================
# 5. PRIORIDADE ALTA — ADMINISTRADOR
# ==========================================================

def test_endpoint_prioridade_alta(client_admin):
    client = client_admin

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema corporativo indisponível"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["prioridade"] == "alta"
    assert dados["revisao_humana"] is False


# ==========================================================
# 6. PRIORIDADE SEM DADOS SUFICIENTES
# ==========================================================

def test_endpoint_prioridade_revisao(client_admin):
    client = client_admin

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Problema de acesso ao sistema"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": None,
            "bloqueia_trabalho": None,
            "solicitacao_rotineira": None
        }
    )

    assert resposta.status_code == 200
    assert resposta.json()["prioridade"] is None
    assert resposta.json()["revisao_humana"] is True


# ==========================================================
# 7. PRIORIDADE — CHAMADO INEXISTENTE
# ==========================================================

def test_endpoint_prioridade_chamado_inexistente(
    client_admin
):
    client = client_admin

    resposta = client.post(
        "/chamados/999999/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert resposta.status_code == 404


# ==========================================================
# 8. IA NÃO PODE SOBRESCREVER PRIORIDADE
# ==========================================================

def test_classificacao_preserva_prioridade(client_admin):
    client = client_admin

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema indisponível para toda a equipe"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    decisao = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert decisao.status_code == 200
    assert decisao.json()["prioridade"] == "alta"

    with patch(
        "app.services.chamados.analisar_chamado_json",
        return_value={
            "categoria": "suporte",
            "prioridade": "baixa",
            "resumo": "Sistema indisponível para a equipe"
        }
    ):
        resposta = client.post(
            f"/chamados/{chamado_id}/classificar"
        )

    assert resposta.status_code == 200

    consulta = client.get("/chamados")

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["prioridade"] == "alta"
    assert chamado["categoria"] == "suporte"


# ==========================================================
# 9. REVISÃO NÃO APAGA PRIORIDADE EXISTENTE
# ==========================================================

def test_revisao_nao_apaga_prioridade(client_admin):
    client = client_admin

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema indisponível para a equipe"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    primeira = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert primeira.status_code == 200
    assert primeira.json()["prioridade"] == "alta"

    segunda = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": None,
            "bloqueia_trabalho": None,
            "solicitacao_rotineira": None
        }
    )

    assert segunda.status_code == 200
    assert segunda.json()["revisao_humana"] is True
    assert segunda.json()["prioridade"] is None

    consulta = client.get("/chamados")

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["prioridade"] == "alta"


# ==========================================================
# 10. AUDITORIA DE DUAS ALTERAÇÕES
# ==========================================================

def test_historico_duas_alteracoes_prioridade(
    client_admin
):
    client = client_admin

    criacao = client.post(
        "/chamados",
        json={
            "descricao": "Sistema corporativo indisponível"
        }
    )

    assert criacao.status_code == 201

    chamado_id = criacao.json()["id"]

    primeira = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert primeira.status_code == 200
    assert primeira.json()["prioridade"] == "alta"

    segunda = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        json={
            "impacto": "moderado",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert segunda.status_code == 200
    assert segunda.json()["prioridade"] == "media"

    resposta = client.get(
        f"/chamados/{chamado_id}/auditoria"
    )

    assert resposta.status_code == 200

    historico = resposta.json()

    assert len(historico) == 2

    assert historico[0]["valor_anterior"] is None
    assert historico[0]["valor_novo"] == "alta"

    assert historico[1]["valor_anterior"] == "alta"
    assert historico[1]["valor_novo"] == "media"

    assert all(
        evento["origem"] == "motor_regras"
        for evento in historico
    )

    consulta = client.get("/chamados")

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    assert chamado["prioridade"] == "media"
