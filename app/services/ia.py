
import json
import os

import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:1.5b"
)

PROMPT_BASE = """
Você é um classificador de chamados corporativos.
Classifique o problema principal do chamado.

CATEGORIAS DISPONÍVEIS:

- suporte:
Problemas técnicos, falhas de sistema, erros de acesso,
login, senhas, computadores, e-mails e dificuldades
de funcionamento.

- financeiro:
Boletos, segunda via de boletos, faturas, pagamentos,
cobranças, mensalidades, reembolsos e notas fiscais
relacionadas a faturamento.

- comercial:
Contratação de serviços, propostas, novos planos,
vendas, orçamentos, negociações e ampliação de contratos.

REGRAS DE CLASSIFICAÇÃO:
1. Identifique a intenção principal do chamado.
2. Pedidos de emissão ou segunda via de boleto
   pertencem à categoria financeiro.
3. Problemas técnicos para acessar uma plataforma
   pertencem à categoria suporte, mesmo quando
   a plataforma contém informações financeiras.

REGRAS DE PRIORIDADE:
- alta: serviço crítico indisponível, vários usuários
  afetados ou impacto operacional grave explicitamente
  informado.
- media: problema que impede ou prejudica o trabalho
  de uma pessoa, sem impacto crítico comprovado.
- baixa: solicitação rotineira, sem urgência ou bloqueio
  de trabalho.

Não presuma impacto crítico quando ele não estiver descrito.
Use alta apenas quando houver impacto crítico explícito.
Não invente causas ou detalhes.
Seja objetivo no resumo.

EXEMPLOS:

Chamado: Não consigo acessar meu e-mail.
Categoria: suporte

Chamado: Preciso da segunda via do boleto.
Categoria: financeiro

Chamado: Quero solicitar um orçamento.
Categoria: comercial

FORMATO DA RESPOSTA:
Responda somente com um objeto JSON contendo:
categoria, prioridade e resumo.

Chamado:
"""


RAIZ_PROJETO = Path(__file__).resolve().parents[2]


def carregar_prompt_ativo() -> str:
    versao = os.getenv("PROMPT_VERSION", "v1").lower()

    if versao not in ("v1", "v2"):
        raise ValueError(
            f"Versão de prompt inválida: {versao}"
        )

    caminho = (
        RAIZ_PROJETO
        / "prompts"
        / f"classificacao_{versao}.txt"
    )

    return caminho.read_text(encoding="utf-8")


def analisar_chamado_json(
    texto: str,
    prompt_base: str | None = None
) -> dict:

    if prompt_base is None:
        prompt_base = carregar_prompt_ativo()

    dados = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_base + "\n" + texto,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    resposta = requests.post(
        OLLAMA_URL,
        json=dados,
        timeout=120
    )

    resposta.raise_for_status()

    resultado = resposta.json()["response"]

    return json.loads(resultado)
