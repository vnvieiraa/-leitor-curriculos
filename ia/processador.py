"""Revisão e tradução de currículos usando a API da OpenAI."""

from __future__ import annotations

import os


def processar_curriculo(texto: str, *, traduzir: bool = False) -> str:
    """Processa um currículo e retorna o texto revisado ou traduzido.

    A chave OPENAI_API_KEY é obrigatória para o processamento com IA.
    """
    if not texto.strip():
        raise RuntimeError("O currículo está vazio.")

    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Defina essa variável antes de usar a IA."
        )

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
