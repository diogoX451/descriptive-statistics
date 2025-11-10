"""
Tipo de variável Contínua.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from .ivariable_type import IVariableType
from analysis.statistical_functions import (
    calc_frequencies,
    calc_central_tendency,
    calc_separatrizes,
    calc_dispersion
)


class ContinuousType(IVariableType):
    """Variável numérica que pode assumir qualquer valor em um intervalo."""

    @property
    def name(self) -> str:
        return "Contínua"

    def is_applicable(self, data: pd.Series) -> bool:
        """Contínua é numérica com valores decimais."""
        if not pd.api.types.is_numeric_dtype(data):
            return False
        return True

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Análises completas para variável contínua:
        - Frequências (com bins para agrupar)
        - Tendência central (média, mediana, moda)
        - Separatrizes (quartis, decis, percentis)
        - Dispersão (amplitude, variância, desvio padrão, IQR, CV)
        """
        result = {}

        # Frequências com bins (agrupa valores contínuos em intervalos)
        # Usa regra de Sturges para determinar número de bins
        n = len(data.dropna())
        bins = int(1 + 3.322 * np.log10(n)) if n > 0 else 10
        result['frequencias'] = calc_frequencies(data, bins=bins)

        # Tendência central
        result['tendencia_central'] = calc_central_tendency(data)

        # Separatrizes
        result['separatrizes'] = calc_separatrizes(data)

        # Dispersão
        result['dispersao'] = calc_dispersion(data)

        return result
