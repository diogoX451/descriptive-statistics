"""
Sistema de Análise de Estatística Descritiva
Arquitetura refatorada com padrões Factory e Strategy
"""
import os
import sys
from data_loading.factory import create_reader, load_implementations
from domain.dataset import DataSet


def main():
    """Função principal do sistema."""

    load_implementations()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "teste.csv"
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

        dataset.print_summary()

        dataset.analyze_all_variables()

        # Exporta gráficos e relatórios
        print("\n" + "="*60)
        print("Gerando visualizações e relatórios...")
        print("="*60)

        try:
            output_dir = dataset.export_all(generate_charts=True)
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
