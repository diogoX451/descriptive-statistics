# src/generate_data.py
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


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _load_df(input_path: str) -> pd.DataFrame:
    load_implementations()
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Arquivo '{input_path}' não encontrado.")
    ext = Path(input_path).suffix.lower().replace(".", "")
    if not ext:
        raise ValueError("Arquivo sem extensão.")
    return create_reader(ext, input_path).read()


def _pick_numeric_column(df: pd.DataFrame, preferred: str | None = None) -> str | None:
    if preferred and preferred in df.columns:
        s = pd.to_numeric(df[preferred], errors="coerce")
        if s.dropna().shape[0] >= 5:
            return preferred
    for col in df.columns:
        s2 = pd.to_numeric(df[col], errors="coerce")
        if s2.dropna().shape[0] >= 5:
            return col
    return None


def generate_univariate(
    base_values: np.ndarray,
    n: int,
    target_mean: float | None = None,
    target_std: float | None = None,
    method: str = "normal"
) -> np.ndarray:
    x = base_values.astype(float)
    x = x[~np.isnan(x)]
    if x.size < 5:
        raise ValueError("Poucos dados na coluna para gerar (mín. 5).")

    if method == "bootstrap":
        gen = np.random.choice(x, size=n, replace=True).astype(float)
        if target_mean is not None or target_std is not None:
            mu = float(np.mean(gen))
            sd = max(float(np.std(gen, ddof=0)), 1e-12)
            desired_mu = float(target_mean) if target_mean is not None else mu
            desired_sd = float(target_std) if target_std is not None else sd
            gen = (gen - mu) / sd
            gen = gen * desired_sd + desired_mu
        return gen

    base_mu = float(np.mean(x))
    base_sd = max(float(np.std(x, ddof=0)), 1e-12)
    mu = float(target_mean) if target_mean is not None else base_mu
    sd = max(float(target_std) if target_std is not None else base_sd, 1e-12)
    return np.random.normal(loc=mu, scale=sd, size=n).astype(float)


