"""
Interface para tipos de variáveis - Padrão Strategy.
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class IVariableType(ABC):
    """Interface abstrata para tipos de variáveis."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do tipo de variável."""
        pass

    @abstractmethod
    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Executa análises estatísticas apropriadas para este tipo de variável.

        Args:
            data: Série de dados

        Returns:
            Dicionário com resultados das análises
        """
        pass

    @abstractmethod
    def is_applicable(self, data: pd.Series) -> bool:
        """
        Verifica se este tipo é aplicável aos dados.

        Args:
            data: Série de dados

        Returns:
            True se o tipo é aplicável, False caso contrário
        """
        pass
