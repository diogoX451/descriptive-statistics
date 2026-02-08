# src/advanced_analysis.py
import os
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats

# Garante que imports do projeto funcionem quando rodar via "python src/advanced_analysis.py"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_loading.factory import create_reader, load_implementations  # noqa: E402
from analysis.heuristics import infer_variable_type_name  # noqa: E402


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# =========================
# 1) AJUSTE DE DISTRIBUIÇÕES
# =========================

def _loglik_normal(x: np.ndarray, mu: float, sigma: float) -> float:
    sigma = max(float(sigma), 1e-12)
    return float(np.sum(stats.norm.logpdf(x, loc=mu, scale=sigma)))


def _loglik_uniform(x: np.ndarray, a: float, b: float) -> float:
    if b <= a:
        return -np.inf
    return float(np.sum(stats.uniform.logpdf(x, loc=a, scale=(b - a))))


def _loglik_expon(x: np.ndarray, loc: float, scale: float) -> float:
    scale = max(float(scale), 1e-12)
    return float(np.sum(stats.expon.logpdf(x, loc=loc, scale=scale)))


def _aic(loglik: float, k: int) -> float:
    return float(2 * k - 2 * loglik)


def fit_and_rank_distributions(series: pd.Series) -> dict:
    x = series.dropna().to_numpy(dtype=float)

    if x.size < 5:
        return {"erro": "Poucos dados para ajuste (mínimo recomendado: 5)."}

    # Normal
    mu = float(np.mean(x))
    sigma = float(np.std(x, ddof=0))
    ll_norm = _loglik_normal(x, mu, sigma)
    aic_norm = _aic(ll_norm, k=2)
    ks_norm = stats.kstest(x, "norm", args=(mu, max(sigma, 1e-12)))

    # Uniforme
    a = float(np.min(x))
    b = float(np.max(x))
    ll_unif = _loglik_uniform(x, a, b)
    aic_unif = _aic(ll_unif, k=2)
    ks_unif = stats.kstest(x, "uniform", args=(a, max(b - a, 1e-12)))

    # Exponencial
    loc_e, scale_e = stats.expon.fit(x)
    ll_exp = _loglik_expon(x, float(loc_e), float(scale_e))
    aic_exp = _aic(ll_exp, k=2)
    ks_exp = stats.kstest(x, "expon", args=(float(loc_e), max(float(scale_e), 1e-12)))

    results = {
        "normal": {
            "params": {"mu": mu, "sigma": sigma},
            "ks_pvalue": float(ks_norm.pvalue),
            "aic": float(aic_norm),
        },
        "uniforme": {
            "params": {"min": a, "max": b},
            "ks_pvalue": float(ks_unif.pvalue),
            "aic": float(aic_unif),
        },
        "exponencial": {
            "params": {"loc": float(loc_e), "scale": float(scale_e)},
            "ks_pvalue": float(ks_exp.pvalue),
            "aic": float(aic_exp),
        },
    }

    best = min(results.keys(), key=lambda name: results[name]["aic"])
    results["melhor"] = best
    return results


def plot_distribution_fit(series: pd.Series, out_path: Path, title: str, fit: dict) -> None:
    x = series.dropna().to_numpy(dtype=float)
    if x.size < 5 or "erro" in fit:
        return

    plt.figure(figsize=(10, 6))
    plt.hist(x, bins="auto", density=True, alpha=0.5, edgecolor="black")

    xs = np.linspace(np.min(x), np.max(x), 400)

    mu = fit["normal"]["params"]["mu"]
    sigma = max(fit["normal"]["params"]["sigma"], 1e-12)
    plt.plot(xs, stats.norm.pdf(xs, loc=mu, scale=sigma), linewidth=2,
             label=f"Normal (AIC={fit['normal']['aic']:.1f}, p={fit['normal']['ks_pvalue']:.3f})")

    a = fit["uniforme"]["params"]["min"]
    b = fit["uniforme"]["params"]["max"]
    plt.plot(xs, stats.uniform.pdf(xs, loc=a, scale=max(b - a, 1e-12)), linewidth=2,
             label=f"Uniforme (AIC={fit['uniforme']['aic']:.1f}, p={fit['uniforme']['ks_pvalue']:.3f})")

    loc_e = fit["exponencial"]["params"]["loc"]
    scale_e = max(fit["exponencial"]["params"]["scale"], 1e-12)
    plt.plot(xs, stats.expon.pdf(xs, loc=loc_e, scale=scale_e), linewidth=2,
             label=f"Exponencial (AIC={fit['exponencial']['aic']:.1f}, p={fit['exponencial']['ks_pvalue']:.3f})")

    plt.title(title)
    plt.xlabel("Valores")
    plt.ylabel("Densidade")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=250)
    plt.close()


