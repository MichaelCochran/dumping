from abc import abstractmethod
from dataclasses import dataclass, field, fields
from enum import Enum
import numbers
import os
import re
from types import NoneType
from typing import _SpecialForm, Any, Type, TypeVar, Union, get_args, get_origin

T = TypeVar('T', bound='DictionaryConvertible')

# Binds dictionary of key-value pairs to dataclass object and recursively replaces them with python objects
# Operates on dataclass members defined in the initializer in the order of their definition
@dataclass
class DictionaryConvertible:

    _tree_nodes: list['DictionaryConvertible'] = field(init=False, default_factory=list)

    @staticmethod
    def __resolve_type(type):
        if isinstance(type, _SpecialForm):
            return (None, ())

        if isinstance(actual_type:=get_origin(type) or type, _SpecialForm):
            if actual_type == Union:
                actual_type = None
                # Handle Optional or equivalent Union(<class>, NoneType)
                # Only Optionals with a single type supported for now (multiple types require additional metadata to know which actual type it is)
                if len(type_args:=get_args(type)) == 2:
                    if type_args[0] == NoneType and type_args[1] != NoneType:
                        return DictionaryConvertible.__resolve_type(type_args[1])
                    elif type_args[0] != NoneType and type_args[1] == NoneType:
                        return DictionaryConvertible.__resolve_type(type_args[0])

        return (actual_type, get_args(type))

    @classmethod
    def __get_transformed_value(cls: Type[T], value: Any, type: Any, root_obj: 'DictionaryConvertible') -> Any:
        actual_type, type_args = DictionaryConvertible.__resolve_type(type)
        if actual_type is not None:
            # Recursively convert DictionaryConvertible objects
            if issubclass(actual_type, DictionaryConvertible):
                if not isinstance(value, dict):
                    raise TypeError("type mismatch")
                return actual_type.convert(root_obj, **value)
            # Convert lists
            elif issubclass(actual_type, list) and len(type_args) == 1:
                # Convert compatible elements of lists
                # Only lists with a single type supported for now
                list_type, list_type_args = DictionaryConvertible.__resolve_type(type_args[0])
                if list_type is not None:
                    if not isinstance(value, list):
                        raise TypeError("type mismatch")
                    return [DictionaryConvertible.__get_transformed_value(x, list_type, root_obj) for x in value]
            # Convert dictionaries
            elif issubclass(actual_type, dict) and len(type_args) == 2:
                dict_k_type, dict_k_type_args = DictionaryConvertible.__resolve_type(type_args[0])
                dict_v_type, dict_v_type_args = DictionaryConvertible.__resolve_type(type_args[1])
                if dict_k_type is not None and dict_v_type is not None:
                    if not isinstance(value, dict):
                        raise TypeError("type mismatch")
                    return {DictionaryConvertible.__get_transformed_value(k, dict_k_type, root_obj):
                            DictionaryConvertible.__get_transformed_value(v, dict_v_type, root_obj)
                            for k, v in value.items()}
            else:
                # Resolve environment variables
                if isinstance(value, str):
                    value = re.sub('{\s*\$(\w+)\s*}', lambda m: os.environ.get(m.group(1)), value)

                # Convert numbers from other types
                if issubclass(actual_type, numbers.Number) and not issubclass(actual_type, Enum) and not isinstance(value, actual_type):
                    # Convert bools represented as a string for safety, so that "False" isn't interpreted as True
                    if issubclass(actual_type, bool) and isinstance(value, str):
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        else:
                            raise Exception(f"Could not convert '{value}' to bool")
                    else:
                        value = actual_type(value)

                # Convert enums from strings or ints
                if issubclass(actual_type, Enum) and not isinstance(value, actual_type):
                    if isinstance(value, str):
                        value = actual_type[value]
                    elif isinstance(value, int):
                        value = actual_type(value)

                if actual_type is not Any and not isinstance(value, actual_type):
                    raise Exception("type mismatch")
                else:
                    return value
                
        raise Exception(f"Unsupported field type '{type}' (consider setting type to Any)")

    @classmethod
    def convert(cls: Type[T], root_obj: 'DictionaryConvertible'=None, ref_obj: Any=None, **kwargs) -> T:
        if root_obj is not None and not isinstance(root_obj, DictionaryConvertible):
            raise Exception(f"'root_obj' ({type(root_obj)}) must be of type 'DictionaryConvertible'")

        obj = cls(**kwargs)
        if root_obj is None:
            root_obj = obj
            obj._pre_root_conversion(ref_obj)

        root_obj._tree_nodes.append(obj)

        obj._pre_conversion(root_obj)

        for f in fields(obj):
            if not f.init: # Skip the field if init is False
                continue
            try:
                value = getattr(obj, f.name)
            except AttributeError: # Skip the field if a value has not been set
                continue
            if value is None: # Skip the field if the value is None
                continue

            try:
                setattr(obj, f.name, cls.__get_transformed_value(value, f.type, root_obj))
            except Exception as e:
                raise Exception(f"Error setting attribute '{f.name}': '{value}'") from e

        obj._post_conversion(root_obj)

        if root_obj is obj:
            for node in root_obj._tree_nodes:
                node._post_root_conversion(root_obj)

        return obj

    @abstractmethod
    def _pre_root_conversion(self, ref_obj: Any):
        pass

    # The root object is provided in the following methods to allow access to data
    # that has already been processed earlier in the traversal
    # Care must be taken not to rely on any root or other data in the structure
    # that will not have been processed by the time this method is called

    # Override to process data after initialization of this object and
    # before conversion of nested objects begins
    # This method is called in pre-order traversal of the root object
    @abstractmethod
    def _pre_conversion(self, root_obj: 'DictionaryConvertible'):
        pass

    # Override to process data after conversion of this object and all nested objects completes
    # This method is called in post-order traversal of the root object
    @abstractmethod
    def _post_conversion(self, root_obj: 'DictionaryConvertible'):
        pass

    # Override to process data after conversion of the root object and all nested objects completes
    # This method is called in pre-order traversal of the root object
    @abstractmethod
    def _post_root_conversion(self, root_obj: 'DictionaryConvertible'):
        pass
