# src/detect_fake.py
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from scipy import stats

# Ajuste de path para imports do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_loading.factory import create_reader, load_implementations  # noqa: E402


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _is_numeric_series(s: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(s):
        return True
    s2 = pd.to_numeric(s, errors="coerce")
    return s2.notna().sum() >= 5


def _to_numeric(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    return pd.to_numeric(s, errors="coerce").astype(float)


def analyze_numeric(series: pd.Series) -> Dict[str, Any]:
    x = _to_numeric(series).dropna().to_numpy(dtype=float)
    if x.size < 5:
        return {"erro": "Poucos dados"}

    mu = float(np.mean(x))
    sd = float(np.std(x, ddof=0))
    sd = max(sd, 1e-12)

    # Repetição / unicidade
    unique_ratio = float(len(np.unique(x)) / len(x))

    # Valores muito “redondos” (muito .0 / .00 / .5)
    frac = np.abs(x - np.round(x))
    frac00 = float(np.mean(frac < 1e-9))  # quase inteiro
    frac05 = float(np.mean(np.abs(frac - 0.5) < 1e-9))  # quase x.5

    # Espaçamento artificial (muitos passos iguais)
    xs = np.sort(x)
    diffs = np.diff(xs)
    diffs = diffs[np.isfinite(diffs)]
    step_mode_ratio = 0.0
    if diffs.size >= 10:
        # arredonda para evitar ruído minúsculo
        diffs_r = np.round(diffs, 6)
        vals, counts = np.unique(diffs_r, return_counts=True)
        step_mode_ratio = float(np.max(counts) / diffs_r.size)

    # Skew e Kurtose (excesso)
    skew = float(stats.skew(x, bias=False))
    kurt_excess = float(stats.kurtosis(x, fisher=True, bias=False))

    # Outliers via IQR
    q1 = float(np.quantile(x, 0.25))
    q3 = float(np.quantile(x, 0.75))
    iqr = max(q3 - q1, 1e-12)
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_ratio = float(np.mean((x < lower) | (x > upper)))

    # CV
    cv = float((sd / mu) * 100) if mu != 0 else float("inf")

    return {
        "n": int(x.size),
        "mean": mu,
        "std": sd,
        "cv_percent": cv,
        "unique_ratio": unique_ratio,
        "frac_integer": frac00,
        "frac_half": frac05,
        "step_mode_ratio": step_mode_ratio,
        "skewness": skew,
        "kurtosis_excess": kurt_excess,
        "outlier_ratio": outlier_ratio,
    }


def analyze_categorical(series: pd.Series) -> Dict[str, Any]:
    s = series.dropna()
    if s.size < 5:
        return {"erro": "Poucos dados"}
    # concentração (dominância de uma categoria)
    vc = s.value_counts(normalize=True, dropna=True)
    top1 = float(vc.iloc[0]) if not vc.empty else 0.0
    unique_ratio = float(s.nunique() / len(s))
    return {
        "n": int(len(s)),
        "top1_ratio": top1,
        "unique_ratio": unique_ratio,
        "num_unique": int(s.nunique()),
    }


def score_rules_numeric(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Regras simples, interpretáveis e fáceis de justificar no relatório.
    Retorna lista de achados (cada um com score, motivo, métrica).
    """
    findings = []
    if "erro" in m:
        return findings

    n = m["n"]

    # 1) Muitos valores repetidos (baixa unicidade)
    if n >= 30 and m["unique_ratio"] < 0.25:
        findings.append({
            "regra": "Baixa unicidade",
            "score": 2,
            "detalhe": f"unique_ratio={m['unique_ratio']:.3f} (< 0.25) indica muitos valores repetidos",
            "metrica": "unique_ratio"
        })

    # 2) Dados muito “redondos”
    if n >= 30 and (m["frac_integer"] > 0.85 or m["frac_half"] > 0.50):
        findings.append({
            "regra": "Valores redondos demais",
            "score": 2,
            "detalhe": f"frac_integer={m['frac_integer']:.3f}, frac_half={m['frac_half']:.3f} sugerem geração artificial/arrendondamento excessivo",
            "metrica": "frac_integer/frac_half"
        })

    # 3) Passo constante (muitos incrementos iguais)
    if n >= 30 and m["step_mode_ratio"] > 0.60:
        findings.append({
            "regra": "Espaçamento artificial",
            "score": 2,
            "detalhe": f"step_mode_ratio={m['step_mode_ratio']:.3f} (> 0.60) muitos diffs iguais após ordenar",
            "metrica": "step_mode_ratio"
        })

    # 4) Ausência de outliers em conjunto grande
    # (não é prova, mas um sinal)
    if n >= 80 and m["outlier_ratio"] == 0.0:
        findings.append({
            "regra": "Ausência total de outliers",
            "score": 1,
            "detalhe": "outlier_ratio=0.000 com n>=80 pode indicar dados sintéticos 'limpos demais'",
            "metrica": "outlier_ratio"
        })

    # 5) Skew e kurtose “perfeitinhos demais” repetidos
    # Aqui só marca se está MUITO perto de 0/0 (normal idealizada)
    if n >= 80 and abs(m["skewness"]) < 0.05 and abs(m["kurtosis_excess"]) < 0.10:
        findings.append({
            "regra": "Distribuição perfeita demais",
            "score": 1,
            "detalhe": f"skew={m['skewness']:.3f}, kurt_excess={m['kurtosis_excess']:.3f} muito próximos de 0",
            "metrica": "skewness/kurtosis_excess"
        })

    # 6) CV extremamente baixo em dados grandes (homogêneo demais)
    if n >= 80 and m["cv_percent"] != float("inf") and m["cv_percent"] < 1.0:
        findings.append({
            "regra": "Variabilidade baixa demais",
            "score": 1,
            "detalhe": f"CV={m['cv_percent']:.3f}% (< 1%) em n>=80 pode indicar dados gerados com pouco ruído",
            "metrica": "cv_percent"
        })

    return findings


def score_rules_categorical(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    if "erro" in m:
        return findings

    n = m["n"]

    # 1) Dominância extrema de uma categoria
    if n >= 30 and m["top1_ratio"] > 0.95:
        findings.append({
            "regra": "Dominância extrema",
            "score": 1,
            "detalhe": f"top1_ratio={m['top1_ratio']:.3f} (>0.95) uma categoria domina quase tudo",
            "metrica": "top1_ratio"
        })

    # 2) Unicidade muito baixa (muita repetição)
    if n >= 30 and m["unique_ratio"] < 0.10 and m["num_unique"] <= 3:
        findings.append({
            "regra": "Poucas categorias / repetição alta",
            "score": 1,
            "detalhe": f"unique_ratio={m['unique_ratio']:.3f} com num_unique={m['num_unique']} pode indicar geração artificial simples",
            "metrica": "unique_ratio"
        })

    return findings


def load_dataframe(file_path: str) -> pd.DataFrame:
    load_implementations()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")

    ext = Path(file_path).suffix.lower().replace(".", "")
    if not ext:
        raise ValueError("Arquivo sem extensão.")

    reader = create_reader(ext, file_path)
    return reader.read()


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/detect_fake.py <arquivo.csv/xlsx/tsv/json>")
        raise SystemExit(1)

    file_path = sys.argv[1]

    try:
        df = load_dataframe(file_path)
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        raise SystemExit(1)

    dataset_stem = Path(file_path).stem.replace(".", "_")
    out_dir = Path("output") / dataset_stem / "detector"
    _safe_mkdir(out_dir)

    print("\n" + "=" * 70)
    print("DETECTOR SIMPLES DE DADOS ARTIFICIAIS")
    print("=" * 70)
    print(f"Arquivo: {file_path}")
    print(f"Saída:   {out_dir.resolve()}\n")

    all_findings = []
    metrics_rows = []

    for col in df.columns:
        s = df[col]

        # numérico?
        if _is_numeric_series(s):
            m = analyze_numeric(s)
            metrics_rows.append({"variavel": col, "tipo": "numerica", **m} if "erro" not in m else {"variavel": col, "tipo": "numerica", "erro": m["erro"]})

            findings = score_rules_numeric(m)
            for f in findings:
                all_findings.append({
                    "variavel": col,
                    "tipo": "numerica",
                    "regra": f["regra"],
                    "score": f["score"],
                    "detalhe": f["detalhe"],
                    "metrica": f["metrica"]
                })
        else:
            m = analyze_categorical(s.astype(str) if not pd.api.types.is_string_dtype(s) else s)
            metrics_rows.append({"variavel": col, "tipo": "categorica", **m} if "erro" not in m else {"variavel": col, "tipo": "categorica", "erro": m["erro"]})

            findings = score_rules_categorical(m)
            for f in findings:
                all_findings.append({
                    "variavel": col,
                    "tipo": "categorica",
                    "regra": f["regra"],
                    "score": f["score"],
                    "detalhe": f["detalhe"],
                    "metrica": f["metrica"]
                })

    # Salva métricas completas
    metrics_csv = out_dir / "metricas_detector.csv"
    pd.DataFrame(metrics_rows).to_csv(metrics_csv, index=False, encoding="utf-8")

    # Salva achados
    findings_df = pd.DataFrame(all_findings).sort_values(["score", "variavel"], ascending=[False, True]) if all_findings else pd.DataFrame(columns=["variavel", "tipo", "regra", "score", "detalhe", "metrica"])
    findings_csv = out_dir / "sinais_suspeitos.csv"
    findings_df.to_csv(findings_csv, index=False, encoding="utf-8")

    # Score por variável
    score_by_var = findings_df.groupby("variavel")["score"].sum().sort_values(ascending=False) if not findings_df.empty else pd.Series(dtype=float)

    # Output no terminal (pra aparecer na GUI)
    if findings_df.empty:
        print("✅ Nenhum sinal forte de artificialidade foi encontrado pelas regras simples.\n")
    else:
        print("⚠️ Sinais suspeitos encontrados (regras simples):\n")
        top_vars = score_by_var.head(10)
        for var, sc in top_vars.items():
            print(f"- {var}: score={int(sc)}")

        print("\nDetalhes (top 15 achados):\n")
        for _, row in findings_df.head(15).iterrows():
            print(f"* {row['variavel']} [{row['tipo']}] | {row['regra']} (score={row['score']}): {row['detalhe']}")

    # Relatório MD
    md_path = out_dir / "RELATORIO_DETECTOR.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Relatório — Detector Simples de Dados Artificiais\n\n")
        f.write(f"**Arquivo analisado:** {file_path}\n\n")
        f.write("## Como funciona (regras simples)\n\n")
        f.write("O detector **não prova** que os dados são artificiais; ele aponta **sinais** comuns em dados gerados ou muito manipulados.\n\n")
        f.write("### Regras para colunas numéricas\n")
        f.write("- **Baixa unicidade**: muitos valores repetidos.\n")
        f.write("- **Valores redondos demais**: muitos inteiros ou valores terminando em .5.\n")
        f.write("- **Espaçamento artificial**: muitos incrementos iguais após ordenar.\n")
        f.write("- **Ausência total de outliers** (IQR) em amostras grandes: dados “limpos demais”.\n")
        f.write("- **Distribuição perfeita demais**: skew e curtose muito próximos de 0 em amostras grandes.\n")
        f.write("- **Variabilidade baixa demais**: CV muito baixo em amostras grandes.\n\n")
        f.write("### Regras para colunas categóricas\n")
        f.write("- **Dominância extrema**: uma categoria aparece quase sempre.\n")
        f.write("- **Poucas categorias + repetição alta**: distribuição artificial simples.\n\n")

        f.write("## Resultado\n\n")
        if findings_df.empty:
            f.write("✅ Nenhum sinal forte de artificialidade foi encontrado pelas regras simples.\n\n")
        else:
            f.write("### Score por variável (maior = mais suspeito)\n\n")
            f.write("| Variável | Score |\n|---|---:|\n")
            for var, sc in score_by_var.items():
                f.write(f"| {var} | {int(sc)} |\n")
            f.write("\n")

            f.write("### Sinais encontrados\n\n")
            f.write("| Variável | Tipo | Regra | Score | Detalhe |\n|---|---|---|---:|---|\n")
            for _, row in findings_df.iterrows():
                detalhe = str(row["detalhe"]).replace("|", "\\|")
                f.write(f"| {row['variavel']} | {row['tipo']} | {row['regra']} | {int(row['score'])} | {detalhe} |\n")

        f.write("\n## Arquivos gerados\n\n")
        f.write(f"- `metricas_detector.csv` (métricas por coluna)\n")
        f.write(f"- `sinais_suspeitos.csv` (sinais encontrados)\n")
        f.write(f"- `RELATORIO_DETECTOR.md` (este relatório)\n")

    print("\nArquivos gerados:")
    print(f"- {metrics_csv}")
    print(f"- {findings_csv}")
    print(f"- {md_path}")
    print("\nConcluído.\n")


if __name__ == "__main__":
    main()
