"""
Classe DataSet - Gerencia o conjunto de dados e suas variáveis.
"""
import pandas as pd
from typing import List, Optional, Dict, Any
from pathlib import Path
from .variable import Variable
from analysis.heuristics import infer_variable_type_strategy


class DataSet:
    """
    Representa um conjunto de dados.
    Gerencia uma coleção de objetos Variable.
    """

    def __init__(self, dataframe: pd.DataFrame, name: str = "Dataset"):
        """
        Inicializa um dataset.

        Args:
            dataframe: DataFrame com os dados
            name: Nome do dataset
        """
        self.name = name
        self.dataframe = dataframe
        self.variables: List[Variable] = []

        self._create_variables()

    def _create_variables(self):
        """Cria objetos Variable para cada coluna do DataFrame."""
        for column_name in self.dataframe.columns:
            series = self.dataframe[column_name]

            variable_type = infer_variable_type_strategy(series)

            variable = Variable(
                data=series,
                name=column_name,
                variable_type=variable_type
            )

            self.variables.append(variable)

    def get_variable(self, name: str) -> Optional[Variable]:
        """
        Obtém uma variável pelo nome.

        Args:
            name: Nome da variável

        Returns:
            Variable ou None se não encontrada
        """
        for variable in self.variables:
            if variable.name == name:
                return variable
        return None

    def analyze_variable(self, name: str):
        """
        Analisa e imprime os resultados de uma variável específica.

        Args:
            name: Nome da variável
        """
        variable = self.get_variable(name)
        if variable:
            variable.print_analysis()
        else:
            print(f"❌ Variável '{name}' não encontrada.")

    def analyze_all_variables(self):
        """Analisa e imprime os resultados de todas as variáveis."""
        print(f"\n{'#'*60}")
        print(f"# ANÁLISE COMPLETA DO DATASET: {self.name}")
        print(f"# Total de variáveis: {len(self.variables)}")
        print(f"# Total de registros: {len(self.dataframe)}")
        print(f"{'#'*60}\n")

        for variable in self.variables:
            variable.print_analysis()

    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo do dataset.

        Returns:
            Dicionário com resumo do dataset
        """
        return {
            'nome': self.name,
            'total_variaveis': len(self.variables),
            'total_registros': len(self.dataframe),
            'variaveis': [var.get_summary() for var in self.variables]
        }

    def print_summary(self):
        """Imprime um resumo do dataset."""
        summary = self.get_summary()

        print(f"\n{'='*60}")
        print(f"Dataset: {summary['nome']}")
        print(f"{'='*60}")
        print(f"Total de variáveis: {summary['total_variaveis']}")
        print(f"Total de registros: {summary['total_registros']}")
        print(f"\nVariáveis:")

        for var in summary['variaveis']:
            print(f"\n  • {var['nome']} ({var['tipo']})")
            print(f"    - Total de valores: {var['total_valores']}")
            print(f"    - Valores faltantes: {var['valores_faltantes']}")
            print(f"    - Valores únicos: {var['valores_unicos']}")

        print(f"\n{'='*60}\n")

    def export_all(self, output_base_dir: Path = None, generate_charts: bool = True, generate_pdfs: bool = True) -> Path:
        """
        Exporta análises completas apenas em PDF com imagens embutidas.

        Args:
            output_base_dir: Diretório base para output (padrão: output/)
            generate_charts: Se deve gerar gráficos (padrão: True)
            generate_pdfs: Se deve gerar PDFs dos relatórios (padrão: True)

        Returns:
            Caminho do diretório de output criado
        """
        import tempfile
        import shutil
        from visualization.chart_generator import ChartGenerator
        from export.report_generator import ReportGenerator
        from export.pdf_generator import PDFGenerator

        # Define diretório de output final
        if output_base_dir is None:
            output_base_dir = Path("output")

        # Cria diretório final específico para este dataset
        final_output_dir = output_base_dir / self.name.replace('.', '_')
        final_output_dir.mkdir(parents=True, exist_ok=True)

        # Cria diretório temporário para MDs e PNGs
        temp_dir = Path(tempfile.mkdtemp(prefix="stats_"))

        try:
            print(f"\n📂 Gerando análises...")

            # Gera análises para cada variável no diretório temporário
            for i, variable in enumerate(self.variables, 1):
                print(f"\n[{i}/{len(self.variables)}] Processando: {variable.name}")

                chart_paths = []
                if generate_charts:
                    try:
                        chart_paths = variable.generate_charts(temp_dir)
                        print(f"  ✅ {len(chart_paths)} gráfico(s) gerado(s)")
                    except Exception as e:
                        print(f"  ⚠️  Erro ao gerar gráficos: {e}")

                try:
                    report_path = variable.export_report(temp_dir, chart_paths)
                    print(f"  ✅ Relatório MD gerado")
                except Exception as e:
                    print(f"  ⚠️  Erro ao gerar relatório: {e}")

            # Gera gráfico resumo do dataset
            summary_chart_path = None
            if generate_charts:
                try:
                    chart_gen = ChartGenerator(temp_dir)
                    variables_summary = [var.get_summary() for var in self.variables]
                    summary_chart_path = chart_gen.generate_summary_chart(self.name, variables_summary)
                    print(f"\n✅ Gráfico resumo gerado")
                except Exception as e:
                    print(f"\n⚠️  Erro ao gerar gráfico resumo: {e}")

            # Gera relatório geral
            try:
                report_gen = ReportGenerator(temp_dir)
                variables_summary = [var.get_summary() for var in self.variables]
                general_report = report_gen.generate_dataset_report(
                    self.name,
                    variables_summary,
                    summary_chart_path
                )
                print(f"✅ Relatório geral MD gerado")
            except Exception as e:
                print(f"⚠️  Erro ao gerar relatório geral: {e}")

            # Gera PDFs de todos os relatórios Markdown
            if generate_pdfs:
                print(f"\n📄 Convertendo para PDF com imagens embutidas...")
                try:
                    pdf_gen = PDFGenerator(final_output_dir)  # PDFs vão direto para output
                    pdf_files = pdf_gen.generate_all_pdfs(temp_dir)  # Lê MDs do temp
                    print(f"✅ {len(pdf_files)} PDF(s) gerado(s)")
                except Exception as e:
                    print(f"⚠️  Erro ao gerar PDFs: {e}")

            print(f"\n🎉 Exportação concluída!")
            print(f"📄 PDFs salvos em: {final_output_dir.absolute()}")
            print(f"💡 Apenas PDFs foram mantidos (com imagens embutidas)\n")

        finally:
            # Limpa diretório temporário
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Arquivos temporários removidos")
            except Exception as e:
                print(f"⚠️  Aviso: não foi possível remover temporários: {e}")

        return final_output_dir

    def __repr__(self):
        return f"DataSet(name='{self.name}', variables={len(self.variables)}, records={len(self.dataframe)})"
