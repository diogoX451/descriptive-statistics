"""
Classe Variable - Representa uma variável (coluna) do dataset.
"""
import pandas as pd
from typing import Dict, Any
from .variable_types.ivariable_type import IVariableType


class Variable:
    """
    Representa uma variável (coluna) do dataset.
    Contém os dados e o tipo de variável (Strategy pattern).
    """

    def __init__(self, data: pd.Series, name: str, variable_type: IVariableType):
        """
        Inicializa uma variável.

        Args:
            data: Série de dados pandas
            name: Nome da variável
            variable_type: Tipo da variável (IVariableType)
        """
        self.data = data
        self.name = name
        self.variable_type = variable_type
        self._analysis_result = None

    def set_variable_type(self, variable_type: IVariableType):
        """
        Permite trocar o tipo da variável.

        Args:
            variable_type: Novo tipo da variável
        """
        self.variable_type = variable_type
        self._analysis_result = None

    def analyze(self, force_reanalyze: bool = False) -> Dict[str, Any]:
        """
        Executa análise estatística delegando para o tipo da variável.

        Args:
            force_reanalyze: Força uma nova análise mesmo se já existir cache

        Returns:
            Dicionário com resultados da análise
        """
        if self._analysis_result is not None and not force_reanalyze:
            return self._analysis_result

        print(f"\n{'='*60}")
        print(f"Variável: {self.name}")
        print(f"Tipo: {self.variable_type.name}")
        print(f"{'='*60}")

        self._analysis_result = self.variable_type.analyze(self.data)

        return self._analysis_result

    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo da variável.

        Returns:
            Dicionário com informações da variável
        """
        return {
            'nome': self.name,
            'tipo': self.variable_type.name,
            'total_valores': len(self.data),
            'valores_faltantes': int(self.data.isna().sum()),
            'valores_unicos': int(self.data.nunique())
        }

    def print_analysis(self):
        """Imprime a análise de forma formatada."""
        result = self.analyze()

        # Frequências
        if 'frequencias' in result:
            print("\n📊 Frequências:")
            print(result['frequencias'].to_string(index=False))

        # Moda (para variáveis categóricas)
        if 'moda' in result and 'tendencia_central' not in result:
            print(f"\n📈 Moda: {result['moda']}")

        # Proporções (para binárias)
        if 'proporcoes' in result:
            print("\n📊 Proporções:")
            for key, value in result['proporcoes'].items():
                print(f"  {key}: {value}")

        # Mediana (para ordinais)
        if 'mediana' in result and 'tendencia_central' not in result:
            print(f"\n📈 Mediana: {result['mediana']}")

        # Tendência central (para numéricas)
        if 'tendencia_central' in result:
            print("\n📈 Tendência Central:")
            for key, value in result['tendencia_central'].items():
                if value is not None:
                    print(f"  {key.capitalize()}: {value}")

        # Separatrizes
        if 'separatrizes' in result:
            print("\n📏 Separatrizes:")

            if result['separatrizes'].get('quartis'):
                print("  Quartis:")
                for key, value in result['separatrizes']['quartis'].items():
                    print(f"    {key}: {value:.2f}")

            if result['separatrizes'].get('decis'):
                print("  Decis:")
                for key, value in result['separatrizes']['decis'].items():
                    print(f"    {key}: {value:.2f}")

        # Dispersão
        if 'dispersao' in result:
            print("\n📐 Dispersão:")
            for key, value in result['dispersao'].items():
                if value is not None:
                    label = key.replace('_', ' ').capitalize()
                    print(f"  {label}: {value:.2f}")

        print(f"\n{'='*60}\n")

    def __repr__(self):
        return f"Variable(name='{self.name}', type='{self.variable_type.name}')"
