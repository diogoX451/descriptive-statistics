"""
Gerador de gráficos para diferentes tipos de variáveis.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import warnings

warnings.filterwarnings('ignore')

# Configuração de estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10


class ChartGenerator:
    """Gerador de gráficos estatísticos."""

    def __init__(self, output_dir: Path):
        """
        Inicializa o gerador de gráficos.

        Args:
            output_dir: Diretório onde os gráficos serão salvos
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_for_nominal(self, data: pd.Series, variable_name: str,
                            analysis_result: Dict[str, Any]) -> list:
        """
        Gera gráficos para variável nominal.
        - Gráfico de barras (frequências)

        Args:
            data: Série de dados
            variable_name: Nome da variável
            analysis_result: Resultado da análise estatística

        Returns:
            Lista de caminhos dos gráficos gerados
        """
        charts = []

        # Gráfico de Barras - Frequências
        fig, ax = plt.subplots(figsize=(12, 6))

        freq_df = analysis_result['frequencias']

        # Limita a 15 categorias para não poluir o gráfico
        if len(freq_df) > 15:
            freq_df = freq_df.head(15)
            title_suffix = " (Top 15)"
        else:
            title_suffix = ""

        bars = ax.bar(range(len(freq_df)), freq_df['freq_absoluta'], color='steelblue', alpha=0.8)
        ax.set_xlabel('Categorias', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequência Absoluta', fontsize=12, fontweight='bold')
        ax.set_title(f'Distribuição de Frequências - {variable_name}{title_suffix}',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(len(freq_df)))
        ax.set_xticklabels(freq_df['valor'], rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        # Adiciona valores sobre as barras
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_barras.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        return charts

    def generate_for_binary(self, data: pd.Series, variable_name: str,
                           analysis_result: Dict[str, Any]) -> list:
        """
        Gera gráficos para variável binária.
        - Gráfico de pizza (proporções)
        - Gráfico de barras

        Args:
            data: Série de dados
            variable_name: Nome da variável
            analysis_result: Resultado da análise

        Returns:
            Lista de caminhos dos gráficos gerados
        """
        charts = []
        freq_df = analysis_result['frequencias']

        # Gráfico de Pizza
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        colors = ['#66b3ff', '#ff9999']
        explode = (0.05, 0)

        ax1.pie(freq_df['freq_absoluta'], labels=freq_df['valor'], autopct='%1.1f%%',
               startangle=90, colors=colors, explode=explode, shadow=True)
        ax1.set_title(f'Proporções - {variable_name}', fontsize=14, fontweight='bold', pad=20)

        # Gráfico de Barras
        bars = ax2.bar(freq_df['valor'], freq_df['freq_absoluta'], color=colors, alpha=0.8)
        ax2.set_xlabel('Categorias', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Frequência Absoluta', fontsize=12, fontweight='bold')
        ax2.set_title(f'Frequências - {variable_name}', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(axis='y', alpha=0.3)

        # Adiciona valores sobre as barras
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=11)

        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_proporcoes.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        return charts

    def generate_for_discrete(self, data: pd.Series, variable_name: str,
                             analysis_result: Dict[str, Any]) -> list:
        """
        Gera gráficos para variável discreta.
        - Histograma
        - Boxplot
        - Gráfico de frequências

        Args:
            data: Série de dados
            variable_name: Nome da variável
            analysis_result: Resultado da análise

        Returns:
            Lista de caminhos dos gráficos gerados
        """
        charts = []
        data_clean = data.dropna()

        # 1. Histograma + Curva de Densidade
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.hist(data_clean, bins='auto', color='skyblue', alpha=0.7,
               edgecolor='black', label='Frequência')
        ax.set_xlabel('Valores', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequência', fontsize=12, fontweight='bold')
        ax.set_title(f'Histograma - {variable_name}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)

        # Adiciona linha vertical para média e mediana
        mean = analysis_result['tendencia_central']['media']
        median = analysis_result['tendencia_central']['mediana']
        ax.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Média: {mean:.2f}')
        ax.axvline(median, color='green', linestyle='--', linewidth=2, label=f'Mediana: {median:.2f}')

        ax.legend()
        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_histograma.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        # 2. Boxplot
        fig, ax = plt.subplots(figsize=(10, 6))

        bp = ax.boxplot([data_clean], vert=True, patch_artist=True,
                        labels=[variable_name], widths=0.5)

        # Colorir o boxplot
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)

        ax.set_ylabel('Valores', fontsize=12, fontweight='bold')
        ax.set_title(f'Boxplot - {variable_name}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)

        # Adiciona informações estatísticas
        q1 = analysis_result['separatrizes']['quartis']['Q1']
        q2 = analysis_result['separatrizes']['quartis']['Q2']
        q3 = analysis_result['separatrizes']['quartis']['Q3']

        text_info = f'Q1: {q1:.2f}\nQ2: {q2:.2f}\nQ3: {q3:.2f}'
        ax.text(1.15, q2, text_info, fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_boxplot.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        return charts

    def generate_for_continuous(self, data: pd.Series, variable_name: str,
                               analysis_result: Dict[str, Any]) -> list:
        """
        Gera gráficos para variável contínua.
        - Histograma com curva de densidade
        - Boxplot
        - QQ-plot (para verificar normalidade)

        Args:
            data: Série de dados
            variable_name: Nome da variável
            analysis_result: Resultado da análise

        Returns:
            Lista de caminhos dos gráficos gerados
        """
        charts = []
        data_clean = data.dropna()

        # 1. Histograma + Curva de Densidade KDE
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.hist(data_clean, bins='auto', color='skyblue', alpha=0.6,
               edgecolor='black', density=True, label='Frequência')

        # Adiciona curva de densidade
        from scipy import stats
        density = stats.gaussian_kde(data_clean)
        xs = np.linspace(data_clean.min(), data_clean.max(), 200)
        ax.plot(xs, density(xs), 'r-', linewidth=2, label='Densidade (KDE)')

        ax.set_xlabel('Valores', fontsize=12, fontweight='bold')
        ax.set_ylabel('Densidade', fontsize=12, fontweight='bold')
        ax.set_title(f'Histograma com Densidade - {variable_name}',
                    fontsize=14, fontweight='bold', pad=20)

        # Adiciona linha vertical para média e mediana
        mean = analysis_result['tendencia_central']['media']
        median = analysis_result['tendencia_central']['mediana']
        ax.axvline(mean, color='darkred', linestyle='--', linewidth=2,
                  label=f'Média: {mean:.2f}')
        ax.axvline(median, color='darkgreen', linestyle='--', linewidth=2,
                  label=f'Mediana: {median:.2f}')

        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_histograma_densidade.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        # 2. Boxplot Horizontal
        fig, ax = plt.subplots(figsize=(12, 4))

        bp = ax.boxplot([data_clean], vert=False, patch_artist=True,
                        labels=[variable_name], widths=0.5)

        for patch in bp['boxes']:
            patch.set_facecolor('lightcoral')
            patch.set_alpha(0.7)

        ax.set_xlabel('Valores', fontsize=12, fontweight='bold')
        ax.set_title(f'Boxplot - {variable_name}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)

        # Adiciona informações
        q1 = analysis_result['separatrizes']['quartis']['Q1']
        q2 = analysis_result['separatrizes']['quartis']['Q2']
        q3 = analysis_result['separatrizes']['quartis']['Q3']
        iqr = analysis_result['dispersao']['intervalo_interquartil']

        text_info = f'Q1: {q1:.2f} | Q2: {q2:.2f} | Q3: {q3:.2f}\nIQR: {iqr:.2f}'
        ax.text(0.02, 0.95, text_info, transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        chart_path = self.output_dir / f"{variable_name}_boxplot.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)

        return charts

    def generate_summary_chart(self, dataset_name: str, variables_summary: list) -> Optional[Path]:
        """
        Gera um gráfico resumo do dataset.

        Args:
            dataset_name: Nome do dataset
            variables_summary: Lista com resumo das variáveis

        Returns:
            Caminho do gráfico gerado
        """
        if not variables_summary:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Gráfico 1: Distribuição de Tipos de Variáveis
        from collections import Counter
        types_count = Counter([v['tipo'] for v in variables_summary])

        ax1.bar(types_count.keys(), types_count.values(), color='steelblue', alpha=0.8)
        ax1.set_xlabel('Tipo de Variável', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
        ax1.set_title('Distribuição de Tipos de Variáveis', fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='y', alpha=0.3)

        for i, (k, v) in enumerate(types_count.items()):
            ax1.text(i, v, str(v), ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Gráfico 2: Valores Faltantes por Variável
        names = [v['nome'][:15] + '...' if len(v['nome']) > 15 else v['nome']
                for v in variables_summary]
        missing = [v['valores_faltantes'] for v in variables_summary]

        bars = ax2.barh(names, missing, color='coral', alpha=0.8)
        ax2.set_xlabel('Valores Faltantes', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Variáveis', fontsize=12, fontweight='bold')
        ax2.set_title('Valores Faltantes por Variável', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(axis='x', alpha=0.3)

        for i, bar in enumerate(bars):
            width = bar.get_width()
            if width > 0:
                ax2.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{int(width)}',
                        ha='left', va='center', fontsize=9)

        plt.tight_layout()
        chart_path = self.output_dir / f"_resumo_dataset.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        return chart_path
