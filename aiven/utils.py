from typing import Any
from types import ModuleType


def module_to_dict(module: ModuleType) -> dict[str, Any]:
    return {key: value for key, value in vars(module).items() if key.isupper()}
