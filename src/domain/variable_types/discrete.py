"""
Tipo de variável Discreta - Versão Final.
"""
import pandas as pd
from typing import Dict, Any
from scipy.stats import skew, kurtosis # Importante para Assimetria e Curtose
from .ivariable_type import IVariableType
from analysis.statistical_functions import (
    calc_frequencies,
    calc_central_tendency,
    calc_separatrizes,
    calc_dispersion,
    calc_shape_metrics
)
from analysis.distribution_fitting import fit_distributions

class DiscreteType(IVariableType):
    """Variável numérica que assume valores inteiros (contagens)."""

    @property
    def name(self) -> str:
        return "Discreta"

    def is_applicable(self, data: pd.Series) -> bool:
        if not pd.api.types.is_numeric_dtype(data):
            return False
        data_clean = data.dropna()
        return (data_clean % 1 == 0).all() if not data_clean.empty else False

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        result = {}
        clean_data = data.dropna()

        # Cálculos Base (Prévia)
        result['frequencias'] = calc_frequencies(data)
        result['tendencia_central'] = calc_central_tendency(data)
        result['separatrizes'] = calc_separatrizes(data)
        result['dispersao'] = calc_dispersion(data)

        # Forma da distribuição
        result['forma'] = calc_shape_metrics(data)

        # Ajuste de distribuições
        result['distribuicoes'] = fit_distributions(data)

        return result
