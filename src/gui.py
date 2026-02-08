import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel, Label, Button, Entry
import subprocess
import os
import glob
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador Estatístico Completo")
        self.geometry("1000x700")

        # Seleção de arquivo
        self.label = tk.Label(self, text="Selecione um arquivo de dados para análise:")
        self.label.pack(pady=5)

        self.btn_select = tk.Button(self, text="Selecionar Arquivo", command=self.select_file)
        self.btn_select.pack(pady=2)

        self.btn_analyze = tk.Button(self, text="Rodar Análise", command=self.run_analysis, state=tk.DISABLED)
        self.btn_analyze.pack(pady=2)

        # Botões extras
        frame = tk.Frame(self)
        frame.pack(pady=5)

        self.btn_view_graphs = tk.Button(frame, text="Visualizar Gráficos", command=self.view_graphs, state=tk.DISABLED)
        self.btn_view_graphs.grid(row=0, column=0, padx=5)

        self.btn_open_report = tk.Button(frame, text="Abrir Relatório PDF", command=self.open_report, state=tk.DISABLED)
        self.btn_open_report.grid(row=0, column=1, padx=5)

        self.btn_generate_data = tk.Button(frame, text="Gerar Dados Artificiais", command=self.generate_data)
        self.btn_generate_data.grid(row=0, column=2, padx=5)

        self.btn_detect_fake = tk.Button(frame, text="Detectar Dados Artificiais", command=self.detect_fake)
        self.btn_detect_fake.grid(row=0, column=3, padx=5)

        self.btn_extra_analysis = tk.Button(frame, text="Análises Avançadas", command=self.extra_analysis)
        self.btn_extra_analysis.grid(row=0, column=4, padx=5)

        self.btn_help = tk.Button(frame, text="Ajuda/Documentação", command=self.show_help)
        self.btn_help.grid(row=0, column=5, padx=5)

        # Área de texto para resultados
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=120, height=30)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.selected_file = None
        self.last_output_dir = None

    def select_file(self):
        filetypes = [("Arquivos de dados", "*.csv *.xlsx *.tsv *.json"), ("Todos os arquivos", "*.*")]
        filename = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=filetypes)
        if filename:
            self.selected_file = filename
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Arquivo selecionado: {filename}\n")
            self.btn_analyze.config(state=tk.NORMAL)
            self.btn_view_graphs.config(state=tk.DISABLED)
            self.btn_open_report.config(state=tk.DISABLED)

    def run_analysis(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return

        self.text_area.insert(tk.END, "Analisando...\n")
        self.update()

        try:
            result = subprocess.run(
                ["python", "src/main.py", self.selected_file],
                capture_output=True, text=True, check=True
            )
            self.text_area.insert(tk.END, result.stdout)

            # Diretório padrão de saída: output/<base>
            base = os.path.splitext(os.path.basename(self.selected_file))[0].replace('.', '_')
            output_dir = os.path.join("output", f"{base}")

            if os.path.exists(output_dir):
                self.last_output_dir = output_dir
                self.btn_view_graphs.config(state=tk.NORMAL)
                self.btn_open_report.config(state=tk.NORMAL)
            else:
                self.last_output_dir = None

        except subprocess.CalledProcessError as e:
            self.text_area.insert(tk.END, f"Erro ao rodar análise:\n{e.stderr}\n")

    def view_graphs(self):
        if not self.last_output_dir or not os.path.exists(self.last_output_dir):
            messagebox.showinfo("Visualizar Gráficos", "Nenhuma pasta de saída encontrada. Rode a análise primeiro.")
            return

        # Procura imagens recursivamente (inclui distribuições, assimetria/curtose, regressão etc.)
        images = []
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            images.extend(glob.glob(os.path.join(self.last_output_dir, "**", ext), recursive=True))

        if not images:
            messagebox.showinfo("Visualizar Gráficos", "Nenhum gráfico encontrado na pasta de saída.")
            return

        # Ordena para navegação mais previsível
        images.sort()

        viewer = Toplevel(self)
        viewer.title("Gráficos Gerados")
        viewer.geometry("900x650")

        img_label = Label(viewer)
        img_label.pack(pady=10)

        idx = [0]

        def show_img(i):
            img = Image.open(images[i])
            img.thumbnail((850, 550))
            photo = ImageTk.PhotoImage(img)
            img_label.config(image=photo)
            img_label.image = photo
            viewer.title(f"Gráficos Gerados ({i + 1}/{len(images)}) — {os.path.basename(images[i])}")

        def next_img():
            idx[0] = (idx[0] + 1) % len(images)
            show_img(idx[0])

        def prev_img():
            idx[0] = (idx[0] - 1) % len(images)
            show_img(idx[0])

        btn_prev = Button(viewer, text="Anterior", command=prev_img)
        btn_prev.pack(side=tk.LEFT, padx=20, pady=10)

        btn_next = Button(viewer, text="Próximo", command=next_img)
        btn_next.pack(side=tk.RIGHT, padx=20, pady=10)

        show_img(0)

    def open_report(self):
        if not self.last_output_dir or not os.path.exists(self.last_output_dir):
            messagebox.showinfo("Relatório", "Nenhuma pasta de saída encontrada. Rode a análise primeiro.")
            return

        # 1) Caminho padrão
        pdf_path = os.path.join(self.last_output_dir, "RELATORIO_GERAL.pdf")
        if os.path.exists(pdf_path):
            os.startfile(pdf_path)
            return

        # 2) Busca recursiva por qualquer PDF
        pdfs = glob.glob(os.path.join(self.last_output_dir, "**", "*.pdf"), recursive=True)
        pdfs.sort()

        if pdfs:
            os.startfile(pdfs[0])
        else:
            messagebox.showinfo("Relatório", "Nenhum PDF encontrado na pasta de saída.")

    def generate_data(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return

        win = Toplevel(self)
        win.title("Gerar Dados Artificiais")
        win.geometry("400x320")

        Label(win, text="Tipo de geração:").pack(pady=5)
        tipo_var = tk.StringVar(value="univariado")
        tk.Radiobutton(win, text="Univariado", variable=tipo_var, value="univariado").pack()
        tk.Radiobutton(win, text="Bivariado", variable=tipo_var, value="bivariado").pack()

        Label(win, text="Quantidade de dados:").pack()
        entry_qtd = Entry(win)
        entry_qtd.pack()

        Label(win, text="Média (opcional):").pack()
        entry_media = Entry(win)
        entry_media.pack()

        Label(win, text="Desvio padrão (opcional):").pack()
        entry_dp = Entry(win)
        entry_dp.pack()

        Label(win, text="Correlação (bivariado):").pack()
        entry_corr = Entry(win)
        entry_corr.pack()

        def gerar():
            qtd = entry_qtd.get().strip()
            media = entry_media.get().strip()
            dp = entry_dp.get().strip()
            corr = entry_corr.get().strip()
            tipo = tipo_var.get()

            if not qtd.isdigit() or int(qtd) <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser um inteiro > 0.")
                return

            # ✅ Alinhado: passa o arquivo selecionado como base
            args = ["python", "src/generate_data.py", "--input", self.selected_file, "--tipo", tipo, "--qtd", qtd]

            if media:
                args += ["--media", media]
            if dp:
                args += ["--dp", dp]
            if tipo == "bivariado" and corr:
                args += ["--corr", corr]

            try:
                result = subprocess.run(args, capture_output=True, text=True, check=True)
                self.text_area.insert(tk.END, "\n[Gerador de Dados Artificiais]\n" + result.stdout + "\n")
                messagebox.showinfo("Gerar Dados", "Dados artificiais gerados com sucesso!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Erro", f"Erro ao gerar dados artificiais:\n{e.stderr}")
            win.destroy()

        Button(win, text="Gerar", command=gerar).pack(pady=10)

    def detect_fake(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return

        args = ["python", "src/detect_fake.py", self.selected_file]
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            self.text_area.insert(tk.END, "\n[Detector de Dados Artificiais]\n" + result.stdout + "\n")
        except subprocess.CalledProcessError as e:
            self.text_area.insert(tk.END, f"\n[Detector de Dados Artificiais] Erro:\n{e.stderr}\n")

    def extra_analysis(self):
        if not self.selected_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return

        win = Toplevel(self)
        win.title("Análises Avançadas")
        win.geometry("420x320")

        Label(win, text="Escolha a análise:").pack(pady=5)

        analyses = [
            "Ajuste de Distribuição",
            "Assimetria e Curtose",
            "Correlação (Pearson/Spearman)",
            "Regressão Linear Simples"
        ]

        var = tk.StringVar(value=analyses[0])
        for a in analyses:
            tk.Radiobutton(win, text=a, variable=var, value=a).pack(anchor="w")

        def rodar():
            analise = var.get()
            args = ["python", "src/advanced_analysis.py", self.selected_file, "--analise", analise]
            try:
                result = subprocess.run(args, capture_output=True, text=True, check=True)
                self.text_area.insert(tk.END, f"\n[Análise Avançada: {analise}]\n{result.stdout}\n")
                # Após análises avançadas, já vale habilitar ver gráficos / abrir pdf
                base = os.path.splitext(os.path.basename(self.selected_file))[0].replace('.', '_')
                output_dir = os.path.join("output", f"{base}")
                if os.path.exists(output_dir):
                    self.last_output_dir = output_dir
                    self.btn_view_graphs.config(state=tk.NORMAL)
                    self.btn_open_report.config(state=tk.NORMAL)
            except subprocess.CalledProcessError as e:
                self.text_area.insert(tk.END, f"\n[Análise Avançada: {analise}] Erro:\n{e.stderr}\n")
            win.destroy()

        Button(win, text="Executar", command=rodar).pack(pady=10)

    def show_help(self):
        help_text = (
            "Ajuda e documentação:\n"
            "- Selecione um arquivo de dados (CSV, XLSX, TSV, JSON).\n"
            "- Clique em 'Rodar Análise' para gerar estatísticas e relatórios.\n"
            "- Use os botões para visualizar gráficos (inclui subpastas), abrir PDFs e rodar módulos extras.\n"
            "- 'Análises Avançadas' executa distribuições, assimetria/curtose, correlação e regressão.\n"
            "- 'Gerar Dados Artificiais' usa o arquivo selecionado como base.\n"
            "- 'Detectar Dados Artificiais' analisa o arquivo selecionado e gera relatório na pasta output.\n"
        )
        messagebox.showinfo("Ajuda", help_text)


if __name__ == "__main__":
    app = App()
    app.mainloop()
