
from pathlib import Path

import pytest

from evals.comparar_prompts import carregar_prompt


@pytest.mark.parametrize(
    "versao",
    ["v1", "v2"]
)
def test_arquivos_de_prompt_existem(versao):
    prompt = carregar_prompt(versao)

    assert isinstance(prompt, str)
    assert prompt.strip()


def test_prompt_v2_define_categorias():
    prompt = carregar_prompt("v2").lower()

    for categoria in (
        "suporte",
        "financeiro",
        "comercial"
    ):
        assert categoria in prompt


def test_prompt_v2_exige_json():
    prompt = carregar_prompt("v2").lower()

    assert "json" in prompt


def test_prompt_v2_prioriza_intencao():
    prompt = carregar_prompt("v2").lower()

    assert "intenção principal" in prompt
