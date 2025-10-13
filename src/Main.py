from Processor.Factory import create_data, load_implementations
import os

def main():
    load_implementations()

    nome, extensao = os.path.splitext("teste.csv")
    data = create_data(extensao[1:], nome + extensao)
    data.read()

    print(data.get_data())


if __name__ == "__main__":
    main()