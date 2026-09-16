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
export OPENAI_API_KEY="sua-chave-aqui"
```

No Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="sua-chave-aqui"
```

## Execução

Para usar a interface web com integração de IA:

```bash
export OPENAI_API_KEY="sua-chave-aqui"
python server.py
```

Em outro terminal, sirva a página:

```bash
python -m http.server 4173
```

Abra `http://127.0.0.1:4173/index.html` e use **Analisar com IA**. A chave
permanece no servidor e nunca é enviada ao navegador.

Para usar a interface desktop:

```bash
python app.py
```

> Em ambientes remotos sem display gráfico, como alguns containers e sessões
> SSH, a interface Tkinter não pode ser aberta diretamente. Use um desktop com
> X11/Wayland ou configure o encaminhamento gráfico antes de executar o app.

O botão **Selecionar arquivo** carrega o texto do PDF ou DOCX. Depois, use
**Processar currículo**, **Traduzir para inglês** e **Salvar resultado**.
Arquivos não suportados ou sem texto exibem uma mensagem de erro na interface.
