"""
Synthetic data generators (univariate and bivariate).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from .distribution_fitting import fit_distributions


def generate_univariate(
    series: pd.Series,
    n: int,
    method: str = "fit",
    dist_name: Optional[str] = None,
    mean: Optional[float] = None,
    std: Optional[float] = None,
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Generates synthetic univariate data.
    method: "fit" (fit distribution) or "bootstrap" (resample).
    """
    if n <= 0:
        return pd.Series(dtype=float), {}

    data = series.dropna()
    if data.empty:
        return pd.Series(dtype=float), {}

    if method == "bootstrap":
        sample = data.sample(n=n, replace=True).reset_index(drop=True)
        return sample, {"method": "bootstrap", "n": n}

    # Fit distribution and sample
    fit_results = fit_distributions(data, None)
    if dist_name:
        selected = next((r for r in fit_results if r["name"] == dist_name), None)
    else:
        selected = fit_results[0] if fit_results else None

    if not selected:
        # fallback to bootstrap if fit fails
        sample = data.sample(n=n, replace=True).reset_index(drop=True)
        return sample, {"method": "bootstrap_fallback", "n": n}

    dist = getattr(stats, selected["name"])
    params = _params_from_dict(selected["name"], selected["params"])
    sample = dist.rvs(*params, size=n)

    if mean is not None and std is not None and std > 0:
        sample = _match_mean_std(sample, mean, std)

    return pd.Series(sample), {
        "method": "fit",
        "distribution": selected["name"],
        "params": selected["params"],
        "n": n,
        "mean_override": mean,
        "std_override": std,
    }


def generate_bivariate(
    series_x: pd.Series,
    series_y: pd.Series,
    n: int,
    target_corr: Optional[float] = None,
    mode: str = "copula",
    dist_x: Optional[str] = None,
    dist_y: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generates bivariate data preserving correlation and optionally non-normal marginals.
    mode: "normal" or "copula"
    """
    if n <= 0:
        return pd.DataFrame(columns=["x", "y"]), {}

    x = series_x.dropna().astype(float)
    y = series_y.dropna().astype(float)
    min_len = min(len(x), len(y))
    if min_len == 0:
        return pd.DataFrame(columns=["x", "y"]), {}

    if target_corr is None:
        target_corr = float(np.corrcoef(x[:min_len], y[:min_len])[0, 1])

    # Generate correlated normals
    corr = max(min(target_corr, 0.999), -0.999)
    cov = np.array([[1.0, corr], [corr, 1.0]])
    z = np.random.multivariate_normal([0, 0], cov, size=n)

    if mode == "normal":
        x_new = z[:, 0] * np.std(x) + np.mean(x)
        y_new = z[:, 1] * np.std(y) + np.mean(y)
        meta = {
            "mode": "normal",
            "target_corr": corr,
            "mean_x": float(np.mean(x)),
            "std_x": float(np.std(x)),
            "mean_y": float(np.mean(y)),
            "std_y": float(np.std(y)),
            "n": n,
        }
        return pd.DataFrame({"x": x_new, "y": y_new}), meta

    # Gaussian copula for non-normal marginals
    u = stats.norm.cdf(z)

    fit_x = _select_fit(series_x, dist_x)
    fit_y = _select_fit(series_y, dist_y)

    dist_x_obj = getattr(stats, fit_x["name"])
    dist_y_obj = getattr(stats, fit_y["name"])

    params_x = _params_from_dict(fit_x["name"], fit_x["params"])
    params_y = _params_from_dict(fit_y["name"], fit_y["params"])

    x_new = dist_x_obj.ppf(u[:, 0], *params_x)
    y_new = dist_y_obj.ppf(u[:, 1], *params_y)

    meta = {
        "mode": "copula",
        "target_corr": corr,
        "dist_x": fit_x["name"],
        "dist_y": fit_y["name"],
        "params_x": fit_x["params"],
        "params_y": fit_y["params"],
        "n": n,
    }
    return pd.DataFrame({"x": x_new, "y": y_new}), meta


def _select_fit(series: pd.Series, dist_name: Optional[str]) -> Dict[str, Any]:
    fit_results = fit_distributions(series, None)
    if dist_name:
        selected = next((r for r in fit_results if r["name"] == dist_name), None)
        if selected:
            return selected
    if fit_results:
        return fit_results[0]
    # fallback to normal
    return {"name": "norm", "params": {"loc": float(series.mean()), "scale": float(series.std() or 1.0)}}


def _params_from_dict(dist_name: str, params: Dict[str, Any]) -> tuple:
    dist = getattr(stats, dist_name)
    if hasattr(dist, "shapes") and dist.shapes:
        shape_names = [s.strip() for s in dist.shapes.split(",")]
    else:
        shape_names = []
    values = []
    for name in shape_names:
        if name in params:
            values.append(params[name])
    if "loc" in params:
        values.append(params["loc"])
    if "scale" in params:
        values.append(params["scale"])
    return tuple(values)


def _match_mean_std(values: np.ndarray, mean: float, std: float) -> np.ndarray:
    current_mean = np.mean(values)
    current_std = np.std(values) or 1.0
    normalized = (values - current_mean) / current_std
    return normalized * std + mean
