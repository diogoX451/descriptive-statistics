import pandas as pd
from typing import Optional, Dict, Any, List


def infer_variable_type(series: pd.Series) -> str:
    """Infer a type of variable using heuristics.

    Returns one of: 'binary', 'discrete', 'continuous', 'nominal'.
    This is a lightweight heuristic used to decide which analyses to run.
    """
    s = series.dropna()
    try:
        kind = s.dtype.kind
    except Exception:
        kind = None

    nunique = s.nunique(dropna=True)

    # binary
    if nunique == 2:
        return "binary"

    # numeric integer small set -> discrete
    if kind in ("i",) and nunique <= 20:
        return "discrete"

    # numeric float or many unique ints -> continuous
    if kind in ("f",) or (kind in ("i",) and nunique > 20):
        return "continuous"

    # fallback nominal (categorical / text)
    return "nominal"


def calc_frequencies(series: pd.Series, bins: Optional[int] = None) -> pd.DataFrame:
    """Calcular frequências absoluta, relativa e acumulada para uma série.

    - Para variáveis categóricas/nominais: usa value_counts.
    - Para variáveis numéricas com muitos valores únicos: agrupa em `bins` (default 10).

    Retorna um DataFrame com colunas: 'abs', 'rel', 'cum'.
    """
    s = series.dropna()
    total = len(s)

    # decidir se precisa agrupar em bins
    if s.dtype.kind in ("f", "i") and (bins is not None or s.nunique() > 20):
        if bins is None:
            bins = 10
        binned = pd.cut(s, bins=bins)
        counts = binned.value_counts(sort=False)
    else:
        counts = s.value_counts()

    rel = counts / counts.sum()
    cum = rel.cumsum()

    df = pd.DataFrame({"abs": counts, "rel": rel, "cum": cum})
    df.index.name = "value"
    return df


def calc_central_tendency(series: pd.Series) -> Dict[str, Any]:
    """Calcular média, mediana e moda quando aplicável.

    Para séries não-numéricas, retorna apenas 'mode'.
    Mode pode ser múltipla (lista).
    """
    s = series.dropna()
    res: Dict[str, Any] = {}

    if s.empty:
        res.update({"mean": None, "median": None, "mode": []})
        return res

    if s.dtype.kind in ("i", "f"):  # numérico
        res["mean"] = float(s.mean())
        res["median"] = float(s.median())
        modes = s.mode()
        res["mode"] = modes.tolist()
    else:
        # categórico: só a moda
        modes = s.mode()
        res["mean"] = None
        res["median"] = None
        res["mode"] = modes.tolist()

    return res


# -----------------------------------------------
# 6️⃣ Separatrizes: Quartis, Decis e Percentis
# -----------------------------------------------
def calc_separatrizes(series: pd.Series) -> Dict[str, Any]:
    """Calcular quartis, decis e percentis para variáveis numéricas."""
    s = series.dropna()
    res: Dict[str, Any] = {}

    if s.empty or s.dtype.kind not in ("i", "f"):
        return {"quartis": None, "decis": None, "percentis": None}

    # Quartis
    quartis = {
        "Q1": float(s.quantile(0.25)),
        "Q2 (Mediana)": float(s.quantile(0.5)),
        "Q3": float(s.quantile(0.75)),
    }

    # Decis (dividem em 10 partes)
    decis = {f"D{i}": float(s.quantile(i / 10)) for i in range(1, 10)}

    # Percentis (dividem em 100 partes, aqui mostramos de 10 em 10 pra não ficar enorme)
    percentis = {f"P{i}": float(s.quantile(i / 100)) for i in range(10, 100, 10)}

    res["quartis"] = quartis
    res["decis"] = decis
    res["percentis"] = percentis

    return res

 # Bloco 3 - Position and Spread Analysis 
#  Dispersão: Amplitude, Variância, Desvio Padrão, Q3-Q1 e Coeficiente de Variação

def calc_dispersion(series: pd.Series) -> Dict[str, Any]:
    """Calcular medidas de dispersão para variáveis numéricas."""
    s = series.dropna()

    if s.empty or s.dtype.kind not in ("i", "f"):
        return {
            "amplitude": None,
            "variancia": None,
            "desvio_padrao": None,
            "Q3-Q1": None,
            "coef_var": None,
        }

    amplitude = float(s.max() - s.min())
    variancia = float(s.var())
    desvio_padrao = float(s.std())
    q3_q1 = float(s.quantile(0.75) - s.quantile(0.25))
    coef_var = (desvio_padrao / s.mean()) * 100 if s.mean() != 0 else None

    return {
        "amplitude": amplitude,
        "variancia": variancia,
        "desvio_padrao": desvio_padrao,
        "Q3-Q1": q3_q1,
        "coef_var": coef_var,
    }
