"""
Custom query calculations (binomial, normal interval, correlations, regression predictions).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from analysis.bivariate_functions import calc_correlations, calc_linear_regression


def binomial_probability(
    series: pd.Series,
    n: int,
    k: int,
    success_value: Optional[Any] = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "n": n,
        "k": k,
        "success_value": success_value,
        "p": None,
        "prob_k": None,
        "sample_n": 0,
        "error": None,
    }

    if n < 0 or k < 0 or k > n:
        result["error"] = "n e k devem ser >= 0 e k <= n."
        return result

    series_clean = series.dropna()
    result["sample_n"] = int(len(series_clean))
    if series_clean.empty:
        result["error"] = "Série vazia."
        return result

    if success_value is None:
        unique = series_clean.unique()
        if len(unique) != 2:
            result["error"] = "A coluna não é binária e nenhum valor de sucesso foi informado."
            return result
        success_value = series_clean.value_counts().idxmax()
        result["success_value"] = success_value

    p = float((series_clean == success_value).mean())
    result["p"] = p
    result["prob_k"] = float(stats.binom.pmf(k, n, p))
    return result


def normal_interval_probability(
    series: pd.Series,
    a: float,
    b: float,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "a": a,
        "b": b,
        "mean": None,
        "std": None,
        "prob_interval": None,
        "sample_n": 0,
        "error": None,
    }

    series_clean = pd.to_numeric(series, errors="coerce").dropna()
    result["sample_n"] = int(len(series_clean))
    if series_clean.empty:
        result["error"] = "Série vazia ou não numérica."
        return result

    mean = float(series_clean.mean())
    std = float(series_clean.std())
    result["mean"] = mean
    result["std"] = std

    if std == 0:
        result["prob_interval"] = 1.0 if a <= mean <= b else 0.0
        return result

    prob = float(stats.norm.cdf(b, mean, std) - stats.norm.cdf(a, mean, std))
    result["prob_interval"] = prob
    return result


def correlation_for_pair(
    x: pd.Series,
    y: pd.Series,
) -> Dict[str, Any]:
    return calc_correlations(x, y)


def regression_with_prediction(
    x: pd.Series,
    y: pd.Series,
    x0: float,
) -> Dict[str, Any]:
    reg = calc_linear_regression(x, y)
    if not reg:
        return {"error": "Não foi possível calcular regressão."}
    y_hat = reg["intercept"] + reg["slope"] * x0
    reg["x0"] = float(x0)
    reg["y_hat"] = float(y_hat)
    return reg


def parse_pair_line(line: str, expected: int) -> Optional[Tuple[str, ...]]:
    raw = line.strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.replace(";", ",").split(",")]
    parts = [p for p in parts if p]
    if len(parts) != expected:
        return None
    return tuple(parts)

