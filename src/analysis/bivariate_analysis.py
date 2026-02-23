import pandas as pd
from scipy.stats import pearsonr, spearmanr
import numpy as np

class BivariateAnalysis:
    @staticmethod
    def calcular_relacoes(df, col_x, col_y):
        x, y = df[col_x].dropna(), df[col_y].dropna()
        
        # Correlação (Pearson)
        corr, _ = pearsonr(x, y)
        
        # Regressão Linear Simples: y = ax + b
        a, b = np.polyfit(x, y, 1)
        
        return {
            "correlacao_pearson": corr,
            "coeficiente_angular": a,
            "intercepto": b,
            "equacao": f"y = {a:.2f}x + {b:.2f}"
        }