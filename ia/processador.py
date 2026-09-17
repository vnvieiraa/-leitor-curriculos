"""Revisão e tradução de currículos usando a API da OpenAI."""

from __future__ import annotations

import os
import json
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _obter_chave_openai() -> str:
    """Retorna a chave real da OpenAI ou informa quando o valor ainda é placeholder."""
    chave = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not chave:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Defina essa variável antes de usar a IA."
        )

    exemplos = {
        "suachaveaqui",
        "sua-chave-aqui",
        "sua_chave_aqui",
        "coloque_sua_chave_aqui",
        "your-openai-key",
        "youropenaikey",
        "changeme",
        "replace-me",
    }
    valor_normalizado = chave.lower().replace("-", "").replace("_", "").replace(" ", "")
    if valor_normalizado in exemplos or "sua-chave" in chave.lower() or "coloque_sua" in chave.lower():
        raise RuntimeError(
            "OPENAI_API_KEY ainda está com o valor de exemplo. Substitua pela chave real da OpenAI."
        )
    return chave


def processar_curriculo(texto: str, *, traduzir: bool = False) -> str:
    """Processa um currículo e retorna o texto revisado ou traduzido.

    A chave OPENAI_API_KEY é obrigatória para o processamento com IA.
    """
    if not texto.strip():
        raise RuntimeError("O currículo está vazio.")

    chave = _obter_chave_openai()

    try:
        from openai import APIError, OpenAI
    except ImportError as erro:
        raise RuntimeError("Instale a dependência 'openai' para usar a IA.") from erro

    tarefa = (
        "Traduza o currículo para inglês profissional, preservando nomes, datas, "
        "empresas, tecnologias e a estrutura das informações."
        if traduzir
        else "Revise o currículo em português do Brasil, corrigindo ortografia, "
        "acentuação, gramática, concordância e clareza profissional. Preserve "
        "nomes, datas, empresas e informações originais."
    )
    prompt = f"{tarefa}\n\nRetorne apenas o currículo final.\n\nCurrículo:\n{texto}"

    cliente = OpenAI(api_key=chave)
    try:
        resposta = cliente.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=prompt,
        )
    except APIError as erro:
        raise RuntimeError(f"Falha na comunicação com a API de IA: {erro}") from erro

    resultado = resposta.output_text.strip()
    if not resultado:
        raise RuntimeError("A API de IA retornou uma resposta vazia.")
    return resultado


def analisar_curriculos_com_ia(curriculos: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Extrai dados estruturados de currículos usando a API da OpenAI."""
    if not curriculos:
        raise ValueError("Envie pelo menos um currículo.")

    chave = _obter_chave_openai()

    try:
        from openai import APIError, OpenAI
    except ImportError as erro:
        raise RuntimeError("Instale a dependência 'openai' para usar a IA.") from erro

    prompt = (
        "Analise os currículos abaixo para triagem técnica. Retorne somente JSON válido "
        "com uma lista na chave results. Cada item deve conter name, candidateName, "
        "hasTechnology (boolean), hasDatabase (boolean), technologies (lista de strings), "
        "databases (lista de strings), years (número) e notes (string). Não invente "
        "informações; use 0 ou listas vazias quando algo não estiver no texto.\n\n"
        f"Currículos:\n{json.dumps(curriculos, ensure_ascii=False)}"
    )
    cliente = OpenAI(api_key=chave)
    try:
        resposta = cliente.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            input=prompt,
        )
    except APIError as erro:
        raise RuntimeError(f"Falha na comunicação com a API de IA: {erro}") from erro

    try:
        dados = json.loads(resposta.output_text)
        resultados = dados["results"]
    except (json.JSONDecodeError, KeyError, TypeError) as erro:
        raise ValueError("A IA retornou um formato de análise inválido.") from erro
    if not isinstance(resultados, list):
        raise ValueError("A IA retornou resultados inválidos.")
    return resultados
