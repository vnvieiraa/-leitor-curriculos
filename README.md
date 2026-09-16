# Leitor de Currículos com IA

Aplicativo desktop em Python/Tkinter para ler currículos em PDF ou DOCX, revisar
o texto em português e traduzir o resultado para inglês usando a API da OpenAI.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Defina a chave da API antes de usar os botões de processamento:

```bash
export OPENAI_API_KEY="vnvieira"
```

No Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="vnvieira"
```

## Execução

```bash
python app.py
```

O botão **Selecionar arquivo** carrega o texto do PDF ou DOCX. Depois, use
**Processar currículo**, **Traduzir para inglês** e **Salvar resultado**.
Arquivos não suportados ou sem texto exibem uma mensagem de erro na interface.