def run_distribution_fitting(file_path: str) -> int:
    load_implementations()

    if not os.path.exists(file_path):
        print(f"Erro: arquivo não encontrado: {file_path}")
        return 1

    _, ext = os.path.splitext(file_path)
    file_type = ext[1:].lower()
    if not file_type:
        print("Erro: arquivo sem extensão.")
        return 1

    reader = create_reader(file_type, file_path)
    df = reader.read()

    base_name = Path(file_path).name
    out_dir = Path("output") / Path(base_name).stem.replace(".", "_") / "distribuicoes"
    _safe_mkdir(out_dir)

    print("\n" + "=" * 70)
    print("AJUSTE DE DISTRIBUIÇÕES (Normal / Uniforme / Exponencial)")
    print("=" * 70)
    print(f"Arquivo: {file_path}")
    print(f"Saída:   {out_dir.resolve()}\n")

    numeric_cols = []
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            numeric_cols.append(col)
        else:
            s2 = pd.to_numeric(s, errors="coerce")
            if s2.notna().sum() >= max(5, int(0.5 * len(s2.dropna()))):
                df[col] = s2
                numeric_cols.append(col)

    if not numeric_cols:
        print("Nenhuma coluna numérica encontrada para ajuste.")
        return 0

    for col in numeric_cols:
        s = df[col].dropna()
        if s.empty:
            continue

        inferred = infer_variable_type_name(df[col])
        if inferred not in ("continuous", "discrete"):
            continue

        fit = fit_and_rank_distributions(df[col])

        print(f"\nVariável: {col}")
        print(f"Tipo inferido: {inferred}")
        if "erro" in fit:
            print(f" - {fit['erro']}")
            continue

        best = fit["melhor"]
        print(f"Melhor (por AIC): {best}")

        for dist_name in ("normal", "uniforme", "exponencial"):
            d = fit[dist_name]
            params = ", ".join([f"{k}={v:.4f}" for k, v in d["params"].items()])
            print(f" - {dist_name.capitalize():12s} | {params} | AIC={d['aic']:.2f} | KS p={d['ks_pvalue']:.4f}")

        safe_col = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in col)
        img_path = out_dir / f"{safe_col}_ajuste_distribuicoes.png"
        plot_distribution_fit(df[col], img_path, f"Ajuste de Distribuições — {col} (melhor: {best})", fit)
        print(f"Gráfico: {img_path.name}")

    print("\nConcluído.\n")
    return 0


# =========================
# 2) ASSIMETRIA E CURTOSE
# =========================

def _interpret_skew(skew: float) -> str:
    if abs(skew) < 0.5:
        return "aproximadamente simétrica"
    if skew > 0:
        return "assimetria positiva (cauda à direita)"
    return "assimetria negativa (cauda à esquerda)"


def _interpret_kurtosis_excess(excess: float) -> str:
    # excess kurtosis: 0 ~ normal (mesocúrtica)
    if excess < -0.5:
        return "platicúrtica (mais achatada que a normal)"
    if excess > 0.5:
        return "leptocúrtica (mais pontuda/caudas mais pesadas)"
    return "mesocúrtica (próxima da normal)"


def calc_skew_kurtosis(series: pd.Series) -> dict:
    x = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)

    if x.size < 5:
        return {"erro": "Poucos dados para calcular (mínimo recomendado: 5)."}

    skew = float(stats.skew(x, bias=False))
    kurt_excess = float(stats.kurtosis(x, fisher=True, bias=False))    # excesso (normal ~ 0)
    kurt_pearson = float(stats.kurtosis(x, fisher=False, bias=False))  # Pearson (normal ~ 3)

    return {
        "n": int(x.size),
        "skewness": skew,
        "kurtosis_excess": kurt_excess,
        "kurtosis_pearson": kurt_pearson,
        "interpretacao_skew": _interpret_skew(skew),
        "interpretacao_kurtosis": _interpret_kurtosis_excess(kurt_excess),
    }


