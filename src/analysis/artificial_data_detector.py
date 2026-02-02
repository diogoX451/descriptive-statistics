"""
Simple statistical detector for artificial data patterns.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats


DEFAULT_THRESHOLDS = {
    "duplicate_row_ratio": 0.2,
    "entropy_rounded_2": 2.0,
    "integer_ratio": 0.9,
    "last_digit_chi_p": 0.01,
    "benford_chi_p": 0.01,
}

DEFAULT_WEIGHTS = {
    "high_duplicate_rows": 25,
    "low_entropy": 20,
    "rounding_spike": 15,
    "last_digit_nonuniform": 20,
    "benford_mismatch": 20,
}


def detect_artificial_patterns(
    df: pd.DataFrame,
    thresholds: Optional[Dict[str, float]] = None,
    weights: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "flags": [],
        "metrics": {},
        "thresholds": thresholds or DEFAULT_THRESHOLDS,
        "score": 0,
        "score_level": "low",
    }
    thresholds = results["thresholds"]
    weights = weights or DEFAULT_WEIGHTS

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    results["metrics"]["numeric_columns"] = numeric_cols

    # Dataset-level metrics
    dup_ratio = float(df.duplicated().mean()) if len(df) else 0.0
    results["metrics"]["duplicate_row_ratio"] = dup_ratio
    if dup_ratio > thresholds["duplicate_row_ratio"]:
        results["flags"].append({
            "type": "high_duplicate_rows",
            "value": dup_ratio,
            "reason": "Mais de 20% das linhas são duplicadas."
        })

    # Per-column heuristics
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        col_metrics = {}

        # Entropy of rounded values (low entropy can be suspicious)
        rounded = series.round(2)
        value_counts = rounded.value_counts()
        probs = value_counts / value_counts.sum()
        entropy = float(-(probs * np.log2(probs)).sum())
        col_metrics["entropy_rounded_2"] = entropy
        if entropy < thresholds["entropy_rounded_2"] and len(value_counts) > 3:
            results["flags"].append({
                "type": "low_entropy",
                "column": col,
                "value": entropy,
                "reason": "Baixa entropia após arredondamento pode indicar geração artificial."
            })

        # Rounding spikes
        is_int = np.isclose(series, np.round(series)).mean()
        col_metrics["integer_ratio"] = float(is_int)
        if is_int > thresholds["integer_ratio"] and series.nunique() > 5:
            results["flags"].append({
                "type": "rounding_spike",
                "column": col,
                "value": float(is_int),
                "reason": "Muitos valores inteiros em dados contínuos sugerem arredondamento."
            })

        # Last digit uniformity (0-9) using chi-square
        last_digits = (np.abs(series * 10).astype(int) % 10)
        if len(last_digits) >= 30:
            obs = last_digits.value_counts().reindex(range(10), fill_value=0).values
            exp = np.full(10, obs.sum() / 10)
            chi_stat, chi_p = stats.chisquare(f_obs=obs, f_exp=exp)
            col_metrics["last_digit_chi_p"] = float(chi_p)
            if chi_p < thresholds["last_digit_chi_p"]:
                results["flags"].append({
                    "type": "last_digit_nonuniform",
                    "column": col,
                    "value": float(chi_p),
                    "reason": "Distribuição do último dígito é significativamente não uniforme."
                })

        # Benford's law (first digit) for positive values
        positives = series[series > 0]
        if len(positives) >= 30:
            first_digits = positives.astype(str).str.replace(".", "", regex=False).str.lstrip("0").str[0]
            first_digits = first_digits[first_digits.notna()]
            if len(first_digits) >= 30:
                obs = first_digits.value_counts().reindex(list("123456789"), fill_value=0).values
                benford = np.array([np.log10(1 + 1 / d) for d in range(1, 10)])
                exp = benford * obs.sum()
                chi_stat, chi_p = stats.chisquare(f_obs=obs, f_exp=exp)
                col_metrics["benford_chi_p"] = float(chi_p)
                if chi_p < thresholds["benford_chi_p"]:
                    results["flags"].append({
                        "type": "benford_mismatch",
                        "column": col,
                        "value": float(chi_p),
                        "reason": "Distribuição do primeiro dígito foge da lei de Benford."
                    })

        results["metrics"][col] = col_metrics

    # Score aggregation
    score = 0
    for flag in results["flags"]:
        score += weights.get(flag["type"], 10)
    score = min(score, 100)
    results["score"] = score
    if score >= 60:
        results["score_level"] = "high"
    elif score >= 30:
        results["score_level"] = "medium"
    else:
        results["score_level"] = "low"

    return results
