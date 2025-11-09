from Processor.AData import AData
from Processor.Factory import register
import pandas as pd

@register("csv")
class CSV(AData):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def get_data(self):
        return self.data
    
    def get_data_key(self, key):
        if self.data is not None and key in self.data.columns:
            return self.data[key]
        else:
            raise KeyError(f"Chave '{key}' não encontrada nos dados.")
    
    def set_data(self, data):
        self.data = data
        self.data.to_csv(self.file_path, index=False)
    
    def read(self, file_path=None):
        if file_path:
            self.file_path = file_path
        self.data = pd.read_csv(self.file_path)
        return self.data

    def all_classificators(self):
        """Retorna a lista de classificadores disponíveis para estes dados.

        Implementação mínima: retorna lista vazia. Pode ser estendida posteriormente
        para integrar classificadores em `Processor/Classificator`.
        """
        return []

    def get_classificator(self, name):
        """Retorna um classificador pelo nome.

        Implementação mínima: lança KeyError indicando não encontrado. Subclasses
        ou integração futura podem retornar um objeto de classificador.
        """
        raise KeyError(f"Classificador '{name}' não encontrado.")