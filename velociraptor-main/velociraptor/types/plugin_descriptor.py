from dataclasses import dataclass
import sys
from typing import Any, Optional, Type, TypeVar

from velociraptor.types.dictionary_convertible import DictionaryConvertible

T = TypeVar('T')

@dataclass(kw_only=True)
class PluginDescriptor(DictionaryConvertible):
    module_name: str
    class_name: str
    config: Optional[Any] = None

    def load(self, cls: Type[T]):
        __import__(self.module_name)
        module = sys.modules[self.module_name]
        plugin_class: Type[T] = getattr(module, self.class_name)
        if not issubclass(plugin_class, cls):
            raise Exception(f"Plugin '{plugin_class.__name__}' must be of type '{cls.__name__}'")
        
        return plugin_class