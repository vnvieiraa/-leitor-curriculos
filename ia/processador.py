"""Revisão e tradução de currículos usando a API da OpenAI."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _normalizar_texto(texto: str | None) -> str:
    """Valida e normaliza o texto do currículo para evitar falhas de entrada."""
    if not isinstance(texto, str):
        raise RuntimeError("O currículo está vazio.")

    texto = texto.strip()
    if not texto:
        raise RuntimeError("O currículo está vazio.")
    return texto


def _extrair_texto_resposta(resposta: Any) -> str:
    """Extrai o texto de uma resposta da API de IA em diferentes versões do SDK."""
    if hasattr(resposta, "output_text"):
        output_text = getattr(resposta, "output_text")
        if isinstance(output_text, str):
            return output_text.strip()

    output = getattr(resposta, "output", None)
    if isinstance(output, list):
        partes: list[str] = []
        for item in output:
            conteudo = (
                item.get("content", [])
                if isinstance(item, Mapping)
                else getattr(item, "content", [])
            )
            for bloco in conteudo:
                texto = (
                    bloco.get("text")
                    if isinstance(bloco, Mapping)
                    else getattr(bloco, "text", None)
                )
                if isinstance(texto, str):
                    partes.append(texto)
        texto_combinado = "".join(partes).strip()
        if texto_combinado:
            return texto_combinado

    raise RuntimeError("A API de IA retornou uma resposta vazia.")


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


def processar_curriculo(texto: str | None, *, traduzir: bool = False) -> str:
    """Processa um currículo e retorna o texto revisado ou traduzido.

    A chave OPENAI_API_KEY é obrigatória para o processamento com IA.
    """
    texto = _normalizar_texto(texto)

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
    except Exception as erro:  # pragma: no cover - depende da versão do SDK
        raise RuntimeError(f"Falha na comunicação com a API de IA: {erro}") from erro

    resultado = _extrair_texto_resposta(resposta)
    if not resultado:
        raise RuntimeError("A API de IA retornou uma resposta vazia.")
    return resultado


def analisar_curriculos_com_ia(curriculos: list[dict[str, str]] | None) -> list[dict[str, Any]]:
    """Extrai dados estruturados de currículos usando a API da OpenAI."""
    if not isinstance(curriculos, list) or not curriculos:
        raise ValueError("Envie pelo menos um currículo.")
    if any(not isinstance(item, dict) for item in curriculos):
        raise ValueError("Cada currículo deve ser um dicionário com nome e texto.")

    chave = _obter_chave_openai()

    try:
        from openai import OpenAI
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
    except Exception as erro:  # pragma: no cover - depende da versão do SDK
        raise RuntimeError(f"Falha na comunicação com a API de IA: {erro}") from erro

    texto_resposta = _extrair_texto_resposta(resposta)
    texto_json = texto_resposta.strip()
    if texto_json.startswith("```"):
        linhas = texto_json.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        texto_json = "\n".join(linhas).strip()

    try:
        dados = json.loads(texto_json)
        resultados = dados["results"]
    except (json.JSONDecodeError, KeyError, TypeError) as erro:
        raise ValueError("A IA retornou um formato de análise inválido.") from erro
    if not isinstance(resultados, list):
        raise ValueError("A IA retornou resultados inválidos.")
    return resultados
