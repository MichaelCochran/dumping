import os
from pathlib import Path

def resolve_path(base_path: Path, target: str, default: str = None):
    value = target or default
    if os.path.isabs(value):
        return value
    else:
        return str(base_path / value)