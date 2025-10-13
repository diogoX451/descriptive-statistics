import pandas as pd
from Processor.AData import AData
from Processor.Factory import register

@register("xlsx")
class XLSX(AData):
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
        self.data = pd.DataFrame(data)
        self.data.to_excel(self.file_path, index=False)

    def read(self, file_path=None):
        if file_path:
            self.file_path = file_path
        self.data = pd.read_excel(self.file_path)
        return self.data