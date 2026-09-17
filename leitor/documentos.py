"""Funções para extrair texto de formatos suportados."""

from __future__ import annotations

from pathlib import Path


def ler_documento(caminho: str | Path) -> str:
    """Extrai texto de um arquivo PDF ou DOCX."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise ValueError(f"Arquivo não encontrado: {arquivo}")

    extensao = arquivo.suffix.lower()
    if extensao == ".pdf":
        return _ler_pdf(arquivo)
    if extensao == ".docx":
        return _ler_docx(arquivo)
    raise ValueError("Formato não suportado. Use um arquivo PDF ou DOCX.")


def _ler_pdf(arquivo: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as erro:
        raise ImportError("Instale a dependência 'pypdf' para ler PDFs.") from erro

    paginas = PdfReader(str(arquivo)).pages
    texto = "\n\n".join((pagina.extract_text() or "").strip() for pagina in paginas)
    if not texto.strip():
        raise ValueError("Não foi possível extrair texto deste PDF.")
    return texto.strip()


def _ler_docx(arquivo: Path) -> str:
    try:
        from docx import Document
    except ImportError as erro:
        raise ImportError("Instale a dependência 'python-docx' para ler DOCX.") from erro

    documento = Document(str(arquivo))
    paragrafos = [paragrafo.text.strip() for paragrafo in documento.paragraphs]
    texto = "\n".join(paragrafo for paragrafo in paragrafos if paragrafo)
    if not texto.strip():
        raise ValueError("Não foi possível extrair texto deste DOCX.")
    return texto.strip()
