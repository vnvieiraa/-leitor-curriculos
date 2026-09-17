"""Interface gráfica para leitura e processamento de currículos."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import TclError

from ia.processador import processar_curriculo
from leitor.documentos import ler_documento


class Aplicacao:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Leitor de Currículos com IA")
        self.master.geometry("1000x700")
        self.master.minsize(700, 500)

        self.arquivo: Path | None = None
        self.texto_original = ""
        self.texto_atual = ""

        self._criar_interface()

    def _criar_interface(self) -> None:
        container = ttk.Frame(self.master, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Leitor de Currículos com IA",
            font=("Arial", 18, "bold"),
        ).pack(pady=(0, 6))
        ttk.Label(
            container,
            text="Selecione um currículo em PDF ou DOCX para revisar e traduzir.",
        ).pack(pady=(0, 14))

        botoes = ttk.Frame(container)
        botoes.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(
            botoes, text="Selecionar arquivo", command=self.selecionar_arquivo
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(
            botoes, text="Processar currículo", command=self.processar
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(
            botoes, text="Traduzir para inglês", command=self.traduzir
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(
            botoes, text="Salvar resultado", command=self.salvar
        ).pack(side=tk.LEFT, padx=8)

        self.status = tk.StringVar(value="Nenhum arquivo selecionado.")
        ttk.Label(container, textvariable=self.status).pack(
            anchor=tk.W, pady=(0, 8)
        )

        area = ttk.Frame(container)
        area.pack(fill=tk.BOTH, expand=True)
        self.texto = tk.Text(area, wrap=tk.WORD, undo=True)
        barra = ttk.Scrollbar(area, orient=tk.VERTICAL, command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        self.texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

    def selecionar_arquivo(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar currículo",
            filetypes=[
                ("Documentos PDF", "*.pdf"),
                ("Documentos Word", "*.docx"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not caminho:
            return

        try:
            self.arquivo = Path(caminho)
            self.texto_original = ler_documento(self.arquivo)
            self._exibir(self.texto_original)
            self.status.set(f"Arquivo carregado: {self.arquivo.name}")
        except (OSError, ValueError, ImportError) as erro:
            self.arquivo = None
            messagebox.showerror("Erro ao ler arquivo", str(erro))

    def processar(self) -> None:
        if not self._validar_conteudo():
            return
        try:
            resultado = processar_curriculo(self.texto_original, traduzir=False)
            self._exibir(resultado)
            self.status.set("Currículo processado com sucesso.")
        except RuntimeError as erro:
            messagebox.showerror("Erro ao processar currículo", str(erro))

    def traduzir(self) -> None:
        if not self._validar_conteudo():
            return
        try:
            resultado = processar_curriculo(self.texto_atual, traduzir=True)
            self._exibir(resultado)
            self.status.set("Currículo traduzido com sucesso.")
        except RuntimeError as erro:
            messagebox.showerror("Erro ao traduzir currículo", str(erro))

    def salvar(self) -> None:
        conteudo = self.texto.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Atenção", "Não há conteúdo para salvar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar currículo processado",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            Path(caminho).write_text(conteudo + "\n", encoding="utf-8")
            self.status.set(f"Resultado salvo em {Path(caminho).name}.")
            messagebox.showinfo("Sucesso", "Currículo salvo com sucesso.")
        except OSError as erro:
            messagebox.showerror("Erro ao salvar", str(erro))

    def _exibir(self, conteudo: str) -> None:
        self.texto.delete("1.0", tk.END)
        self.texto.insert("1.0", conteudo)
        self.texto_atual = conteudo

    def _validar_conteudo(self) -> bool:
        if not self.texto_original.strip():
            messagebox.showwarning(
                "Atenção", "Selecione e carregue um currículo antes de continuar."
            )
            return False
        return True


def main() -> None:
    try:
        root = tk.Tk()
    except TclError as erro:
        raise SystemExit(
            "Não foi possível iniciar a interface gráfica. "
            "Execute em um ambiente com display (X11/Wayland) ou "
            "configure o encaminhamento gráfico do seu ambiente remoto."
        ) from erro
    Aplicacao(root)
    root.mainloop()


if __name__ == "__main__":
    main()
