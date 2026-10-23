# AI Corporate Assistant

API em FastAPI que cadastra chamados corporativos e os classifica
(categoria, prioridade e resumo) com um modelo local via Ollama.

## Estrutura

```
app/
  main.py            # rotas da API
  core/database.py   # conexão com o PostgreSQL (SQLAlchemy)
  models/            # modelos do banco
  schemas/           # schemas Pydantic (entrada/saída)
  repositories/      # acesso ao banco
  services/          # regras de negócio e integração com a IA
scripts/             # utilitários (criar tabelas, testar banco, avaliar modelo)
tests/               # testes automatizados (pytest)
```

## Configuração

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # e preencha o DATABASE_URL
```

## Uso

Todos os comandos devem ser executados na raiz do projeto.

```powershell
fastapi dev app/main.py                 # sobe a API
python -m pytest                        # roda os testes
python -m scripts.criar_tabelas         # cria as tabelas no banco
python -m scripts.testar_banco          # testa a conexão com o banco
python -m scripts.avaliar_modelo        # mede a acurácia da categoria (requer Ollama)
python -m scripts.avaliar_prioridade    # mede a acurácia da prioridade (requer Ollama)
python -m scripts.executar_json         # classifica um chamado de exemplo (requer Ollama)
```
