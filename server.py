"""Servidor web para análise de currículos com IA."""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ia.processador import analisar_curriculos_com_ia

app = FastAPI(title="Leitor de Currículos API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


class CurriculoEntrada(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1, max_length=100_000)


class AnaliseEntrada(BaseModel):
    resumes: list[CurriculoEntrada] = Field(min_length=1, max_length=20)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "ai_configured": str(bool(os.getenv("OPENAI_API_KEY"))).lower()}


@app.post("/api/analyze")
def analyze(payload: AnaliseEntrada) -> dict[str, Any]:
    try:
        results = analisar_curriculos_com_ia(
            [{"name": resume.name, "text": resume.text} for resume in payload.resumes]
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
