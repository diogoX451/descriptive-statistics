"""
Tipo de variável Contínua - Versão Final.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy.stats import skew, kurtosis, norm # Novas importações necessárias
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
        if not pd.api.types.is_numeric_dtype(data):
            return False
        return True

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        result = {}
        clean_data = data.dropna()
        n = len(clean_data)

        # Frequências (Regra de Sturges)
        bins = int(1 + 3.322 * np.log10(n)) if n > 0 else 10
        result['frequencias'] = calc_frequencies(data, bins=bins)

        # Tendência central, Separatrizes e Dispersão (Existentes)
        result['tendencia_central'] = calc_central_tendency(data)
        result['separatrizes'] = calc_separatrizes(data)
        result['dispersao'] = calc_dispersion(data)

        # --- VERSÃO FINAL --- 
        
        # 1. Assimetria e Curtose
        result['forma'] = {
            'assimetria': skew(clean_data),
            'curtose': kurtosis(clean_data)
        }

        # 2. Ajuste de Distribuição Normal
        if n > 0:
            mu, std = norm.fit(clean_data)
            result['distribuicao'] = {
                'tipo': 'Normal',
                'parametros': {'media': mu, 'desvio_padrão': std}
            }

        return result