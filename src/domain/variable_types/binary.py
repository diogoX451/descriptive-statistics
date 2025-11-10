"""
Tipo de variável Binária.
"""
import pandas as pd
from typing import Dict, Any
from .ivariable_type import IVariableType
from analysis.statistical_functions import calc_frequencies, calc_central_tendency


class BinaryType(IVariableType):
    """Variável com apenas duas categorias possíveis."""

    @property
    def name(self) -> str:
        return "Binária"

    def is_applicable(self, data: pd.Series) -> bool:
        """Binária tem exatamente 2 valores únicos."""
        return data.dropna().nunique() == 2

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Análises para variável binária:
        - Frequências
        - Moda
        - Proporções
        """
        result = {}

        # Frequências
        freq_df = calc_frequencies(data)
        result['frequencias'] = freq_df

        # Moda
        central_tendency = calc_central_tendency(data)
        result['moda'] = central_tendency['moda']

        # Proporções (mesma coisa que freq_relativa, mas mais explícito)
        result['proporcoes'] = {
            str(row['valor']): f"{row['freq_relativa']:.2%}"
            for _, row in freq_df.iterrows()
        }

        return result
