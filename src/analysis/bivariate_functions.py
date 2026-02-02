"""
Bivariate analysis utilities: correlation and regression.
"""
from __future__ import annotations

from typing import Dict, Any

import numpy as np
import pandas as pd
from scipy import stats


def calc_correlations(x: pd.Series, y: pd.Series) -> Dict[str, Any]:
    x_clean, y_clean = _align_numeric(x, y)
    if x_clean.empty:
        return {}

    pearson_r, pearson_p = stats.pearsonr(x_clean, y_clean)
    spearman_r, spearman_p = stats.spearmanr(x_clean, y_clean)

    return {
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
        "n": int(len(x_clean)),
    }


def calc_linear_regression(x: pd.Series, y: pd.Series) -> Dict[str, Any]:
    x_clean, y_clean = _align_numeric(x, y)
    if x_clean.empty:
        return {}

    reg = stats.linregress(x_clean, y_clean)
    # linregress returns intercept_stderr in newer scipy versions
    intercept_stderr = getattr(reg, "intercept_stderr", None)

    return {
        "slope": float(reg.slope),
        "intercept": float(reg.intercept),
        "r_value": float(reg.rvalue),
        "p_value": float(reg.pvalue),
        "stderr": float(reg.stderr),
        "intercept_stderr": float(intercept_stderr) if intercept_stderr is not None else None,
        "r2": float(reg.rvalue ** 2),
        "n": int(len(x_clean)),
    }


def predict_y(x: pd.Series, slope: float, intercept: float) -> np.ndarray:
    return slope * x + intercept


def _align_numeric(x: pd.Series, y: pd.Series) -> tuple[pd.Series, pd.Series]:
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    df = df[pd.to_numeric(df["x"], errors="coerce").notna()]
    df = df[pd.to_numeric(df["y"], errors="coerce").notna()]
    df["x"] = df["x"].astype(float)
    df["y"] = df["y"].astype(float)
    return df["x"], df["y"]
