"""
Sistema de Análise de Estatística Descritiva
Arquitetura refatorada com padrões Factory e Strategy
"""
import os
import argparse
from data_loading.factory import create_reader, load_implementations
from domain.dataset import DataSet


def main():
    """Função principal do sistema."""

    load_implementations()

    parser = argparse.ArgumentParser(description="Sistema de Estatística Descritiva")
    parser.add_argument("file", nargs="?", default="teste.csv", help="Arquivo CSV/XLSX")
    parser.add_argument("--no-charts", action="store_true", help="Não gerar gráficos")
    parser.add_argument("--no-pdfs", action="store_true", help="Não gerar PDFs")
    parser.add_argument("--no-bivariate", action="store_true", help="Não gerar análise bivariada")
    parser.add_argument("--no-detector", action="store_true", help="Não executar detector de dados artificiais")
    parser.add_argument("--no-final-report", action="store_true", help="Não gerar relatório final consolidado")

    # Gerador univariado
    parser.add_argument("--generate-univariate", action="store_true", help="Gerar dados sintéticos univariados")
    parser.add_argument("--univariate-var", type=str, help="Nome da variável para gerar")
    parser.add_argument("--univariate-n", type=int, default=0, help="Quantidade de dados sintéticos")
    parser.add_argument("--univariate-method", choices=["fit", "bootstrap"], default="fit")
    parser.add_argument("--univariate-dist", type=str, default=None)
    parser.add_argument("--univariate-mean", type=float, default=None)
    parser.add_argument("--univariate-std", type=float, default=None)

    # Gerador bivariado
    parser.add_argument("--generate-bivariate", action="store_true", help="Gerar dados sintéticos bivariados")
    parser.add_argument("--bivariate-vars", nargs=2, help="Nomes das variáveis (X Y)")
    parser.add_argument("--bivariate-n", type=int, default=0, help="Quantidade de pares sintéticos")
    parser.add_argument("--bivariate-corr", type=float, default=None, help="Correlação alvo")
    parser.add_argument("--bivariate-mode", choices=["normal", "copula"], default="copula")
    parser.add_argument("--bivariate-dist-x", type=str, default=None)
    parser.add_argument("--bivariate-dist-y", type=str, default=None)

    # Consultas parametrizadas
    parser.add_argument("--binom-col", type=str, help="Coluna binária para binomial")
    parser.add_argument("--binom-n", type=int, default=None, help="n da binomial")
    parser.add_argument("--binom-k", type=int, default=None, help="k da binomial")
    parser.add_argument("--binom-success", type=str, default=None, help="Valor de sucesso (opcional)")

    parser.add_argument("--normal-col", type=str, help="Coluna numérica para normal")
    parser.add_argument("--normal-min", type=float, default=None, help="Limite inferior do intervalo")
    parser.add_argument("--normal-max", type=float, default=None, help="Limite superior do intervalo")

    parser.add_argument("--corr-pair", nargs=2, action="append", metavar=("X", "Y"),
                        help="Par de colunas para correlação (pode repetir)")
    parser.add_argument("--regress-predict", nargs=3, action="append", metavar=("X", "Y", "X0"),
                        help="Par de colunas para regressão e predição (pode repetir)")

    args = parser.parse_args()
    file_path = args.file

    if file_path == "teste.csv":
        print("💡 Dica: Você pode passar um arquivo como argumento:")
        print("   python src/main.py seu_arquivo.csv\n")

    if not os.path.exists(file_path):
        print(f"❌ Erro: Arquivo '{file_path}' não encontrado.")
        return

    _, extensao = os.path.splitext(file_path)
    file_type = extensao[1:].lower()

    if not file_type:
        print("❌ Erro: Arquivo sem extensão.")
        return

    print(f"\n🔄 Carregando arquivo: {file_path}")
    print(f"📄 Tipo de arquivo: {file_type.upper()}")

    try:
        reader = create_reader(file_type, file_path)

        df = reader.read()

        print(f"✅ Arquivo carregado com sucesso!")
        print(f"📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")

        dataset = DataSet(df, name=os.path.basename(file_path))
        dataset.generation_reports["execucao"] = {
            "arquivo": file_path,
            "args": vars(args)
        }

        dataset.print_summary()

        dataset.analyze_all_variables()

        # Exporta gráficos e relatórios
        print("\n" + "="*60)
        print("Gerando visualizações e relatórios...")
        print("="*60)

        # Geração de dados sintéticos (opcional)
        if args.generate_univariate and args.univariate_var and args.univariate_n > 0:
            dataset.generate_univariate_synthetic(
                args.univariate_var,
                n=args.univariate_n,
                method=args.univariate_method,
                dist_name=args.univariate_dist,
                mean=args.univariate_mean,
                std=args.univariate_std
            )

        if args.generate_bivariate and args.bivariate_vars and args.bivariate_n > 0:
            x_name, y_name = args.bivariate_vars
            dataset.generate_bivariate_synthetic(
                x_name,
                y_name,
                n=args.bivariate_n,
                target_corr=args.bivariate_corr,
                mode=args.bivariate_mode,
                dist_x=args.bivariate_dist_x,
                dist_y=args.bivariate_dist_y
            )

        custom_queries = {}
        if args.binom_col and args.binom_n is not None and args.binom_k is not None:
            custom_queries["binomial"] = {
                "col": args.binom_col,
                "n": args.binom_n,
                "k": args.binom_k,
                "success_value": args.binom_success,
            }
        if args.normal_col and args.normal_min is not None and args.normal_max is not None:
            custom_queries["normal_interval"] = {
                "col": args.normal_col,
                "a": args.normal_min,
                "b": args.normal_max,
            }
        if args.corr_pair:
            custom_queries["correlations"] = [
                {"x": x, "y": y} for x, y in args.corr_pair
            ]
        if args.regress_predict:
            regressions = []
            for x, y, x0 in args.regress_predict:
                regressions.append({"x": x, "y": y, "x0": float(x0)})
            custom_queries["regressions"] = regressions

        if custom_queries:
            dataset.run_custom_queries(custom_queries)

        try:
            output_dir = dataset.export_all(
                generate_charts=not args.no_charts,
                generate_pdfs=not args.no_pdfs,
                generate_bivariate=not args.no_bivariate,
                detect_artificial=not args.no_detector,
                generate_final_report=not args.no_final_report
            )
            print(f"\n✨ Visualizações e relatórios salvos em: {output_dir.absolute()}")
        except Exception as export_error:
            print(f"\n⚠️  Erro ao gerar visualizações: {export_error}")
            import traceback
            traceback.print_exc()

    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
    except ValueError as e:
        print(f"❌ Erro: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
