import numpy as np
import pandas as pd

class DataGenerator:
    """Gera dados sintéticos preservando estatísticas originais."""

    @staticmethod
    def generate_univariate(data: pd.Series, n_samples: int) -> np.ndarray:
        """Cria X novos dados seguindo média e desvio padrão originais."""
        mu = data.mean()
        std = data.std()
        return np.random.normal(mu, std, n_samples)

    @staticmethod
    def generate_bivariate(df: pd.DataFrame, col1: str, col2: str, n_samples: int) -> pd.DataFrame:
        """Gera duas variáveis mantendo a correlação alvo."""
        subset = df[[col1, col2]].dropna()
        means = subset.mean()
        cov = subset.cov() # Matriz de covariância mantém a relação
        
        synthetic = np.random.multivariate_normal(means, cov, n_samples)
        return pd.DataFrame(synthetic, columns=[f"new_{col1}", f"new_{col2}"])