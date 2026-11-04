
import pytest


# ==========================================================
# 1. TOKENS FICTÍCIOS PARA OS TESTES
# ==========================================================

@pytest.fixture
def perfis_teste(monkeypatch):
    monkeypatch.setenv(
        "ADMIN_API_TOKEN",
        "admin-token-exclusivo-para-testes"
    )

    monkeypatch.setenv(
        "ANALYST_API_TOKEN",
        "analyst-token-exclusivo-para-testes"
    )

    return {
        "admin": "admin-token-exclusivo-para-testes",
        "analyst": "analyst-token-exclusivo-para-testes"
    }


# ==========================================================
# 2. CRIAR CHAMADO AUTENTICADO
# ==========================================================

@pytest.fixture
def chamado_id(client, perfis_teste):
    resposta = client.post(
        "/chamados",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['analyst']}"
            )
        },
        json={
            "descricao": "Sistema corporativo indisponível"
        }
    )

    assert resposta.status_code == 201

    return resposta.json()["id"]


# ==========================================================
# 3. ANALISTA NÃO PODE ALTERAR PRIORIDADE
# ==========================================================

def test_analista_nao_altera_prioridade(
    client, chamado_id, perfis_teste
):
    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['analyst']}"
            )
        },
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    assert resposta.status_code == 403


# ==========================================================
# 4. ANALISTA NÃO PODE CONSULTAR AUDITORIA
# ==========================================================

def test_analista_nao_consulta_auditoria(
    client, chamado_id, perfis_teste
):
    resposta = client.get(
        f"/chamados/{chamado_id}/auditoria",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['analyst']}"
            )
        }
    )

    assert resposta.status_code == 403


# ==========================================================
# 5. ADMINISTRADOR PODE CONSULTAR AUDITORIA
# ==========================================================

def test_admin_consulta_auditoria(
    client, chamado_id, perfis_teste
):
    resposta = client.get(
        f"/chamados/{chamado_id}/auditoria",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['admin']}"
            )
        }
    )

    assert resposta.status_code == 200
    assert resposta.json() == []


# ==========================================================
# 6. ACESSO NEGADO NÃO ALTERA O BANCO
# ==========================================================

def test_acesso_negado_nao_altera_banco(
    client, chamado_id, perfis_teste
):
    # Analista tenta alterar a prioridade.
    resposta = client.post(
        f"/chamados/{chamado_id}/avaliar-prioridade",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['analyst']}"
            )
        },
        json={
            "impacto": "critico",
            "bloqueia_trabalho": True,
            "solicitacao_rotineira": False
        }
    )

    # A API deve bloquear a operação.
    assert resposta.status_code == 403

    # Consulta o chamado com um token válido.
    consulta = client.get(
        "/chamados",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['analyst']}"
            )
        }
    )

    assert consulta.status_code == 200

    chamado = next(
        item for item in consulta.json()
        if item["id"] == chamado_id
    )

    # A prioridade não pode ter sido alterada.
    assert chamado["prioridade"] is None

    # Administrador consulta o histórico de auditoria.
    auditoria = client.get(
        f"/chamados/{chamado_id}/auditoria",
        headers={
            "Authorization": (
                f"Bearer {perfis_teste['admin']}"
            )
        }
    )

    assert auditoria.status_code == 200

    # Nenhum evento de auditoria deve ter sido criado.
    assert auditoria.json() == []