def plot_skew_kurt(series: pd.Series, out_path: Path, title: str, metrics: dict) -> None:
    x = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if x.size < 5 or "erro" in metrics:
        return

    mean = float(np.mean(x))
    median = float(np.median(x))

    plt.figure(figsize=(10, 6))
    plt.hist(x, bins="auto", density=False, alpha=0.6, edgecolor="black")

    plt.axvline(mean, linestyle="--", linewidth=2, label=f"Média: {mean:.3f}")
    plt.axvline(median, linestyle="--", linewidth=2, label=f"Mediana: {median:.3f}")

    skew = metrics["skewness"]
    kurt_excess = metrics["kurtosis_excess"]

    info = (
        f"n={metrics['n']}\n"
        f"Skewness={skew:.3f}\n"
        f"Kurtosis(excesso)={kurt_excess:.3f}\n"
        f"{metrics['interpretacao_skew']}\n"
        f"{metrics['interpretacao_kurtosis']}"
    )

    plt.gca().text(
        0.98, 0.95, info,
        transform=plt.gca().transAxes,
        ha="right", va="top",
        bbox=dict(boxstyle="round", alpha=0.25)
    )

    plt.title(title)
    plt.xlabel("Valores")
    plt.ylabel("Frequência")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=250)
    plt.close()


def run_skew_kurtosis(file_path: str) -> int:
    load_implementations()

    if not os.path.exists(file_path):
        print(f"Erro: arquivo não encontrado: {file_path}")
        return 1

    _, ext = os.path.splitext(file_path)
    file_type = ext[1:].lower()
    if not file_type:
        print("Erro: arquivo sem extensão.")
        return 1

    reader = create_reader(file_type, file_path)
    df = reader.read()

    base_name = Path(file_path).name
    out_dir = Path("output") / Path(base_name).stem.replace(".", "_") / "assimetria_curtose"
    _safe_mkdir(out_dir)

    print("\n" + "=" * 70)
    print("ASSIMETRIA E CURTOSE (Skewness / Kurtosis)")
    print("=" * 70)
    print(f"Arquivo: {file_path}")
    print(f"Saída:   {out_dir.resolve()}\n")

    numeric_cols = []
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            numeric_cols.append(col)
        else:
            s2 = pd.to_numeric(s, errors="coerce")
            if s2.notna().sum() >= 5:
                df[col] = s2
                numeric_cols.append(col)

    if not numeric_cols:
        print("Nenhuma coluna numérica encontrada.")
        return 0

    rows = []
    for col in numeric_cols:
        inferred = infer_variable_type_name(df[col])
        if inferred not in ("continuous", "discrete"):
            continue

        metrics = calc_skew_kurtosis(df[col])

        print(f"\nVariável: {col}")
        print(f"Tipo inferido: {inferred}")
        if "erro" in metrics:
            print(f" - {metrics['erro']}")
            continue

        print(f" - n = {metrics['n']}")
        print(f" - Skewness = {metrics['skewness']:.4f} -> {metrics['interpretacao_skew']}")
        print(f" - Kurtosis (excesso) = {metrics['kurtosis_excess']:.4f} -> {metrics['interpretacao_kurtosis']}")
        print(f" - Kurtosis (Pearson) = {metrics['kurtosis_pearson']:.4f}")

        safe_col = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in col)
        img_path = out_dir / f"{safe_col}_hist_skew_kurt.png"
        plot_skew_kurt(df[col], img_path, f"Assimetria e Curtose — {col}", metrics)
        print(f"Gráfico: {img_path.name}")

        rows.append({
            "variavel": col,
            "n": metrics["n"],
            "skewness": metrics["skewness"],
            "kurtosis_excess": metrics["kurtosis_excess"],
            "kurtosis_pearson": metrics["kurtosis_pearson"],
            "interpretacao_skew": metrics["interpretacao_skew"],
            "interpretacao_kurtosis": metrics["interpretacao_kurtosis"],
        })

    if rows:
        summary_csv = out_dir / "resumo_assimetria_curtose.csv"
        pd.DataFrame(rows).to_csv(summary_csv, index=False, encoding="utf-8")
        print(f"\nResumo CSV: {summary_csv.name}")

    print("\nConcluído.\n")
    return 0

# =========================
# 3) CORRELAÇÃO E REGRESSÃO
# =========================

def _get_numeric_df(df: pd.DataFrame, min_non_na: int = 5) -> pd.DataFrame:
    """Retorna um DataFrame apenas com colunas numéricas (ou conversíveis)."""
    out = {}
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            if s.dropna().shape[0] >= min_non_na:
                out[col] = s.astype(float)
        else:
            s2 = pd.to_numeric(s, errors="coerce")
            if s2.dropna().shape[0] >= min_non_na:
                out[col] = s2.astype(float)
    return pd.DataFrame(out)


