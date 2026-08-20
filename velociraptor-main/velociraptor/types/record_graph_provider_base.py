from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from velociraptor.types.field import Field
from velociraptor.types.record import Record
from velociraptor.types.i_record_graph_collection_provider import IRecordGraph, IRecordGraphCollection, IRecordGraphCollectionProvider, IRecordNode

class RecordNodeVisitStatusEnum(Enum):
    UNVISITED = 0
    VISITING_DOWN = 1
    VISITING_UP = 2
    VISITED = 3

@dataclass
class RecordNode(IRecordNode):
    key: Any
    record: Optional[Record] = None
    parent_nodes: list['RecordNode'] = field(default_factory=list)
    child_nodes: list['RecordNode'] = field(default_factory=list)
    visit_status: RecordNodeVisitStatusEnum = RecordNodeVisitStatusEnum.UNVISITED

    def get_key(self) -> Any:
        return self.key
    
    def get_record(self) -> Optional[Record]:
        return self.record
    
    def get_parent_nodes(self) -> Iterable[IRecordNode]:
        return self.parent_nodes
    
    def get_child_nodes(self) -> Iterable[IRecordNode]:
        return self.child_nodes

    def is_leaf_node(self) -> bool:
        return len(self.child_nodes) == 0

    def is_root_node(self) -> bool:
        return len(self.parent_nodes) == 0

@dataclass
class RecordGraph(IRecordGraph):
    all_nodes: list[RecordNode] = field(default_factory=list)
    root_nodes: list[RecordNode] = field(default_factory=list)
    leaf_nodes: list[RecordNode] = field(default_factory=list)
    graph_is_tree: bool = True
    graph_has_cycles: bool = False

    def get_all_nodes(self) -> Iterable[IRecordNode]:
        return self.all_nodes

    def get_root_nodes(self) -> Iterable[IRecordNode]:
        return self.root_nodes

    def get_leaf_nodes(self) -> Iterable[IRecordNode]:
        return self.leaf_nodes
    
    def is_tree(self) -> bool:
        return self.graph_is_tree

    def has_cycles(self) -> bool:
        return self.graph_has_cycles

@dataclass
class RecordGraphCollection(IRecordGraphCollection):
    record_graphs: list[RecordGraph] = field(default_factory=list)
    node_dict: dict[Any, RecordNode] = field(default_factory=dict)

    def get_node_by_key(self, key: Any) -> IRecordNode:
        return self.node_dict[key]
    
    @abstractmethod
    def get_record_graphs(self) -> Iterable[IRecordGraph]:
        return self.record_graphs

class RecordGraphProviderBase(IRecordGraphCollectionProvider):
    def create(self, key_field: Field, records: Iterable[Record]) -> IRecordGraphCollection:
        record_graph_collection = RecordGraphCollection()

        for record in records:
            key = record.get_value(key_field)
            # Get or create current node if it does not already exist
            record_node = record_graph_collection.node_dict.setdefault(key, RecordNode(key=key))
            if record_node.record is not None:
                raise Exception("Issue already fetched") # Should never happen
            record_node.record = record

            for parent_key in self._get_parent_keys(record):

                # Get or create parent node if it does not already exist
                parent_node = record_graph_collection.node_dict.setdefault(parent_key, RecordNode(key=parent_key))
                # Link parent node to current node (child)
                parent_node.child_nodes.append(record_node)
                # Link current node to parent node
                record_node.parent_nodes.append(parent_node)

        for key, record_node in record_graph_collection.node_dict.items():
            if record_node.record is None:
                print(f"Didn't fetch issue '{record_node.key}'")
            if len(record_node.parent_nodes) > 1:
                print(f"Issue '{record_node.key}' has more than one parent")
            if len(record_node.parent_nodes) == 0:
                print(f"Issue '{record_node.key}' is top level")

            if record_node.visit_status == RecordNodeVisitStatusEnum.UNVISITED:
                record_graph_collection.record_graphs.append(record_graph := RecordGraph())
                self._traverse_graph(record_graph, record_node)
            elif record_node.visit_status == RecordNodeVisitStatusEnum.VISITING_DOWN or record_node.visit_status == RecordNodeVisitStatusEnum.VISITING_UP:
                raise Exception("Shouldn't happen")

            # TODO: Consider adding support for getting child keys to improve data integrity instead of relying purely on parent keys
            # One problem may be if they aren't really issue leaves because their children weren't included in the query
            # though we can't check child links of these leaves if they are connected by epic link

        return record_graph_collection

    @abstractmethod
    def _get_parent_keys(self, record: Record) -> Iterable[Any]:
        raise NotImplementedError

    def _traverse_graph(self, record_graph: RecordGraph, record_node: RecordNode):
        record_graph.all_nodes.append(record_node)
        num_parent_nodes = len(record_node.get_parent_nodes())
        if num_parent_nodes == 0:
            record_graph.root_nodes.append(record_node)
        elif num_parent_nodes > 1:
            record_graph.graph_is_tree = False
            print(f"Found tree violation: {record_node.get_key()} has multiple parents")
        if len(record_node.get_child_nodes()) == 0:
            record_graph.leaf_nodes.append(record_node)

        self._traverse_graph_directed(record_graph, record_node, True)
        self._traverse_graph_directed(record_graph, record_node, False)

    def _traverse_graph_directed(self, record_graph: RecordGraph, record_node: RecordNode, traverse_down_graph: bool):
        visiting_status = RecordNodeVisitStatusEnum.VISITING_DOWN if traverse_down_graph else RecordNodeVisitStatusEnum.VISITING_UP
        record_node.visit_status = visiting_status
        for adjacent_node in record_node.child_nodes if traverse_down_graph else record_node.parent_nodes:
            if adjacent_node.visit_status == RecordNodeVisitStatusEnum.UNVISITED:
                self._traverse_graph(record_graph, adjacent_node)
            elif adjacent_node.visit_status == visiting_status:
                record_graph.graph_is_tree = False
                record_graph.graph_has_cycles = True
                print(f"Found cycle: {record_node.get_key()} --> {adjacent_node.get_key()}")
        record_node.visit_status = RecordNodeVisitStatusEnum.VISITED