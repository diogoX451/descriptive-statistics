"""
Tipo de variável Discreta.
"""
import pandas as pd
from typing import Dict, Any
from .ivariable_type import IVariableType
from analysis.statistical_functions import (
    calc_frequencies,
    calc_central_tendency,
    calc_separatrizes,
    calc_dispersion
)


class DiscreteType(IVariableType):
    """Variável numérica que assume valores inteiros (contagens)."""

    @property
    def name(self) -> str:
        return "Discreta"

    def is_applicable(self, data: pd.Series) -> bool:
        """Discreta é numérica e com valores inteiros."""
        if not pd.api.types.is_numeric_dtype(data):
            return False
        data_clean = data.dropna()
        return (data_clean % 1 == 0).all() if not data_clean.empty else False

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Análises completas para variável discreta:
        - Frequências
        - Tendência central (média, mediana, moda)
        - Separatrizes (quartis, decis, percentis)
        - Dispersão (amplitude, variância, desvio padrão, IQR, CV)
        """
        result = {}

        # Frequências
        result['frequencias'] = calc_frequencies(data)

        # Tendência central
        result['tendencia_central'] = calc_central_tendency(data)

        # Separatrizes
        result['separatrizes'] = calc_separatrizes(data)

        # Dispersão
        result['dispersao'] = calc_dispersion(data)

        return result
