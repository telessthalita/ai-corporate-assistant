
import json
from pathlib import Path

arquivo = Path(__file__).with_name("chamados_avaliacao.json")

casos = json.loads(
    arquivo.read_text(encoding="utf-8")
)

for caso in casos:
    print(
        caso["id"],
        "|",
        caso["categoria_esperada"],
        "|",
        caso["texto"]
    )
