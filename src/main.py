"""
Sistema de Análise de Estatística Descritiva
"""
import os
import sys
from data_loading.factory import create_reader, load_implementations
from domain.dataset import DataSet
from analysis.bivariate_analysis import BivariateAnalysis
from analysis.data_generator import DataGenerator

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

    try:
        reader = create_reader(file_type, file_path)
        df = reader.read()

        print(f"✅ Arquivo carregado com sucesso!")
        dataset = DataSet(df, name=os.path.basename(file_path))
        dataset.print_summary()
        dataset.analyze_all_variables()

        # ---  BIVARIADA E GERADOR ---
        print("\n" + "="*60)
        print("🚀 NOVAS FUNCIONALIDADES: VERSÃO FINAL")
        print("="*60)
        
        colunas_num = df.select_dtypes(include=['number']).columns
        
        # 1. Teste de Correlação e Regressão (Bivariada)
        if len(colunas_num) >= 2:
            c1, c2 = colunas_num[0], colunas_num[1]
            relacao = BivariateAnalysis.analyze_relation(df, c1, c2)
            print(f"📈 Relação entre {c1} e {c2}:")
            print(f"   - Correlação Pearson: {relacao['pearson']:.4f}")
            print(f"   - Regressão: {relacao['regressao']['formula']}")
        
        # 2. Teste do Gerador Univariado
        if not colunas_num.empty:
            print(f"\n🧬 Gerando dados artificiais baseados em '{colunas_num[0]}':")
            novos_dados = DataGenerator.generate_univariate(df[colunas_num[0]], n_samples=5)
            print(f"   Amostra gerada: {novos_dados}")

        # Exporta Gráficos e Relatórios

        print("\n" + "="*60)
        print("Gerando visualizações e relatórios...")
        print("="*60)

        output_dir = dataset.export_all(generate_charts=True)
        print(f"\n✨ Resultados salvos em: {output_dir.absolute()}")

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()