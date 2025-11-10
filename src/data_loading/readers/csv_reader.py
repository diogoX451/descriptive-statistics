"""
Leitor de arquivos CSV.
"""
import pandas as pd
from ..idata_reader import IDataReader
from ..factory import register


@register("csv")
class CSVReader(IDataReader):
    """Leitor de arquivos CSV."""

    def __init__(self, file_path: str):
        """
        Inicializa o leitor CSV.

        Args:
            file_path: Caminho do arquivo CSV
        """
        self.file_path = file_path

    def read(self) -> pd.DataFrame:
        """
        Lê o arquivo CSV e retorna um DataFrame.
        Converte automaticamente vírgulas em pontos para números decimais.

        Returns:
            pd.DataFrame: Dados do CSV

        Raises:
            FileNotFoundError: Se o arquivo não existir
            pd.errors.ParserError: Se houver erro ao parsear o CSV
        """
        try:
            # Tenta diferentes delimitadores comuns
            for delimiter in [';', ',', '\t', '|']:
                try:
                    df = pd.read_csv(self.file_path, delimiter=delimiter)
                    # Verifica se foi parseado corretamente (mais de uma coluna)
                    if len(df.columns) > 1:
                        # Converte colunas com vírgulas decimais para float
                        df = self._convert_comma_to_decimal(df)
                        return df
                except:
                    continue

            # Se nenhum delimitador funcionou, usa o padrão do pandas
            df = pd.read_csv(self.file_path)
            df = self._convert_comma_to_decimal(df)
            return df

        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        except Exception as e:
            raise pd.errors.ParserError(f"Erro ao ler CSV: {str(e)}")

    def _convert_comma_to_decimal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte colunas com números no formato brasileiro (vírgula decimal)
        para o formato padrão (ponto decimal).

        Args:
            df: DataFrame original

        Returns:
            DataFrame com números convertidos
        """
        for col in df.columns:
            # Verifica se a coluna é object (texto)
            if df[col].dtype == 'object':
                try:
                    # Tenta converter substituindo vírgula por ponto
                    # Remove aspas se existirem
                    converted = df[col].astype(str).str.replace(',', '.', regex=False)
                    # Tenta converter para float
                    converted_float = pd.to_numeric(converted, errors='coerce')

                    # Se pelo menos 50% foi convertido com sucesso, assume que é numérico
                    valid_count = converted_float.notna().sum()
                    total_count = len(converted_float)

                    if valid_count / total_count >= 0.5:
                        df[col] = converted_float
                except:
                    # Se der erro, mantém a coluna original
                    pass

        return df
