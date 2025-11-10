"""
Funções estatísticas puras para cálculo de métricas.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any


def calc_frequencies(series: pd.Series, bins: Optional[int] = None) -> pd.DataFrame:
    """
    Calcula frequências absoluta, relativa e acumulada.

    Args:
        series: Série de dados
        bins: Número de intervalos para agrupar dados contínuos (opcional)

    Returns:
        DataFrame com colunas: valor, freq_absoluta, freq_relativa, freq_acumulada
    """
    series_clean = series.dropna()

    if series_clean.empty:
        return pd.DataFrame(columns=['valor', 'freq_absoluta', 'freq_relativa', 'freq_acumulada'])

    # Se bins for especificado, agrupa dados contínuos
    if bins and pd.api.types.is_numeric_dtype(series_clean):
        series_clean = pd.cut(series_clean, bins=bins)

    # Frequência absoluta
    freq_abs = series_clean.value_counts().sort_index()

    # Frequência relativa
    freq_rel = freq_abs / len(series_clean)

    # Frequência acumulada
    freq_acum = freq_rel.cumsum()

    # Monta DataFrame
    df_freq = pd.DataFrame({
        'valor': freq_abs.index,
        'freq_absoluta': freq_abs.values,
        'freq_relativa': freq_rel.values,
        'freq_acumulada': freq_acum.values
    })

    return df_freq


def calc_central_tendency(series: pd.Series) -> Dict[str, Optional[Any]]:
    """
    Calcula medidas de tendência central: média, mediana e moda.

    Args:
        series: Série de dados

    Returns:
        Dicionário com média, mediana e moda
    """
    series_clean = series.dropna()

    result = {
        'media': None,
        'mediana': None,
        'moda': None
    }

    if series_clean.empty:
        return result

    # Média (apenas para numéricos)
    if pd.api.types.is_numeric_dtype(series_clean):
        result['media'] = float(series_clean.mean())

    # Mediana (apenas para numéricos)
    if pd.api.types.is_numeric_dtype(series_clean):
        result['mediana'] = float(series_clean.median())

    # Moda (para todos os tipos)
    moda_values = series_clean.mode()
    if not moda_values.empty:
        result['moda'] = moda_values.tolist() if len(moda_values) > 1 else moda_values.iloc[0]

    return result


def calc_separatrizes(series: pd.Series) -> Dict[str, Any]:
    """
    Calcula separatrizes: quartis, decis e percentis.

    Args:
        series: Série de dados numéricos

    Returns:
        Dicionário com quartis, decis e percentis
    """
    series_clean = series.dropna()

    result = {
        'quartis': {},
        'decis': {},
        'percentis': {}
    }

    if series_clean.empty or not pd.api.types.is_numeric_dtype(series_clean):
        return result

    # Quartis
    result['quartis'] = {
        'Q1': float(series_clean.quantile(0.25)),
        'Q2': float(series_clean.quantile(0.50)),
        'Q3': float(series_clean.quantile(0.75))
    }

    # Decis
    result['decis'] = {
        f'D{i}': float(series_clean.quantile(i/10))
        for i in range(1, 10)
    }

    # Percentis (de 10 em 10)
    result['percentis'] = {
        f'P{i}': float(series_clean.quantile(i/100))
        for i in range(10, 100, 10)
    }

    return result


def calc_dispersion(series: pd.Series) -> Dict[str, Optional[float]]:
    """
    Calcula medidas de dispersão.

    Args:
        series: Série de dados numéricos

    Returns:
        Dicionário com amplitude, variância, desvio padrão, IQR e coeficiente de variação
    """
    series_clean = series.dropna()

    result = {
        'amplitude': None,
        'variancia': None,
        'desvio_padrao': None,
        'intervalo_interquartil': None,
        'coeficiente_variacao': None
    }

    if series_clean.empty or not pd.api.types.is_numeric_dtype(series_clean):
        return result

    # Amplitude
    result['amplitude'] = float(series_clean.max() - series_clean.min())

    # Variância
    result['variancia'] = float(series_clean.var())

    # Desvio padrão
    result['desvio_padrao'] = float(series_clean.std())

    # Intervalo interquartil (Q3 - Q1)
    q1 = series_clean.quantile(0.25)
    q3 = series_clean.quantile(0.75)
    result['intervalo_interquartil'] = float(q3 - q1)

    # Coeficiente de variação (apenas se média != 0)
    media = series_clean.mean()
    if media != 0:
        result['coeficiente_variacao'] = float((series_clean.std() / media) * 100)

    return result


def clean_data(series: pd.Series, remove_duplicates: bool = True, remove_outliers: bool = False) -> pd.Series:
    """
    Limpa os dados da série.

    Args:
        series: Série de dados
        remove_duplicates: Remove valores duplicados
        remove_outliers: Remove outliers usando método IQR

    Returns:
        Série limpa
    """
    series_clean = series.copy()

    # Remove valores faltantes
    series_clean = series_clean.dropna()

    # Remove duplicados
    if remove_duplicates:
        series_clean = series_clean.drop_duplicates()

    # Remove outliers (apenas para dados numéricos)
    if remove_outliers and pd.api.types.is_numeric_dtype(series_clean):
        q1 = series_clean.quantile(0.25)
        q3 = series_clean.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        series_clean = series_clean[(series_clean >= lower_bound) & (series_clean <= upper_bound)]

    return series_clean
