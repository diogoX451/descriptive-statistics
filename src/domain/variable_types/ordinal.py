"""
Tipo de variável Ordinal.
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from .ivariable_type import IVariableType
from analysis.statistical_functions import calc_frequencies, calc_central_tendency


class OrdinalType(IVariableType):
    """Variável categórica com ordem definida."""

    def __init__(self, order: Optional[List] = None):
        """
        Inicializa tipo ordinal.

        Args:
            order: Lista opcional com a ordem das categorias
        """
        self.order = order

    @property
    def name(self) -> str:
        return "Ordinal"

    def is_applicable(self, data: pd.Series) -> bool:
        """
        Ordinal requer definição manual da ordem.
        Retorna True se a ordem foi definida.
        """
        return self.order is not None

    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """
        Análises para variável ordinal:
        - Frequências
        - Moda
        - Mediana (se ordem estiver definida)
        """
        result = {}

        # Se ordem foi definida, converte para categórico ordenado
        if self.order:
            data = pd.Categorical(data, categories=self.order, ordered=True)
            data = pd.Series(data)

        # Frequências
        result['frequencias'] = calc_frequencies(data)

        # Tendência central
        central_tendency = calc_central_tendency(data)
        result['moda'] = central_tendency['moda']

        # Mediana para ordinais (posição central na ordem)
        if self.order and not data.dropna().empty:
            # Converte para códigos numéricos baseados na ordem
            data_numeric = pd.Series(pd.Categorical(data, categories=self.order, ordered=True).codes)
            data_numeric = data_numeric[data_numeric >= 0]  # Remove -1 (NaN)
            if not data_numeric.empty:
                median_idx = int(data_numeric.median())
                result['mediana'] = self.order[median_idx]

        return result
