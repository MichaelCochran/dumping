from typing import Any
import unittest

from velociraptor.interfaces.jira_interface import JiraIssueRecord, JiraResults
from velociraptor.plugins.jira_issue_tree_depth_provider import JiraIssueTreeDepthProvider
from velociraptor.types.field import Field
from velociraptor.types.record import Record
from velociraptor.types.record_graph_provider_base import RecordGraphProviderBase

class RecordStub(JiraIssueRecord):
    def __init__(self, key: int, parents: list[int]):
        self.values: dict[str, Any] =\
            {
              'key': key,
              'parents': parents,
            }

    def get_value(self, field: Field):
        return self.values[field.data_id]
    
    def set_custom_value(self, field: Field, value: Any):
        self.values[field.data_id] = value

class RecordTreeProviderStub(RecordGraphProviderBase):
    def _get_parent_keys(self, record: Record) -> list[Any]:
        assert(type(record) == RecordStub)
        return record.values['parents']

class TestJiraIssueTreeDepthProvider(unittest.TestCase):
    def _create_values(self,
                       records: list[RecordStub]) -> list[RecordStub]:

        results = JiraResults(fields=[], issue_records=records, issue_graph_collection=RecordTreeProviderStub().create(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT, records))
        JiraIssueTreeDepthProvider(None, None).process_results(results)
        return sorted(results.issue_records, key=lambda x: x.get_value(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT))

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

    def test_graph(self):
        records = self._create_values(self.records)

        assert(records[0].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 0)

        assert(records[1].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 0)

        assert(records[3].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 1)
        assert(records[4].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 1)
        assert(records[5].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 1)

        assert(records[9].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 2)
        assert(records[10].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 2)
        assert(records[11].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 2)

        assert(records[18].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == 3)

        for x in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
            assert(records[x].get_value(JiraIssueTreeDepthProvider.TREE_DEPTH_FIELD) == None)
