# src/prof_pablo_tasks.py
import os
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_loading.factory import create_reader, load_implementations  # noqa: E402


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_df(path: str) -> pd.DataFrame:
    load_implementations()
    ext = Path(path).suffix.lower().replace(".", "")
    if not ext:
        raise ValueError("Arquivo sem extensão.")
    return create_reader(ext, path).read()


def _find_col(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """
    Procura coluna por palavras-chave (case-insensitive, match por substring).
    """
    cols = list(df.columns)
    lower_map = {c: str(c).lower() for c in cols}

    for kw in keywords:
        kw = kw.lower()
        for c, lc in lower_map.items():
            if kw in lc:
                return c
    return None


def _to_numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce")


def _linear_regression_predict(x: np.ndarray, y: np.ndarray, x0: float):
    lin = stats.linregress(x, y)
    slope = float(lin.slope)
    intercept = float(lin.intercept)
    r = float(lin.rvalue)
    r2 = r ** 2
    p = float(lin.pvalue)
    stderr = float(lin.stderr)
    intercept_stderr = float(getattr(lin, "intercept_stderr", np.nan))
    y0 = slope * x0 + intercept
    return {
        "slope": slope,
        "intercept": intercept,
        "r": r,
        "r2": r2,
        "p": p,
        "stderr_slope": stderr,
        "stderr_intercept": intercept_stderr,
        "x0": x0,
        "y0": float(y0),
    }


def run_tasks(births_path: str, fish_path: str) -> int:
    births = _load_df(births_path)
    fish = _load_df(fish_path)

    out_dir = Path("output") / "tarefas_prof_pablo"
    _safe_mkdir(out_dir)

    lines = []
    lines.append("# Tarefas — Professor Pablo\n")
    lines.append(f"Arquivo nascimentos: `{births_path}`\n")
    lines.append(f"Arquivo peixes: `{fish_path}`\n")

    # ============================
    # 1) Binomial do sexo (bebês)
    # ============================
    sex_col = _find_col(births, ["sexo", "sex", "gender"])
    if sex_col is None:
        lines.append("## 1) Binomial do sexo\n")
        lines.append("⚠️ Não encontrei coluna de sexo automaticamente. (Procurei por: sexo/sex/gender)\n")
    else:
        s = births[sex_col].astype(str).str.strip().str.lower()
        # tenta inferir "masculino"
        male_mask = s.str.contains("m") | s.str.contains("masc") | s.str.contains("hom") | s.str.contains("male")
        # Se a coluna for tipo "M/F" isso funciona; se for "1/0" também pode cair em contains("m") errado.
        # Ajuste adicional para casos numéricos:
        s_num = pd.to_numeric(births[sex_col], errors="coerce")
        if s_num.notna().sum() > 0 and s_num.dropna().isin([0, 1]).mean() > 0.9:
            # assume 1 = homem, 0 = mulher (convenção comum)
            male_mask = (s_num == 1)

        p_male = float(male_mask.mean())
        prob = float(stats.binom.pmf(3, 10, p_male))

        lines.append("## 1) Distribuição Binomial do sexo\n")
        lines.append(f"- Coluna usada: **{sex_col}**\n")
        lines.append(f"- Estimativa de p(homem) = {p_male:.4f}\n")
        lines.append(f"- Probabilidade de exatamente 3 homens em 10 nascimentos:\n")
        lines.append(f"  - **P(X=3 | n=10, p={p_male:.4f}) = {prob:.6f}**\n")
        lines.append("  - Fórmula: P(X=k)=C(n,k)·p^k·(1-p)^(n-k)\n")

    # ==========================================
    # 2) Normal do peso (peixes) entre 400-500g
    # ==========================================
    weight_col_fish = _find_col(fish, ["peso", "weight", "gram", "g"])
    if weight_col_fish is None:
        lines.append("\n## 2) Normal do peso dos peixes\n")
        lines.append("⚠️ Não encontrei coluna de peso automaticamente. (Procurei por: peso/weight/gram/g)\n")
    else:
        w = _to_numeric_series(fish, weight_col_fish).dropna()
        mu = float(w.mean())
        sd = float(w.std(ddof=0))
        sd = max(sd, 1e-12)
        pct = float((stats.norm.cdf(500, mu, sd) - stats.norm.cdf(400, mu, sd)) * 100)

        lines.append("\n## 2) Distribuição Normal do peso (peixes)\n")
        lines.append(f"- Coluna usada: **{weight_col_fish}**\n")
        lines.append(f"- Parâmetros estimados: μ={mu:.4f}, σ={sd:.4f}\n")
        lines.append(f"- Percentual entre 400g e 500g:\n")
        lines.append(f"  - **P(400 ≤ X ≤ 500) = {pct:.2f}%**\n")
        lines.append("  - Fórmula: P(a≤X≤b)=Φ((b-μ)/σ) - Φ((a-μ)/σ)\n")

    # =======================================
    # 3) Correlação peso x tamanho (peixes)
    # =======================================
    length_col_fish = _find_col(fish, ["tamanho", "length", "compr", "cm", "size"])
    if weight_col_fish and length_col_fish:
        pair = fish[[weight_col_fish, length_col_fish]].copy()
        pair[weight_col_fish] = pd.to_numeric(pair[weight_col_fish], errors="coerce")
        pair[length_col_fish] = pd.to_numeric(pair[length_col_fish], errors="coerce")
        pair = pair.dropna()
        if len(pair) >= 5:
            x = pair[weight_col_fish].to_numpy(float)
            y = pair[length_col_fish].to_numpy(float)
            pr, pp = stats.pearsonr(x, y)
            sr, sp = stats.spearmanr(x, y)
            lines.append("\n## 3) Correlação (peixes): peso × tamanho\n")
            lines.append(f"- Colunas: **{weight_col_fish}** (peso) e **{length_col_fish}** (tamanho)\n")
            lines.append(f"- Pearson r={pr:.4f} (p={pp:.4g})\n")
            lines.append(f"- Spearman r={sr:.4f} (p={sp:.4g})\n")
        else:
            lines.append("\n## 3) Correlação (peixes)\n")
            lines.append("⚠️ Dados insuficientes após limpeza (mín. 5 pares).\n")
    else:
        lines.append("\n## 3) Correlação (peixes)\n")
        lines.append("⚠️ Não encontrei automaticamente peso e/ou tamanho.\n")

    # ==========================================
    # 4) Correlação idade mãe x peso bebê (nasc.)
    # ==========================================
    mother_age_col = _find_col(births, ["idade", "age", "mae", "mãe"])
    baby_weight_col = _find_col(births, ["peso", "weight", "crianca", "criança", "bebe", "bebê"])
    if mother_age_col and baby_weight_col:
        pair = births[[mother_age_col, baby_weight_col]].copy()
        pair[mother_age_col] = pd.to_numeric(pair[mother_age_col], errors="coerce")
        pair[baby_weight_col] = pd.to_numeric(pair[baby_weight_col], errors="coerce")
        pair = pair.dropna()
        if len(pair) >= 5:
            x = pair[mother_age_col].to_numpy(float)
            y = pair[baby_weight_col].to_numpy(float)
            pr, pp = stats.pearsonr(x, y)
            sr, sp = stats.spearmanr(x, y)
            lines.append("\n## 4) Correlação (nascimentos): idade da mãe × peso da criança\n")
            lines.append(f"- Colunas: **{mother_age_col}** (idade) e **{baby_weight_col}** (peso)\n")
            lines.append(f"- Pearson r={pr:.4f} (p={pp:.4g})\n")
            lines.append(f"- Spearman r={sr:.4f} (p={sp:.4g})\n")
        else:
            lines.append("\n## 4) Correlação (nascimentos)\n")
            lines.append("⚠️ Dados insuficientes após limpeza (mín. 5 pares).\n")
    else:
        lines.append("\n## 4) Correlação (nascimentos)\n")
        lines.append("⚠️ Não encontrei automaticamente idade da mãe e/ou peso da criança.\n")

    # ==========================================
    # 5) Regressão peixes: tamanho ~ peso, X=1200
    # ==========================================
    if weight_col_fish and length_col_fish:
        pair = fish[[weight_col_fish, length_col_fish]].copy()
        pair[weight_col_fish] = pd.to_numeric(pair[weight_col_fish], errors="coerce")
        pair[length_col_fish] = pd.to_numeric(pair[length_col_fish], errors="coerce")
        pair = pair.dropna()
        if len(pair) >= 5:
            x = pair[weight_col_fish].to_numpy(float)
            y = pair[length_col_fish].to_numpy(float)
            reg = _linear_regression_predict(x, y, x0=1200.0)
            lines.append("\n## 5) Regressão (peixes): prever tamanho para 1200g\n")
            lines.append(f"Modelo: **{length_col_fish} = a·{weight_col_fish} + b**\n")
            lines.append(f"- a (slope) = {reg['slope']:.6f}\n")
            lines.append(f"- b (intercept) = {reg['intercept']:.6f}\n")
            lines.append(f"- r={reg['r']:.4f}  |  R²={reg['r2']:.4f}\n")
            lines.append(f"- erro padrão do slope = {reg['stderr_slope']:.6f}\n")
            if not np.isnan(reg["stderr_intercept"]):
                lines.append(f"- erro padrão do intercepto = {reg['stderr_intercept']:.6f}\n")
            lines.append(f"- **Previsão:** se peso = 1200g, então tamanho ≈ **{reg['y0']:.4f}**\n")
        else:
            lines.append("\n## 5) Regressão (peixes)\n")
            lines.append("⚠️ Dados insuficientes após limpeza.\n")
    else:
        lines.append("\n## 5) Regressão (peixes)\n")
        lines.append("⚠️ Não encontrei automaticamente peso e tamanho.\n")

    # ==========================================
    # 6) Regressão nascimentos: peso ~ idade, X=60
    # ==========================================
    if mother_age_col and baby_weight_col:
        pair = births[[mother_age_col, baby_weight_col]].copy()
        pair[mother_age_col] = pd.to_numeric(pair[mother_age_col], errors="coerce")
        pair[baby_weight_col] = pd.to_numeric(pair[baby_weight_col], errors="coerce")
        pair = pair.dropna()
        if len(pair) >= 5:
            x = pair[mother_age_col].to_numpy(float)
            y = pair[baby_weight_col].to_numpy(float)
            reg = _linear_regression_predict(x, y, x0=60.0)
            lines.append("\n## 6) Regressão (nascimentos): prever peso do bebê para mãe de 60 anos\n")
            lines.append(f"Modelo: **{baby_weight_col} = a·{mother_age_col} + b**\n")
            lines.append(f"- a (slope) = {reg['slope']:.6f}\n")
            lines.append(f"- b (intercept) = {reg['intercept']:.6f}\n")
            lines.append(f"- r={reg['r']:.4f}  |  R²={reg['r2']:.4f}\n")
            lines.append(f"- erro padrão do slope = {reg['stderr_slope']:.6f}\n")
            if not np.isnan(reg["stderr_intercept"]):
                lines.append(f"- erro padrão do intercepto = {reg['stderr_intercept']:.6f}\n")
            lines.append(f"- **Previsão:** se idade = 60 anos, então peso do bebê ≈ **{reg['y0']:.4f}**\n")
        else:
            lines.append("\n## 6) Regressão (nascimentos)\n")
            lines.append("⚠️ Dados insuficientes após limpeza.\n")
    else:
        lines.append("\n## 6) Regressão (nascimentos)\n")
        lines.append("⚠️ Não encontrei automaticamente idade da mãe e peso do bebê.\n")

    # salvar relatório
    md_path = out_dir / "RELATORIO_PROF_PABLO.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))
    print(f"\nRelatório salvo em: {md_path.resolve()}\n")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nascimentos", required=True, help="Arquivo de nascimentos (CSV/XLSX/TSV/JSON)")
    parser.add_argument("--peixes", required=True, help="Arquivo de peixes (CSV/XLSX/TSV/JSON)")
    args = parser.parse_args()

    raise SystemExit(run_tasks(args.nascimentos, args.peixes))


if __name__ == "__main__":
    main()
