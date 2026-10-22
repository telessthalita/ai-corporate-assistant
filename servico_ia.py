
import json
import requests


def analisar_chamado_json(texto: str) -> dict:
    url = "http://localhost:11434/api/generate"

    prompt = (
        "Você é um classificador de chamados corporativos.\n"
        "Classifique o problema principal do chamado.\n\n"

        "REGRAS OBRIGATÓRIAS:\n"
        "- suporte: login, senhas, computadores, "
        "e-mails, sistemas e problemas técnicos.\n"
        "- financeiro: pagamentos, faturas, "
        "reembolsos e notas fiscais.\n"
        "- comercial: vendas, orçamentos, "
        "propostas e negociações.\n\n"       
        
        "REGRAS DE PRIORIDADE:\n"
"- alta: serviço crítico indisponível, "
"vários usuários afetados ou impacto "
"operacional grave explicitamente informado.\n"
"- media: problema que impede ou prejudica "
"o trabalho de uma pessoa, sem impacto "
"crítico comprovado.\n"
"- baixa: solicitação rotineira, sem urgência "
"ou bloqueio de trabalho.\n"
"Não presuma impacto crítico quando "
"ele não estiver descrito.\n\n"


        "Exemplos:\n"
        "Chamado: Não consigo acessar meu e-mail.\n"
        "Categoria: suporte\n\n"
        "Chamado: Preciso pagar uma fatura.\n"
        "Categoria: financeiro\n\n"
        "Chamado: Quero solicitar um orçamento.\n"
        "Categoria: comercial\n\n"

        "Prioridade: baixa, media ou alta.\n"
        "Use alta apenas quando o chamado indicar "
        "impacto crítico ou urgência explícita.\n"
        "Não invente causas ou detalhes.\n"
        "Seja objetivo no resumo.\n\n"

        "Responda apenas com um objeto JSON contendo "
        "categoria, prioridade e resumo.\n\n"

        f"Chamado: {texto}"
    )

    dados = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    
    resposta = requests.post(
        url,
        json=dados,
        timeout=120
    )

    resposta.raise_for_status()

    resultado = resposta.json()["response"]

    return json.loads(resultado)
