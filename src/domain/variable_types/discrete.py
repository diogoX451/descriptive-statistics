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
    calc_dispersion
)

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

        # --- ITENS DA VERSÃO FINAL ---
        
        # 1. Assimetria e Curtose (Encontrar caudas e pico)
        if not clean_data.empty:
            result['forma'] = {
                'assimetria': float(skew(clean_data)),
                'curtose': float(kurtosis(clean_data))
            }
            
            # 2. Distribuição (Ajuste Simples)
            result['distribuicao'] = {
                'sugerida': "Poisson" if clean_data.mean() > 0 else "Indefinida",
                'media_lambda': float(clean_data.mean())
            }

        return result