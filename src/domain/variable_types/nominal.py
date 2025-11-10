"""
Tipo de variável Nominal.
"""
import pandas as pd
from typing import Dict, Any
from .ivariable_type import IVariableType
from analysis.statistical_functions import calc_frequencies, calc_central_tendency


class NominalType(IVariableType):
    """Variável categórica sem ordem intrínseca."""

    @property
    def name(self) -> str:
        return "Nominal"

    def is_applicable(self, data: pd.Series) -> bool:
        """Nominal é aplicável a dados categóricos/texto."""
        return not pd.api.types.is_numeric_dtype(data)

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Análises para variável nominal:
        - Frequências (absoluta, relativa, acumulada)
        - Moda
        """
        result = {}

        # Frequências
        result['frequencias'] = calc_frequencies(data)

        # Apenas moda para variáveis nominais
        central_tendency = calc_central_tendency(data)
        result['moda'] = central_tendency['moda']

        return result
