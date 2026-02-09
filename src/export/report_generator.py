"""
Gerador de relatórios em Markdown.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import matplotlib.pyplot as plt


class ReportGenerator:
    """Gera relatórios em Markdown com análises estatísticas."""

    def __init__(self, output_dir: Path):
        """
        Inicializa o gerador de relatórios.

        Args:
            output_dir: Diretório onde os relatórios serão salvos
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_variable_report(
        self,
        variable_name: str,
        variable_type: str,
        analysis_result: Dict[str, Any],
        chart_paths: List[Path],
    ) -> Path:
        """
        Gera relatório individual para uma variável.

        Args:
            variable_name: Nome da variável
            variable_type: Tipo da variável
            analysis_result: Resultados da análise
            chart_paths: Caminhos dos gráficos gerados

        Returns:
            Caminho do relatório gerado
        """
        report_path = self.output_dir / f"{variable_name}_relatorio.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Relatório de Análise: {variable_name}\n\n")
            f.write(f"**Tipo de Variável:** {variable_type}\n\n")
            f.write(
                f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            )
            f.write("---\n\n")

            # Frequências
            if "frequencias" in analysis_result:
                f.write("## 📊 Distribuição de Frequências\n\n")
                freq_df = analysis_result["frequencias"]

                f.write(
                    "| Valor | Freq. Absoluta | Freq. Relativa | Freq. Acumulada |\n"
                )
                f.write(
                    "|-------|----------------|----------------|------------------|\n"
                )

                # Limita a 20 linhas
                display_df = freq_df.head(20)
                for _, row in display_df.iterrows():
                    valor = row["valor"]
                    fa = row["freq_absoluta"]
                    fr = row["freq_relativa"]
                    fac = row["freq_acumulada"]
                    f.write(
                        f"| {valor} | {fa} | {fr:.4f} ({fr*100:.2f}%) | {fac:.4f} |\n"
                    )

                if len(freq_df) > 20:
                    f.write(f"\n*Mostrando top 20 de {len(freq_df)} valores*\n")

                f.write("\n")

            # Moda (para nominais e binárias)
            if "moda" in analysis_result and "tendencia_central" not in analysis_result:
                f.write("## 📈 Medida de Tendência Central\n\n")
                moda = analysis_result["moda"]
                if isinstance(moda, list):
                    f.write(f"**Moda:** {', '.join(map(str, moda))}\n\n")
                else:
                    f.write(f"**Moda:** {moda}\n\n")

            # Proporções (para binárias)
            if "proporcoes" in analysis_result:
                f.write("## 📊 Proporções\n\n")
                for key, value in analysis_result["proporcoes"].items():
                    f.write(f"- **{key}:** {value}\n")
                f.write("\n")

            # Tendência Central (para numéricas)
            if "tendencia_central" in analysis_result:
                f.write("## 📈 Medidas de Tendência Central\n\n")
                tc = analysis_result["tendencia_central"]

                f.write("| Medida | Valor |\n")
                f.write("|--------|-------|\n")
                if tc["media"] is not None:
                    f.write(f"| **Média** | {tc['media']:.4f} |\n")
                if tc["mediana"] is not None:
                    f.write(f"| **Mediana** | {tc['mediana']:.4f} |\n")
                if tc["moda"] is not None:
                    if isinstance(tc["moda"], list):
                        moda_str = ", ".join(
                            [
                                f"{m:.4f}" if isinstance(m, (int, float)) else str(m)
                                for m in tc["moda"]
                            ]
                        )
                        f.write(f"| **Moda** | {moda_str} |\n")
                    else:
                        f.write(f"| **Moda** | {tc['moda']} |\n")
                f.write("\n")

            # Separatrizes
            if "separatrizes" in analysis_result:
                sep = analysis_result["separatrizes"]

                if sep.get("quartis"):
                    f.write("## 📏 Separatrizes\n\n")
                    f.write("### Quartis\n\n")
                    f.write("| Quartil | Valor | Interpretação |\n")
                    f.write("|---------|-------|---------------|\n")
                    q1 = sep["quartis"]["Q1"]
                    q2 = sep["quartis"]["Q2"]
                    q3 = sep["quartis"]["Q3"]
                    f.write(
                        f"| Q1 (25%) | {q1:.4f} | 25% dos valores estão abaixo de {q1:.4f} |\n"
                    )
                    f.write(
                        f"| Q2 (50%) | {q2:.4f} | 50% dos valores estão abaixo de {q2:.4f} (mediana) |\n"
                    )
                    f.write(
                        f"| Q3 (75%) | {q3:.4f} | 75% dos valores estão abaixo de {q3:.4f} |\n"
                    )
                    f.write("\n")

            # Dispersão
            if "dispersao" in analysis_result:
                f.write("## 📐 Medidas de Dispersão\n\n")
                disp = analysis_result["dispersao"]

                f.write("| Medida | Valor | Interpretação |\n")
                f.write("|--------|-------|---------------|\n")

                if disp["amplitude"] is not None:
                    f.write(
                        f"| **Amplitude** | {disp['amplitude']:.4f} | Diferença entre máximo e mínimo |\n"
                    )

                if disp["variancia"] is not None:
                    f.write(
                        f"| **Variância** | {disp['variancia']:.4f} | Medida de dispersão ao quadrado |\n"
                    )

                if disp["desvio_padrao"] is not None:
                    f.write(
                        f"| **Desvio Padrão** | {disp['desvio_padrao']:.4f} | Dispersão média em relação à média |\n"
                    )

                if disp["intervalo_interquartil"] is not None:
                    f.write(
                        f"| **IQR (Q3-Q1)** | {disp['intervalo_interquartil']:.4f} | Amplitude dos 50% centrais |\n"
                    )

                if disp["coeficiente_variacao"] is not None:
                    cv = disp["coeficiente_variacao"]
                    f.write(f"| **Coef. Variação** | {cv:.2f}% | ")
                    if cv < 15:
                        f.write("Dados muito homogêneos |\n")
                    elif cv < 30:
                        f.write("Dados moderadamente homogêneos |\n")
                    else:
                        f.write("Dados heterogêneos |\n")

                f.write("\n")

            # Forma da distribuição
            if (
                "forma" in analysis_result
                and analysis_result["forma"].get("assimetria") is not None
            ):
                forma = analysis_result["forma"]
                f.write("## 📈 Forma da Distribuição\n\n")
                f.write("| Medida | Valor | Interpretação |\n")
                f.write("|--------|-------|---------------|\n")
                assim = forma.get("assimetria")
                curt_ex = forma.get("curtose_excesso")
                curt = forma.get("curtose")
                if assim is not None:
                    interp = (
                        "Simétrica"
                        if abs(assim) < 0.1
                        else (
                            "Assimetria positiva"
                            if assim > 0
                            else "Assimetria negativa"
                        )
                    )
                    f.write(f"| **Assimetria** | {assim:.4f} | {interp} |\n")
                if curt_ex is not None:
                    if curt_ex < 0:
                        kinterp = "Platicúrtica (menos pontiaguda)"
                    elif curt_ex > 0:
                        kinterp = "Leptocúrtica (mais pontiaguda)"
                    else:
                        kinterp = "Mesocúrtica (normal)"
                    f.write(f"| **Curtose (excesso)** | {curt_ex:.4f} | {kinterp} |\n")
                if curt is not None:
                    f.write(
                        f"| **Curtose (total)** | {curt:.4f} | Referência normal = 3 |\n"
                    )
                f.write("\n")

            # Ajuste de distribuições
            if "distribuicoes" in analysis_result and analysis_result["distribuicoes"]:
                f.write("## 🔎 Ajuste de Distribuições\n\n")
                f.write(
                    "| Distribuição | AIC | BIC | Estatística | p-valor | Método |\n"
                )
                f.write("|-------------|-----|-----|-------------|--------|--------|\n")
                for dist in analysis_result["distribuicoes"]:
                    f.write(
                        f"| {dist['name']} | {dist['aic']:.2f} | {dist['bic']:.2f} | "
                        f"{dist['gof_stat']:.4f} | {dist['gof_pvalue']:.4f} | {dist['method']} |\n"
                    )
                f.write("\n")

            # Interpretação
            f.write("## 💡 Interpretação\n\n")
            f.write(self._generate_interpretation(variable_type, analysis_result))
            f.write("\n")

            # Gráficos
            if chart_paths:
                f.write("## 📊 Visualizações\n\n")
                for chart_path in chart_paths:
                    chart_name = (
                        chart_path.stem.replace(f"{variable_name}_", "")
                        .replace("_", " ")
                        .title()
                    )
                    f.write(f"### {chart_name}\n\n")
                    f.write(f"![{chart_name}]({chart_path.name})\n\n")

        return report_path

    def _generate_interpretation(
        self, variable_type: str, analysis_result: Dict[str, Any]
    ) -> str:
        """
        Gera interpretação automática baseada nos resultados.

        Args:
            variable_type: Tipo da variável
            analysis_result: Resultados da análise

        Returns:
            Texto com interpretação
        """
        interpretation = []

        if variable_type == "Nominal":
            if "moda" in analysis_result:
                moda = analysis_result["moda"]
                if isinstance(moda, list):
                    interpretation.append(
                        f"- As categorias mais frequentes são: **{', '.join(map(str, moda))}**"
                    )
                else:
                    interpretation.append(f"- A categoria mais frequente é: **{moda}**")

        elif variable_type == "Binária":
            if "proporcoes" in analysis_result:
                props = analysis_result["proporcoes"]
                for key, value in props.items():
                    interpretation.append(f"- **{key}** representa {value} dos dados")

        elif variable_type in ["Discreta", "Contínua"]:
            tc = analysis_result.get("tendencia_central", {})
            disp = analysis_result.get("dispersao", {})

            # Média vs Mediana
            if tc.get("media") and tc.get("mediana"):
                media = tc["media"]
                mediana = tc["mediana"]
                diff = abs(media - mediana)
                if diff / media < 0.05:  # Menos de 5% de diferença
                    interpretation.append(
                        "- A **média e mediana** são muito próximas, indicando uma **distribuição aproximadamente simétrica**."
                    )
                elif media > mediana:
                    interpretation.append(
                        "- A **média é maior que a mediana**, sugerindo uma **assimetria positiva** (cauda à direita)."
                    )
                else:
                    interpretation.append(
                        "- A **mediana é maior que a média**, sugerindo uma **assimetria negativa** (cauda à esquerda)."
                    )

            # Coeficiente de Variação
            if disp.get("coeficiente_variacao"):
                cv = disp["coeficiente_variacao"]
                if cv < 15:
                    interpretation.append(
                        f"- Com **CV = {cv:.2f}%**, os dados são **muito homogêneos** (pouca dispersão)."
                    )
                elif cv < 30:
                    interpretation.append(
                        f"- Com **CV = {cv:.2f}%**, os dados são **moderadamente homogêneos**."
                    )
                else:
                    interpretation.append(
                        f"- Com **CV = {cv:.2f}%**, os dados são **heterogêneos** (alta dispersão)."
                    )

            # IQR
            if disp.get("intervalo_interquartil") and tc.get("mediana"):
                iqr = disp["intervalo_interquartil"]
                mediana = tc["mediana"]
                interpretation.append(
                    f"- Os **50% centrais** dos dados variam em uma amplitude de **{iqr:.2f}** em torno da mediana ({mediana:.2f})."
                )

        return (
            "\n".join(interpretation)
            if interpretation
            else "Análise concluída com sucesso."
        )

    def generate_dataset_report(
        self,
        dataset_name: str,
        variables_summary: List[Dict],
        summary_chart_path: Path = None,
    ) -> Path:
        """
        Gera relatório geral do dataset.

        Args:
            dataset_name: Nome do dataset
            variables_summary: Lista com resumo das variáveis
            summary_chart_path: Caminho do gráfico resumo

        Returns:
            Caminho do relatório gerado
        """
        report_path = self.output_dir / "RELATORIO_GERAL.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Relatório de Análise Estatística Descritiva\n\n")
            f.write(f"## Dataset: {dataset_name}\n\n")
            f.write(
                f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            )
            f.write("---\n\n")

            # Resumo Geral
            f.write("## 📊 Resumo Geral\n\n")
            f.write(f"- **Total de variáveis:** {len(variables_summary)}\n")

            if variables_summary:
                total_records = variables_summary[0]["total_valores"]
                f.write(f"- **Total de registros:** {total_records}\n\n")

                # Contagem por tipo
                from collections import Counter

                types_count = Counter([v["tipo"] for v in variables_summary])

                f.write("### Distribuição por Tipo de Variável\n\n")
                f.write("| Tipo | Quantidade |\n")
                f.write("|------|------------|\n")
                for tipo, count in sorted(types_count.items()):
                    f.write(f"| {tipo} | {count} |\n")
                f.write("\n")

            # Tabela de Variáveis
            f.write("## 📋 Detalhamento das Variáveis\n\n")
            f.write(
                "| Variável | Tipo | Total Valores | Valores Únicos | Valores Faltantes |\n"
            )
            f.write(
                "|----------|------|---------------|----------------|-------------------|\n"
            )

            for var in variables_summary:
                f.write(f"| {var['nome']} | {var['tipo']} | {var['total_valores']} | ")
                f.write(f"{var['valores_unicos']} | {var['valores_faltantes']} |\n")

            f.write("\n")

            # Gráfico Resumo
            if summary_chart_path and summary_chart_path.exists():
                f.write("## 📊 Visualização Geral\n\n")
                f.write(f"![Resumo do Dataset]({summary_chart_path.name})\n\n")

            # Links para relatórios individuais
            f.write("## 📄 Relatórios Individuais\n\n")
            for var in variables_summary:
                var_name = var["nome"]
                f.write(f"- [{var_name}]({var_name}_relatorio.md)\n")

            f.write("\n---\n\n")
            f.write(
                "*Relatório gerado automaticamente pelo Sistema de Análise de Estatística Descritiva*\n"
            )

        return report_path

    def generate_final_report(
        self,
        dataset_name: str,
        variables_summary: List[Dict],
        bivariate_results: List[Dict],
        artificial_report: Dict[str, Any],
        generation_reports: Dict[str, Any],
        summary_chart_path: Path = None,
        custom_queries: Dict[str, Any] = None,
    ) -> Path:
        """
        Gera relatório final consolidado com fórmulas e explicações.
        """
        report_path = self.output_dir / "RELATORIO_FINAL.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório Final de Análise Estatística\n\n")
            f.write(f"## Dataset: {dataset_name}\n\n")
            f.write(
                f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            )
            f.write("---\n\n")

            f.write("## ✅ Checklist de Entregas\n\n")
            f.write("- Distribuições (ajuste e métricas)\n")
            f.write("- Assimetria e curtose\n")
            f.write("- Correlação e regressão\n")
            f.write("- Gerador univariado funcional\n")
            f.write("- Gerador bivariado mantendo correlação\n")
            f.write("- Detector de dados artificiais com resumo\n")
            f.write("- Relatório final com imagens e fórmulas\n\n")

            f.write("## 📊 Resumo Geral\n\n")
            f.write(f"- **Total de variáveis:** {len(variables_summary)}\n")
            if variables_summary:
                total_records = variables_summary[0]["total_valores"]
                f.write(f"- **Total de registros:** {total_records}\n\n")

            if summary_chart_path and summary_chart_path.exists():
                f.write("## 🧭 Visão Geral do Dataset\n\n")
                f.write(f"![Resumo do Dataset]({summary_chart_path.name})\n\n")

            f.write("## 📐 Fórmulas Utilizadas (Resumo)\n\n")
            formula_images = self._render_formula_images()
            for title, path in formula_images:
                f.write(f"**{title}**\n\n")
                f.write(f"![{title}]({path.name})\n\n")

            if bivariate_results:
                f.write("## 🔗 Correlação e Regressão (Bivariada)\n\n")
                for item in bivariate_results:
                    corr = item.get("correlacao", {})
                    reg = item.get("regressao", {})
                    f.write(f"### {item['x']} vs {item['y']}\n\n")
                    if corr:
                        f.write(
                            f"- **Pearson r:** {corr.get('pearson_r'):.4f} (p={corr.get('pearson_p'):.4f})\n"
                        )
                        f.write(
                            f"- **Spearman ρ:** {corr.get('spearman_r'):.4f} (p={corr.get('spearman_p'):.4f})\n"
                        )
                    if reg:
                        f.write(
                            f"- **Regressão:** y = {reg.get('intercept'):.4f} + {reg.get('slope'):.4f}x\n"
                        )
                        f.write(
                            f"- **R²:** {reg.get('r2'):.4f} | **p-value:** {reg.get('p_value'):.4f}\n"
                        )
                        if reg.get("stderr") is not None:
                            f.write(
                                f"- **Erro padrão (coeficiente):** {reg.get('stderr'):.4f}\n"
                            )
                    f.write("\n")
                    chart_path = item.get("chart_path")
                    if chart_path:
                        f.write(
                            f"![Scatter {item['x']} vs {item['y']}]({chart_path.name})\n\n"
                        )

            if custom_queries:
                f.write("## 🧩 Consultas Parametrizadas\n\n")

                binom = custom_queries.get("binomial")
                if binom:
                    f.write("### Distribuição Binomial\n\n")
                    if binom.get("error"):
                        f.write(f"- Erro: {binom['error']}\n\n")
                    else:
                        f.write(
                            f"- Coluna: {binom.get('col')}\n"
                            f"- Sucesso: {binom.get('success_value')}\n"
                            f"- n={binom.get('n')} | k={binom.get('k')} | p={binom.get('p'):.4f}\n"
                            f"- P(X=k) = {binom.get('prob_k'):.6f}\n\n"
                        )

                normal = custom_queries.get("normal_interval")
                if normal:
                    f.write("### Distribuição Normal (Intervalo)\n\n")
                    if normal.get("error"):
                        f.write(f"- Erro: {normal['error']}\n\n")
                    else:
                        f.write(
                            f"- Coluna: {normal.get('col')}\n"
                            f"- Média={normal.get('mean'):.4f} | Desvio={normal.get('std'):.4f}\n"
                            f"- Intervalo: [{normal.get('a')}, {normal.get('b')}]\n"
                            f"- Probabilidade no intervalo = {normal.get('prob_interval'):.6f}\n\n"
                        )

                corr_list = custom_queries.get("correlations") or []
                if corr_list:
                    f.write("### Correlações Específicas\n\n")
                    for item in corr_list:
                        if item.get("error"):
                            f.write(f"- {item.get('x')} vs {item.get('y')}: {item['error']}\n")
                            continue
                        corr = item.get("correlacao", {})
                        f.write(
                            f"- {item.get('x')} vs {item.get('y')}: "
                            f"Pearson r={corr.get('pearson_r'):.4f} (p={corr.get('pearson_p'):.4f}), "
                            f"Spearman ρ={corr.get('spearman_r'):.4f} (p={corr.get('spearman_p'):.4f})\n"
                        )
                    f.write("\n")

                reg_list = custom_queries.get("regressions") or []
                if reg_list:
                    f.write("### Regressões com Predição\n\n")
                    for item in reg_list:
                        if item.get("error"):
                            f.write(f"- {item.get('x')} vs {item.get('y')}: {item['error']}\n")
                            continue
                        reg = item.get("regressao", {})
                        if reg.get("error"):
                            f.write(
                                f"- {item.get('x')} vs {item.get('y')}: {reg.get('error')}\n"
                            )
                            continue
                        f.write(
                            f"- {item.get('x')} vs {item.get('y')}: "
                            f"y = {reg.get('intercept'):.4f} + {reg.get('slope'):.4f}x | "
                            f"x0={reg.get('x0')} => ŷ={reg.get('y_hat'):.4f}\n"
                        )
                    f.write("\n")

            if artificial_report:
                f.write("## 🕵️ Detector de Dados Artificiais\n\n")
                score = artificial_report.get("score")
                level = artificial_report.get("score_level")
                if score is not None:
                    f.write(f"- **Score de suspeita:** {score}/100 ({level})\n\n")
                f.write("### Métricas avaliadas\n\n")
                for key, value in artificial_report.get("metrics", {}).items():
                    if isinstance(value, dict):
                        f.write(f"- **{key}**\n")
                        for m_key, m_val in value.items():
                            f.write(f"  - {m_key}: {m_val}\n")
                    else:
                        f.write(f"- {key}: {value}\n")
                f.write("\n### Thresholds usados\n\n")
                thresholds = artificial_report.get("thresholds", {})
                for k, v in thresholds.items():
                    f.write(f"- {k}: {v}\n")
                f.write("\n### Sinais encontrados\n\n")
                if artificial_report.get("flags"):
                    for flag in artificial_report["flags"]:
                        reason = flag.get("reason", "")
                        f.write(
                            f"- **{flag.get('type')}** ({flag.get('column', 'dataset')}): {reason}\n"
                        )
                else:
                    f.write("- Nenhum sinal forte detectado.\n")
                f.write("\n")

            if generation_reports:
                f.write("## 🧪 Geradores Sintéticos\n\n")
                for gen_type, items in generation_reports.items():
                    if gen_type == "execucao":
                        continue
                    f.write(f"### {gen_type.title()}\n\n")
                    for item in items:
                        if isinstance(item, dict):
                            f.write("- \n")
                            for k, v in item.items():
                                f.write(f"  - {k}: {v}\n")
                        else:
                            f.write(f"- {item}\n")
                    f.write("\n")

            if generation_reports.get("execucao"):
                f.write("## 🖥️ Registro de Execução\n\n")
                exec_info = generation_reports["execucao"]
                f.write("```\n")
                f.write(f"arquivo: {exec_info.get('arquivo')}\n")
                f.write(f"args: {exec_info.get('args')}\n")
                f.write("```\n\n")

            f.write("---\n\n")
            f.write("*Relatório final gerado automaticamente.*\n")

        return report_path

    def _render_formula_images(self):
        """
        Renderiza fórmulas em imagens PNG usando mathtext do matplotlib.
        """
        formulas = [
            ("Assimetria", r"$\gamma_1 = \frac{E[(X-\mu)^3]}{\sigma^3}$"),
            (
                "Curtose",
                r"$\gamma_2 = \frac{E[(X-\mu)^4]}{\sigma^4}$ e excesso $\gamma_2 - 3$",
            ),
            (
                "Correlação (Pearson)",
                r"$r = \frac{\sum (x-\bar{x})(y-\bar{y})}{(n-1)s_x s_y}$",
            ),
            ("Regressão linear", r"$\hat{y} = \beta_0 + \beta_1 x$"),
        ]

        rendered = []
        for i, (title, formula) in enumerate(formulas, 1):
            fig = plt.figure(figsize=(6, 1.2), dpi=200)
            fig.text(0.5, 0.5, formula, fontsize=14, ha="center", va="center")
            plt.axis("off")
            out_path = self.output_dir / f"formula_{i}.png"
            fig.savefig(out_path, bbox_inches="tight", transparent=True)
            plt.close(fig)
            rendered.append((title, out_path))

        return rendered
