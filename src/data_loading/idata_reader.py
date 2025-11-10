"""
Interface para leitores de dados.
"""
from abc import ABC, abstractmethod
import pandas as pd


class IDataReader(ABC):
    """Interface abstrata para leitores de dados."""

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Lê os dados do arquivo e retorna um DataFrame.

        Returns:
            pd.DataFrame: Dados carregados
        """
        pass
