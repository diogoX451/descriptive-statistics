"""
Factory para criação de leitores de dados.
"""
from typing import Dict, Type
from .idata_reader import IDataReader

# Registro de leitores disponíveis
_registry: Dict[str, Type[IDataReader]] = {}


def register(key: str):
    """
    Decorador para registrar um leitor de dados na factory.

    Args:
        key: Chave identificadora do tipo de arquivo (ex: 'csv', 'xlsx')
    """
    def decorator(cls: Type[IDataReader]):
        _registry[key] = cls
        return cls
    return decorator


def create_reader(file_type: str, file_path: str) -> IDataReader:
    """
    Cria um leitor de dados apropriado para o tipo de arquivo.

    Args:
        file_type: Tipo do arquivo (ex: 'csv', 'xlsx')
        file_path: Caminho do arquivo

    Returns:
        IDataReader: Instância do leitor apropriado

    Raises:
        ValueError: Se o tipo de arquivo não for suportado
    """
    if file_type not in _registry:
        raise ValueError(
            f"Tipo de arquivo '{file_type}' não suportado. "
            f"Tipos disponíveis: {list(_registry.keys())}"
        )

    reader_class = _registry[file_type]
    return reader_class(file_path)


def load_implementations():
    """
    Carrega dinamicamente todas as implementações de leitores.
    """
    # Import dos leitores para que sejam registrados via decorator
    from .readers import csv_reader, xlsx_reader  # noqa: F401