def generate_bivariate_from_sample(
    x: np.ndarray,
    y: np.ndarray,
    n: int,
    target_corr: float | None = None
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Gera (X,Y) preservando médias/desvios do sample e correlação.
    Usa normal bivariada com matriz de covariância.
    """
    x = x.astype(float); y = y.astype(float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    # aqui assumimos que já veio pareado (vamos parear antes de chamar)

    mu_x = float(np.mean(x))
    mu_y = float(np.mean(y))
    sd_x = max(float(np.std(x, ddof=0)), 1e-12)
    sd_y = max(float(np.std(y, ddof=0)), 1e-12)

    if target_corr is None:
        r = float(np.corrcoef(x, y)[0, 1])
        if np.isnan(r):
            r = 0.0
    else:
        r = float(target_corr)
        r = max(min(r, 0.999), -0.999)

    cov = np.array([
        [sd_x**2, r * sd_x * sd_y],
        [r * sd_x * sd_y, sd_y**2],
    ], dtype=float)

    mean = np.array([mu_x, mu_y], dtype=float)
    gen = np.random.multivariate_normal(mean, cov, size=n)
    gx = gen[:, 0]
    gy = gen[:, 1]

    # métricas do gerado
    pearson_r = float(np.corrcoef(gx, gy)[0, 1])
    info = {
        "mu_x": mu_x, "sd_x": sd_x,
        "mu_y": mu_y, "sd_y": sd_y,
        "corr_target": r,
        "corr_generated": pearson_r,
    }
    return gx, gy, info


def print_summary(label: str, values: np.ndarray) -> None:
    values = values.astype(float)
    values = values[~np.isnan(values)]
    if values.size == 0:
        print(f"{label}: vazio")
        return
    print(f"{label}:")
    print(f" - n = {values.size}")
    print(f" - média = {np.mean(values):.6f}")
    print(f" - dp = {np.std(values, ddof=0):.6f}")
    print(f" - min = {np.min(values):.6f}")
    print(f" - max = {np.max(values):.6f}")


def main():
    parser = argparse.ArgumentParser(description="Gerador de Dados Artificiais (Univariado/Bivariado)")
    parser.add_argument("--tipo", required=True, choices=["univariado", "bivariado"])
    parser.add_argument("--qtd", required=True, type=int, help="Quantidade de dados a gerar")
    parser.add_argument("--media", type=float, default=None, help="Média desejada (univariado, opcional)")
    parser.add_argument("--dp", type=float, default=None, help="Desvio padrão desejado (univariado, opcional)")
    parser.add_argument("--input", type=str, default=None, help="Arquivo base (csv/xlsx/tsv/json)")
    parser.add_argument("--coluna", type=str, default=None, help="Coluna base (univariado, opcional)")
    parser.add_argument("--metodo", type=str, default="normal", choices=["normal", "bootstrap"])

    # bivariado
    parser.add_argument("--corr", type=float, default=None, help="Correlação alvo (bivariado, opcional)")
    parser.add_argument("--coluna_x", type=str, default=None, help="Coluna X (bivariado) ex: peso")
    parser.add_argument("--coluna_y", type=str, default=None, help="Coluna Y (bivariado) ex: tamanho")
    parser.add_argument("--categoria_col", type=str, default=None, help="Coluna categórica para filtrar (ex: especie)")
    parser.add_argument("--categoria_valor", type=str, default=None, help="Valor da categoria (ex: Tilapia)")
    parser.add_argument("--fixar_categoria", action="store_true", help="Se marcado, adiciona a categoria fixa na saída")

    args = parser.parse_args()

    if args.qtd <= 0:
        print("Erro: --qtd deve ser > 0.")
        raise SystemExit(1)

    if not args.input:
        print("Erro: para a GUI funcionar 100%, passe --input <arquivo selecionado>.")
        print("Ex.: python src/generate_data.py --input seu.csv --tipo univariado --qtd 100")
        raise SystemExit(1)

    df = _load_df(args.input)
    dataset_stem = Path(args.input).stem.replace(".", "_")
    out_dir = Path("output") / dataset_stem / "dados_artificiais"
    _safe_mkdir(out_dir)

    if args.tipo == "univariado":
        col = _pick_numeric_column(df, preferred=args.coluna)
        if not col:
            print("Erro: não encontrei coluna numérica com dados suficientes (mín. 5).")
            raise SystemExit(1)

        base = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(float)
        gen = generate_univariate(base, args.qtd, args.media, args.dp, args.metodo)

        out_csv = out_dir / f"univariado_{col}_n{args.qtd}.csv"
        pd.DataFrame({col: gen}).to_csv(out_csv, index=False, encoding="utf-8")

        print(f"\nGERADOR UNIVARIADO — coluna: {col}")
        print_summary("Base", base)
        print_summary("Gerado", gen)
        print(f"\nArquivo gerado: {out_csv}\n")
        raise SystemExit(0)

    # =========================
    # BIVARIADO (para 20 peixes)
    # =========================
    # Filtra por espécie/categoria se fornecido
    df_work = df.copy()
    if args.categoria_col and args.categoria_valor:
        if args.categoria_col not in df_work.columns:
            print(f"Erro: categoria_col '{args.categoria_col}' não existe no dataset.")
            raise SystemExit(1)
        mask = df_work[args.categoria_col].astype(str).str.strip().str.lower() == str(args.categoria_valor).strip().lower()
        df_work = df_work[mask].copy()
        if df_work.shape[0] < 5:
            print("Erro: após filtrar a espécie/categoria, sobraram poucos dados (mín. 5).")
            raise SystemExit(1)

    # Escolhe colunas x/y
    x_col = args.coluna_x or _pick_numeric_column(df_work, preferred=None)
    if not x_col:
        print("Erro: não encontrei coluna numérica para X.")
        raise SystemExit(1)

    # Para Y, escolhe uma segunda coluna numérica diferente
    if args.coluna_y and args.coluna_y in df_work.columns:
        y_col = args.coluna_y
    else:
        y_col = None
        for c in df_work.columns:
            if c == x_col:
                continue
            s2 = pd.to_numeric(df_work[c], errors="coerce")
            if s2.dropna().shape[0] >= 5:
                y_col = c
                break
    if not y_col:
        print("Erro: não encontrei uma segunda coluna numérica para Y.")
        raise SystemExit(1)

    pair = df_work[[x_col, y_col]].copy()
    pair[x_col] = pd.to_numeric(pair[x_col], errors="coerce")
    pair[y_col] = pd.to_numeric(pair[y_col], errors="coerce")
    pair = pair.dropna()
    if len(pair) < 5:
        print("Erro: poucos pares válidos para gerar bivariado (mín. 5).")
        raise SystemExit(1)

    x = pair[x_col].to_numpy(float)
    y = pair[y_col].to_numpy(float)

    gx, gy, info = generate_bivariate_from_sample(x, y, args.qtd, target_corr=args.corr)

    out_df = pd.DataFrame({x_col: gx, y_col: gy})

    if args.fixar_categoria and args.categoria_col and args.categoria_valor:
        out_df[args.categoria_col] = args.categoria_valor

    tag = "bivariado"
    if args.categoria_col and args.categoria_valor:
        safe_val = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in args.categoria_valor)
        tag += f"_{args.categoria_col}_{safe_val}"

    out_csv = out_dir / f"{tag}_n{args.qtd}.csv"
    out_df.to_csv(out_csv, index=False, encoding="utf-8")

    print("\nGERADOR BIVARIADO")
    print(f"- X: {x_col}")
    print(f"- Y: {y_col}")
    if args.categoria_col and args.categoria_valor:
        print(f"- Filtro: {args.categoria_col} == {args.categoria_valor}")
    print(f"- n gerado: {args.qtd}")
    print(f"- Corr alvo: {info['corr_target']:.4f}")
    print(f"- Corr gerada: {info['corr_generated']:.4f}")
    print(f"\nArquivo gerado: {out_csv}\n")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
