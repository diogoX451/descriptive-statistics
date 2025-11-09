from Processor.Factory import create_data, load_implementations
from Processor.Analysis import infer_variable_type, calc_frequencies, calc_central_tendency
import os


def main():
    load_implementations()

    nome, extensao = os.path.splitext("teste.csv")
    data = create_data(extensao[1:], nome + extensao)
    data.read()

    df = data.get_data()
    print("Dados lidos: \n", df.head())

    # Bloco 2: Análise de Frequência e Tendência Central por coluna
    print("\n=== Análise (Bloco 2) por coluna ===\n")
    for col in df.columns:
        s = df[col]
        vtype = infer_variable_type(s)
        print(f"Coluna: {col} — tipo inferido: {vtype}")

        freqs = calc_frequencies(s)
        print("Frequências (abs / rel / cum):")
        print(freqs.to_string())

        central = calc_central_tendency(s)
        print("Tendência central:")
        for k, v in central.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()