from sqlalchemy.exc import SQLAlchemyError
from app.core.database import testar_conexao

try:
    resultado = testar_conexao()
    print("Conexão com Supabase:", resultado)

except SQLAlchemyError as erro:
    print("Falha na conexão com PostgreSQL")
    print("Tipo:", type(erro).__name__)

    causa = getattr(erro, "orig", None)

    if causa:
        print("Detalhes:", str(causa))
