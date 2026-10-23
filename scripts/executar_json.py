from pydantic import ValidationError

from app.schemas.chamado import ClassificacaoChamado
from app.services.ia import analisar_chamado_json


chamado = (
    "Não consigo acessar meu e-mail "
    "corporativo desde ontem."
)

try:
    resposta = analisar_chamado_json(chamado)

    classificacao = (
        ClassificacaoChamado.model_validate(resposta)
    )

    print("JSON validado!")
    print(classificacao.model_dump())

except ValidationError as erro:
    print("Erro de validação:")
    print(erro)

except Exception as erro:
    print("Erro na integração:")
    print(erro)
