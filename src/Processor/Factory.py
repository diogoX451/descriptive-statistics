import pkgutil
import importlib
import inspect
import os
from Processor.AData import AData
from typing import Dict, Type

_registry: Dict[str, Type[AData]] = {}

def load_implementations():
    implementations_dir = os.path.join(os.path.dirname(__file__), "Implementations")
    for filename in os.listdir(implementations_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"Processor.Implementations.{filename[:-3]}"
            importlib.import_module(module_name)

def register(key: str):
    def decorator(cls: Type[AData]):
        _registry[key] = cls
        return cls
    return decorator

def discover_implementations(package="Processor.Implementations"):
    pkg = importlib.import_module(package)
    prefix = pkg.__name__ + "."
    for _, name, _ in pkgutil.iter_modules(pkg.__path__, prefix):
        module = importlib.import_module(name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, AData) and obj is not AData:
                key = getattr(obj, "TYPE", None) or obj.__name__.lower()
                _registry[key] = obj

def create_data(kind: str, *args, **kwargs) -> AData:
    if not _registry:
        discover_implementations()
    cls = _registry.get(kind.lower())
    if cls is None:
        raise ValueError(f"Nenhuma implementação encontrada para '{kind}'")
    return cls(*args, **kwargs)