def compute_correlations(numeric_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula Pearson e Spearman para todos os pares de colunas numéricas.
    Retorna um DataFrame longo: var_x, var_y, n, pearson_r, pearson_p, spearman_r, spearman_p
    """
    cols = list(numeric_df.columns)
    rows = []

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            x_name, y_name = cols[i], cols[j]

            pair = numeric_df[[x_name, y_name]].dropna()
            n = int(len(pair))
            if n < 5:
                continue

            x = pair[x_name].to_numpy(dtype=float)
            y = pair[y_name].to_numpy(dtype=float)

            pearson_r, pearson_p = stats.pearsonr(x, y)
            spearman_r, spearman_p = stats.spearmanr(x, y)

            rows.append({
                "var_x": x_name,
                "var_y": y_name,
                "n": n,
                "pearson_r": float(pearson_r),
                "pearson_p": float(pearson_p),
                "spearman_r": float(spearman_r),
                "spearman_p": float(spearman_p),
                "abs_pearson_r": float(abs(pearson_r)),
                "abs_spearman_r": float(abs(spearman_r)),
            })

    if not rows:
        return pd.DataFrame(columns=[
            "var_x", "var_y", "n",
            "pearson_r", "pearson_p",
            "spearman_r", "spearman_p",
            "abs_pearson_r", "abs_spearman_r"
        ])

    return pd.DataFrame(rows).sort_values("abs_pearson_r", ascending=False)


def plot_scatter_with_line(x: np.ndarray, y: np.ndarray, out_path: Path, title: str,
                           slope: float, intercept: float, r: float) -> None:
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.7, edgecolors="black", linewidths=0.3)

    xs = np.linspace(np.min(x), np.max(x), 200)
    ys = slope * xs + intercept
    plt.plot(xs, ys, linewidth=2, label=f"Reta ajustada (r={r:.3f})")

    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=250)
    plt.close()


def run_correlation(file_path: str) -> int:
    load_implementations()

    if not os.path.exists(file_path):
        print(f"Erro: arquivo não encontrado: {file_path}")
        return 1

    _, ext = os.path.splitext(file_path)
    file_type = ext[1:].lower()
    if not file_type:
        print("Erro: arquivo sem extensão.")
        return 1

    df = create_reader(file_type, file_path).read()

    base_name = Path(file_path).name
    out_dir = Path("output") / Path(base_name).stem.replace(".", "_") / "correlacao_regressao"
    _safe_mkdir(out_dir)

    print("\n" + "=" * 70)
    print("CORRELAÇÃO (Pearson / Spearman)")
    print("=" * 70)
    print(f"Arquivo: {file_path}")
    print(f"Saída:   {out_dir.resolve()}\n")

    numeric_df = _get_numeric_df(df)
    if numeric_df.shape[1] < 2:
        print("É necessário pelo menos 2 colunas numéricas para correlação.")
        return 0

    corr_df = compute_correlations(numeric_df)

    if corr_df.empty:
        print("Não foi possível calcular correlações (pares com dados insuficientes).")
        return 0

    # Salva CSV com todos os pares
    all_csv = out_dir / "correlacoes_pares.csv"
    corr_df.drop(columns=["abs_pearson_r", "abs_spearman_r"], errors="ignore").to_csv(all_csv, index=False, encoding="utf-8")

    # Mostra top 10 no terminal
    print("Top 10 pares por |Pearson r|:\n")
    top10 = corr_df.head(10)
    for _, row in top10.iterrows():
        print(
            f"- {row['var_x']} vs {row['var_y']} | n={int(row['n'])} | "
            f"Pearson r={row['pearson_r']:.4f} (p={row['pearson_p']:.4g}) | "
            f"Spearman r={row['spearman_r']:.4f} (p={row['spearman_p']:.4g})"
        )

    print(f"\nCSV salvo: {all_csv.name}")
    return 0


def run_regression(file_path: str) -> int:
    load_implementations()

    if not os.path.exists(file_path):
        print(f"Erro: arquivo não encontrado: {file_path}")
        return 1

    _, ext = os.path.splitext(file_path)
    file_type = ext[1:].lower()
    if not file_type:
        print("Erro: arquivo sem extensão.")
        return 1

    df = create_reader(file_type, file_path).read()

    base_name = Path(file_path).name
    out_dir = Path("output") / Path(base_name).stem.replace(".", "_") / "correlacao_regressao"
    _safe_mkdir(out_dir)

    print("\n" + "=" * 70)
    print("REGRESSÃO LINEAR SIMPLES (Y = aX + b)")
    print("=" * 70)
    print(f"Arquivo: {file_path}")
    print(f"Saída:   {out_dir.resolve()}\n")

    numeric_df = _get_numeric_df(df)
    if numeric_df.shape[1] < 2:
        print("É necessário pelo menos 2 colunas numéricas para regressão.")
        return 0

    corr_df = compute_correlations(numeric_df)
    if corr_df.empty:
        print("Não foi possível escolher um par (dados insuficientes).")
        return 0

    # Escolhe o par com maior |Pearson|
    best = corr_df.iloc[0]
    x_name = best["var_x"]
    y_name = best["var_y"]

    pair = numeric_df[[x_name, y_name]].dropna()
    x = pair[x_name].to_numpy(dtype=float)
    y = pair[y_name].to_numpy(dtype=float)

    if len(x) < 5:
        print("Dados insuficientes para regressão.")
        return 0

    # Regressão linear simples
    lin = stats.linregress(x, y)
    slope = float(lin.slope)
    intercept = float(lin.intercept)
    r = float(lin.rvalue)
    p = float(lin.pvalue)
    stderr = float(lin.stderr)
    # erro padrão do intercepto (scipy >=1.7 tem intercept_stderr; senão calcula aproximado)
    intercept_stderr = float(getattr(lin, "intercept_stderr", np.nan))
    r2 = r ** 2

    print(f"Par escolhido automaticamente (maior |Pearson|): {x_name} (X) vs {y_name} (Y)")
    print(f"n = {len(x)}")
    print(f"Coef. angular (slope) a = {slope:.6f}")
    print(f"Intercepto (b) = {intercept:.6f}")
    print(f"r = {r:.6f}  |  R² = {r2:.6f}")
    print(f"p-value = {p:.6g}")
    print(f"Erro padrão do slope = {stderr:.6f}")
    if not np.isnan(intercept_stderr):
        print(f"Erro padrão do intercepto = {intercept_stderr:.6f}")

    # Previsões
    y_pred = slope * x + intercept
    pred_df = pd.DataFrame({
        x_name: x,
        y_name: y,
        "y_pred": y_pred,
        "residuo": (y - y_pred)
    })

    preds_csv = out_dir / f"regressao_predicoes_{x_name}_para_{y_name}.csv"
    pred_df.to_csv(preds_csv, index=False, encoding="utf-8")

    # Gráfico scatter + reta
    img_path = out_dir / f"regressao_{x_name}_vs_{y_name}.png"
    plot_scatter_with_line(x, y, img_path, f"Regressão Linear: {y_name} = a·{x_name} + b", slope, intercept, r)

    # Um TXT simples com os coeficientes (facilita colocar no relatório final)
    coef_txt = out_dir / f"regressao_{x_name}_vs_{y_name}_coeficientes.txt"
    with open(coef_txt, "w", encoding="utf-8") as f:
        f.write("REGRESSÃO LINEAR SIMPLES\n")
        f.write(f"X = {x_name}\nY = {y_name}\n\n")
        f.write(f"n = {len(x)}\n")
        f.write(f"a (slope) = {slope:.10f}\n")
        f.write(f"b (intercept) = {intercept:.10f}\n")
        f.write(f"r = {r:.10f}\n")
        f.write(f"R² = {r2:.10f}\n")
        f.write(f"p-value = {p:.10g}\n")
        f.write(f"stderr(slope) = {stderr:.10f}\n")
        f.write(f"stderr(intercept) = {intercept_stderr:.10f}\n")

    print(f"\nArquivos gerados:")
    print(f"- {preds_csv.name}")
    print(f"- {img_path.name}")
    print(f"- {coef_txt.name}")
    print("\nConcluído.\n")
    return 0


# =========================
# DISPATCHER (GUI)
# =========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Caminho do arquivo (csv/xlsx/tsv/json)")
    parser.add_argument("--analise", default="Ajuste de Distribuição")
    args = parser.parse_args()

    analise = args.analise.lower().strip()

    if analise == "ajuste de distribuição":
        raise SystemExit(run_distribution_fitting(args.file_path))

    if analise == "assimetria e curtose":
        raise SystemExit(run_skew_kurtosis(args.file_path))

    if analise == "correlação (pearson/spearman)":
        raise SystemExit(run_correlation(args.file_path))

    if analise == "regressão linear simples":
        raise SystemExit(run_regression(args.file_path))

    print(f"Análise '{args.analise}' ainda não implementada neste arquivo.")
    return



if __name__ == "__main__":
    main()
