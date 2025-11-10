"""
Heurísticas para inferência de tipos de variáveis.
"""
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.variable_types.ivariable_type import IVariableType


def infer_variable_type_name(series: pd.Series) -> str:
    """
    Infere o tipo de variável baseado em heurísticas.

    Args:
        series: Série de dados

    Returns:
        Nome do tipo inferido: 'binary', 'discrete', 'continuous', 'nominal', 'ordinal'
    """
    series_clean = series.dropna()

    if series_clean.empty:
        return 'nominal'

    n_unique = series_clean.nunique()

    # Binária: apenas 2 valores únicos
    if n_unique == 2:
        return 'binary'

    # Verifica se é numérico
    if pd.api.types.is_numeric_dtype(series_clean):
        # Verifica se todos os valores são inteiros
        if pd.api.types.is_integer_dtype(series_clean) or (series_clean % 1 == 0).all():
            # Discreta: inteiros com poucos valores únicos relativos ao tamanho
            if n_unique < len(series_clean) * 0.05:  # Menos de 5% de valores únicos
                return 'discrete'
            # Pode ser discreta mesmo com muitos valores
            return 'discrete'
        else:
            # Contínua: valores decimais
            return 'continuous'

    # Categórico/Texto
    # Ordinal é difícil de inferir automaticamente, retornamos nominal por padrão
    return 'nominal'


def infer_variable_type_strategy(series: pd.Series) -> 'IVariableType':
    """
    Infere o tipo de variável e retorna a estratégia apropriada.

    Args:
        series: Série de dados

    Returns:
        Instância de IVariableType apropriada
    """
    # Import lazy para evitar circular imports
    from domain.variable_types.binary import BinaryType
    from domain.variable_types.continuous import ContinuousType
    from domain.variable_types.discrete import DiscreteType
    from domain.variable_types.nominal import NominalType

    type_name = infer_variable_type_name(series)

    type_map = {
        'binary': BinaryType,
        'continuous': ContinuousType,
        'discrete': DiscreteType,
        'nominal': NominalType,
        'ordinal': NominalType,  # Ordinal requer input manual, usa nominal como fallback
    }

    return type_map[type_name]()
