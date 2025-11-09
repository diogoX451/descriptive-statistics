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
