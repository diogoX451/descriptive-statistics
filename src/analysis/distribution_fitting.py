"""
Utilities for fitting candidate distributions and evaluating goodness of fit.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class FitResult:
    name: str
    params: Dict[str, Any]
    loglik: float
    aic: float
    bic: float
    gof_stat: float
    gof_pvalue: float
    method: str


def _safe_loglik(pdf_values: np.ndarray) -> float:
    eps = 1e-12
    pdf_values = np.clip(pdf_values, eps, None)
    return float(np.sum(np.log(pdf_values)))


def _calc_aic_bic(loglik: float, k: int, n: int) -> tuple[float, float]:
    aic = 2 * k - 2 * loglik
    bic = k * np.log(max(n, 1)) - 2 * loglik
    return float(aic), float(bic)


def _fit_continuous(
    data: np.ndarray,
    dist: stats.rv_continuous,
    dist_name: str,
) -> Optional[FitResult]:
    try:
        params = dist.fit(data)
        # scipy continuous distributions return (shape..., loc, scale)
        k = len(params)
        pdf_vals = dist.pdf(data, *params)
        loglik = _safe_loglik(pdf_vals)
        aic, bic = _calc_aic_bic(loglik, k, len(data))
        # KS test
        ks_stat, ks_pvalue = stats.kstest(data, dist_name, args=params)
        param_dict = _params_to_dict(dist, params)
        return FitResult(
            name=dist_name,
            params=param_dict,
            loglik=loglik,
            aic=aic,
            bic=bic,
            gof_stat=float(ks_stat),
            gof_pvalue=float(ks_pvalue),
            method="KS"
        )
    except Exception:
        return None


def _fit_discrete(
    data: np.ndarray,
    dist: stats.rv_discrete,
    dist_name: str,
) -> Optional[FitResult]:
    try:
        # Some discrete distributions don't support fit reliably.
        if dist_name == "poisson":
            mu = float(np.mean(data))
            params = (mu,)
            k = 1
        elif dist_name == "binom":
            n = int(np.max(data))
            if n <= 0:
                return None
            p = float(np.mean(data) / n)
            p = min(max(p, 1e-6), 1 - 1e-6)
            params = (n, p)
            k = 2
        else:
            # fallback to fit if available
            params = dist.fit(data)
            k = len(params)

        pmf_vals = dist.pmf(data, *params)
        loglik = _safe_loglik(pmf_vals)
        aic, bic = _calc_aic_bic(loglik, k, len(data))

        # Chi-square goodness of fit
        values, counts = np.unique(data, return_counts=True)
        expected = dist.pmf(values, *params) * len(data)
        # Avoid zeros
        mask = expected > 1e-8
        if mask.sum() < 2:
            return None
        chi_stat, chi_p = stats.chisquare(f_obs=counts[mask], f_exp=expected[mask])
        param_dict = _params_to_dict(dist, params)
        return FitResult(
            name=dist_name,
            params=param_dict,
            loglik=loglik,
            aic=aic,
            bic=bic,
            gof_stat=float(chi_stat),
            gof_pvalue=float(chi_p),
            method="Chi-square"
        )
    except Exception:
        return None


def _params_to_dict(dist: Any, params: tuple) -> Dict[str, Any]:
    # Build a readable parameter dictionary
    if hasattr(dist, "shapes") and dist.shapes:
        shape_names = [s.strip() for s in dist.shapes.split(",")]
    else:
        shape_names = []
    param_dict: Dict[str, Any] = {}
    idx = 0
    for name in shape_names:
        if idx < len(params):
            param_dict[name] = float(params[idx])
        idx += 1
    # loc/scale for continuous
    if len(params) >= idx + 2:
        param_dict["loc"] = float(params[idx])
        param_dict["scale"] = float(params[idx + 1])
    return param_dict


def fit_distributions(
    series: pd.Series,
    max_candidates: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Fits candidate distributions and returns ordered results by AIC.
    """
    data = series.dropna()
    if data.empty:
        return []

    is_numeric = pd.api.types.is_numeric_dtype(data)
    if not is_numeric:
        return []

    values = data.astype(float).values

    results: List[FitResult] = []

    if _is_integer_like(values):
        if np.min(values) < 0:
            return []
        candidates = max_candidates or ["poisson", "binom", "nbinom"]
        for name in candidates:
            dist = getattr(stats, name, None)
            if dist is None:
                continue
            fit = _fit_discrete(values, dist, name)
            if fit:
                results.append(fit)
    else:
        candidates = max_candidates or ["norm", "uniform", "expon", "gamma", "lognorm", "beta"]
        for name in candidates:
            dist = getattr(stats, name, None)
            if dist is None:
                continue
            fit = _fit_continuous(values, dist, name)
            if fit:
                results.append(fit)

    # Order by AIC (lower is better)
    results.sort(key=lambda r: r.aic)
    return [r.__dict__ for r in results]


def _is_integer_like(values: np.ndarray) -> bool:
    return np.all(np.isclose(values, np.round(values)))
