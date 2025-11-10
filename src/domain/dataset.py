"""
Classe DataSet - Gerencia o conjunto de dados e suas variáveis.
"""
import pandas as pd
from typing import List, Optional, Dict, Any
from .variable import Variable
from analysis.heuristics import infer_variable_type_strategy


class DataSet:
    """
    Representa um conjunto de dados.
    Gerencia uma coleção de objetos Variable.
    """

    def __init__(self, dataframe: pd.DataFrame, name: str = "Dataset"):
        """
        Inicializa um dataset.

        Args:
            dataframe: DataFrame com os dados
            name: Nome do dataset
        """
        self.name = name
        self.dataframe = dataframe
        self.variables: List[Variable] = []

        self._create_variables()

    def _create_variables(self):
        """Cria objetos Variable para cada coluna do DataFrame."""
        for column_name in self.dataframe.columns:
            series = self.dataframe[column_name]

            variable_type = infer_variable_type_strategy(series)

            variable = Variable(
                data=series,
                name=column_name,
                variable_type=variable_type
            )

            self.variables.append(variable)

    def get_variable(self, name: str) -> Optional[Variable]:
        """
        Obtém uma variável pelo nome.

        Args:
            name: Nome da variável

        Returns:
            Variable ou None se não encontrada
        """
        for variable in self.variables:
            if variable.name == name:
                return variable
        return None

    def analyze_variable(self, name: str):
        """
        Analisa e imprime os resultados de uma variável específica.

        Args:
            name: Nome da variável
        """
        variable = self.get_variable(name)
        if variable:
            variable.print_analysis()
        else:
            print(f"❌ Variável '{name}' não encontrada.")

    def analyze_all_variables(self):
        """Analisa e imprime os resultados de todas as variáveis."""
        print(f"\n{'#'*60}")
        print(f"# ANÁLISE COMPLETA DO DATASET: {self.name}")
        print(f"# Total de variáveis: {len(self.variables)}")
        print(f"# Total de registros: {len(self.dataframe)}")
        print(f"{'#'*60}\n")

        for variable in self.variables:
            variable.print_analysis()

    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo do dataset.

        Returns:
            Dicionário com resumo do dataset
        """
        return {
            'nome': self.name,
            'total_variaveis': len(self.variables),
            'total_registros': len(self.dataframe),
            'variaveis': [var.get_summary() for var in self.variables]
        }

    def print_summary(self):
        """Imprime um resumo do dataset."""
        summary = self.get_summary()

        print(f"\n{'='*60}")
        print(f"Dataset: {summary['nome']}")
        print(f"{'='*60}")
        print(f"Total de variáveis: {summary['total_variaveis']}")
        print(f"Total de registros: {summary['total_registros']}")
        print(f"\nVariáveis:")

        for var in summary['variaveis']:
            print(f"\n  • {var['nome']} ({var['tipo']})")
            print(f"    - Total de valores: {var['total_valores']}")
            print(f"    - Valores faltantes: {var['valores_faltantes']}")
            print(f"    - Valores únicos: {var['valores_unicos']}")

        print(f"\n{'='*60}\n")

    def __repr__(self):
        return f"DataSet(name='{self.name}', variables={len(self.variables)}, records={len(self.dataframe)})"
