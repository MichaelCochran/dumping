from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Optional
from velociraptor.types.field import Field
from velociraptor.types.record import Record

class IRecordNode:

    @abstractmethod
    def get_key(self) -> Any:
        raise NotImplementedError
    
    @abstractmethod
    def get_record(self) -> Optional[Record]:
        raise NotImplementedError
    
    @abstractmethod
    def get_parent_nodes(self) -> Iterable['IRecordNode']:
        raise NotImplementedError
    
    @abstractmethod
    def get_child_nodes(self) -> Iterable['IRecordNode']:
        raise NotImplementedError
    
    @abstractmethod
    def is_root_node(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_leaf_node(self) -> bool:
        raise NotImplementedError

class IRecordGraph:

    @abstractmethod
    def get_all_nodes(self) -> Iterable[IRecordNode]:
        raise NotImplementedError
    
    @abstractmethod
    def get_root_nodes(self) -> Iterable[IRecordNode]:
        raise NotImplementedError

    @abstractmethod
    def get_leaf_nodes(self) -> Iterable[IRecordNode]:
        raise NotImplementedError
    
    @abstractmethod
    def is_tree(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_cycles(self) -> bool:
        raise NotImplementedError

class IRecordGraphCollection:

    @abstractmethod
    def get_node_by_key(self, key: Any) -> IRecordNode:
        raise NotImplementedError
    
    @abstractmethod
    def get_record_graphs(self) -> Iterable[IRecordGraph]:
        raise NotImplementedError

class IRecordGraphCollectionProvider:

    @abstractmethod
    def create(self, key_field: Field, records: Iterable[Record]) -> IRecordGraphCollection:
        raise NotImplementedError