from typing import Any
import unittest
from velociraptor.interfaces.jira_interface import JiraIssueRecord
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Record
from velociraptor.types.record_graph_provider_base import RecordGraphProviderBase

class RecordStub(JiraIssueRecord):
    key: int
    parents: list[int]

    def __init__(self, key: int, parents: list[int]) -> None:
        self.key = key
        self.parents = parents

    def get_value(self, field: Field):
        if field.data_id == 'key':
            return self.key
        else: raise Exception()

class RecordGraphProviderStub(RecordGraphProviderBase):
    def _get_parent_keys(self, record: Record) -> list[Any]:
        assert(type(record) == RecordStub)
        return record.parents

class TestRecordGraphProviderBase(unittest.TestCase):
    def setUp(self):
        # 0
        # 1 <─┐
        #     ├─ 3
        #     ├─ 4 <─┐
        #     │      └─ 9
        #     └─ 5 <─┐
        #            ├─ 10
        #            └─ 11 <─┐
        #                    └─ 18
        # 2 <─┐
        #     ├─ 6 <─┐
        #     │      └─ 12
        #     ├─ 7 <─┬──────────────────┐
        #     │      ├─ 13              │
        #     │      └─ 14              │
        #     │  ┌──────(Cycle)──────┐  │
        #     └─ 8 <─┐               │  │
        #            ├─ 15           │  │
        #            ├─ 16 <─┐       │  │
        #            │       ├─ 19 <─┘  │
        #            │       └─ 20 ─────┘
        #            └─ 17
        # 
        # 21 <─┐
        # │    └─ 22 <─┐
        # │            └─ 23 <─┐
        # └────────────────────┘
        #
        # 24 <────────────┐
        # 100 (missing) <─┤
        #                 └─ 25

        self.provider = RecordGraphProviderStub()

        self.records = [
            # Graph 1 - Single node
            RecordStub(0, []),
            
            # Graph 2 - Normal tree
            RecordStub(1, []),
            RecordStub(3, [1]), RecordStub(4, [1]), RecordStub(5, [1]),
            RecordStub(9, [4]), RecordStub(10, [5]), RecordStub(11, [5]),
            RecordStub(18, [11]),

            # Graph 3 - Graph with multiple parents and cycle
            RecordStub(2, []),
            RecordStub(6, [2]), RecordStub(7, [2]), RecordStub(8, [2, 19]),
            RecordStub(12, [6]), RecordStub(13, [7]), RecordStub(14, [7]), RecordStub(15, [8]), RecordStub(16, [8]), RecordStub(17, [8]),
            RecordStub(19, [16]), RecordStub(20, [16, 7]),

            # Graph 4 - Isolated cycle
            RecordStub(21, [23]), RecordStub(22, [21]), RecordStub(23, [22]),

            # Graph 5 - Two root nodes and missing parent
            RecordStub(24, []),
            RecordStub(25, [24, 100])
        ]

    def test_create(self):
        record_graph_collection = self.provider.create(Field(data_id = 'key', type=DataTypeEnum.NUMBER), self.records)

        # Sort graphs by lowest key
        record_graphs = sorted(record_graph_collection.get_record_graphs(), key=lambda x: sorted(x.get_all_nodes(), key=lambda y: y.get_key())[0].get_key())
        assert(len(record_graphs) == 5)

        assert(sorted([x.get_key() for x in record_graphs[0].get_all_nodes()]) == [0])
        assert(sorted([x.get_key() for x in record_graphs[0].get_leaf_nodes()]) == [0])
        assert(sorted([x.get_key() for x in record_graphs[0].get_root_nodes()]) == [0])
        assert(record_graphs[0].is_tree())
        assert(not record_graphs[0].has_cycles())

        assert(sorted([x.get_key() for x in record_graphs[1].get_all_nodes()]) == [1, 3, 4, 5, 9, 10, 11, 18])
        assert(sorted([x.get_key() for x in record_graphs[1].get_leaf_nodes()]) == [3, 9, 10, 18])
        assert(sorted([x.get_key() for x in record_graphs[1].get_root_nodes()]) == [1])
        assert(record_graphs[1].is_tree())
        assert(not record_graphs[1].has_cycles())

        assert(sorted([x.get_key() for x in record_graphs[2].get_all_nodes()]) == [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20])
        assert(sorted([x.get_key() for x in record_graphs[2].get_leaf_nodes()]) == [12, 13, 14, 15, 17, 20])
        assert(sorted([x.get_key() for x in record_graphs[2].get_root_nodes()]) == [2])
        assert(not record_graphs[2].is_tree())
        assert(record_graphs[2].has_cycles())

        assert(sorted([x.get_key() for x in record_graphs[3].get_all_nodes()]) == [21, 22, 23])
        assert(sorted([x.get_key() for x in record_graphs[3].get_leaf_nodes()]) == [])
        assert(sorted([x.get_key() for x in record_graphs[3].get_root_nodes()]) == [])
        assert(not record_graphs[3].is_tree())
        assert(record_graphs[3].has_cycles())

        assert(sorted([x.get_key() for x in record_graphs[4].get_all_nodes()]) == [24, 25, 100])
        assert(sorted([x.get_key() for x in record_graphs[4].get_leaf_nodes()]) == [25])
        assert(sorted([x.get_key() for x in record_graphs[4].get_root_nodes()]) == [24, 100])
        assert(not record_graphs[4].is_tree())
        assert(not record_graphs[4].has_cycles())

        sorted_records = sorted(self.records, key=lambda x: x.key)

        node = record_graph_collection.get_node_by_key(0)
        assert(node.get_key() == 0)
        assert(node.get_record() == sorted_records[0])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [])
        assert(node.is_leaf_node())
        assert(node.is_root_node())
        
        node = record_graph_collection.get_node_by_key(1)
        assert(node.get_key() == 1)
        assert(node.get_record() == sorted_records[1])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [3, 4, 5])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [])
        assert(not node.is_leaf_node())
        assert(node.is_root_node())
    
        node = record_graph_collection.get_node_by_key(2)
        assert(node.get_key() == 2)
        assert(node.get_record() == sorted_records[2])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [6, 7, 8])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [])
        assert(not node.is_leaf_node())
        assert(node.is_root_node())

        node = record_graph_collection.get_node_by_key(3)
        assert(node.get_key() == 3)
        assert(node.get_record() == sorted_records[3])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [1])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(4)
        assert(node.get_key() == 4)
        assert(node.get_record() == sorted_records[4])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [9])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [1])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(5)
        assert(node.get_key() == 5)
        assert(node.get_record() == sorted_records[5])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [10, 11])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [1])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(6)
        assert(node.get_key() == 6)
        assert(node.get_record() == sorted_records[6])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [12])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [2])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(7)
        assert(node.get_key() == 7)
        assert(node.get_record() == sorted_records[7])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [13, 14, 20])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [2])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(8)
        assert(node.get_key() == 8)
        assert(node.get_record() == sorted_records[8])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [15, 16, 17])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [2, 19])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(9)
        assert(node.get_key() == 9)
        assert(node.get_record() == sorted_records[9])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [4])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(10)
        assert(node.get_key() == 10)
        assert(node.get_record() == sorted_records[10])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [5])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(11)
        assert(node.get_key() == 11)
        assert(node.get_record() == sorted_records[11])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [18])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [5])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(12)
        assert(node.get_key() == 12)
        assert(node.get_record() == sorted_records[12])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [6])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(13)
        assert(node.get_key() == 13)
        assert(node.get_record() == sorted_records[13])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [7])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(14)
        assert(node.get_key() == 14)
        assert(node.get_record() == sorted_records[14])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [7])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(15)
        assert(node.get_key() == 15)
        assert(node.get_record() == sorted_records[15])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [8])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(16)
        assert(node.get_key() == 16)
        assert(node.get_record() == sorted_records[16])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [19, 20])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [8])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(17)
        assert(node.get_key() == 17)
        assert(node.get_record() == sorted_records[17])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [8])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(18)
        assert(node.get_key() == 18)
        assert(node.get_record() == sorted_records[18])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [11])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(19)
        assert(node.get_key() == 19)
        assert(node.get_record() == sorted_records[19])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [8])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [16])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(20)
        assert(node.get_key() == 20)
        assert(node.get_record() == sorted_records[20])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [7, 16])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(21)
        assert(node.get_key() == 21)
        assert(node.get_record() == sorted_records[21])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [22])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [23])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(22)
        assert(node.get_key() == 22)
        assert(node.get_record() == sorted_records[22])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [23])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [21])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(23)
        assert(node.get_key() == 23)
        assert(node.get_record() == sorted_records[23])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [21])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [22])
        assert(not node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(24)
        assert(node.get_key() == 24)
        assert(node.get_record() == sorted_records[24])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [25])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [])
        assert(not node.is_leaf_node())
        assert(node.is_root_node())

        node = record_graph_collection.get_node_by_key(25)
        assert(node.get_key() == 25)
        assert(node.get_record() == sorted_records[25])
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [24, 100])
        assert(node.is_leaf_node())
        assert(not node.is_root_node())

        node = record_graph_collection.get_node_by_key(100)
        assert(node.get_key() == 100)
        assert(node.get_record() is None)
        assert(sorted([x.get_key() for x in node.get_child_nodes()]) == [25])
        assert(sorted([x.get_key() for x in node.get_parent_nodes()]) == [])
        assert(not node.is_leaf_node())
        assert(node.is_root_node())