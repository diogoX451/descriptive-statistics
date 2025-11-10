"""
Leitor de arquivos XLSX.
"""
import pandas as pd
from ..idata_reader import IDataReader
from ..factory import register


@register("xlsx")
class XLSXReader(IDataReader):
    """Leitor de arquivos XLSX."""

    def __init__(self, file_path: str):
        """
        Inicializa o leitor XLSX.

        Args:
            file_path: Caminho do arquivo XLSX
        """
        self.file_path = file_path

    def read(self) -> pd.DataFrame:
        """
        Lê o arquivo XLSX e retorna um DataFrame.

        Returns:
            pd.DataFrame: Dados do XLSX

        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se houver erro ao ler o arquivo
        """
        try:
            return pd.read_excel(self.file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Erro ao ler XLSX: {str(e)}")
