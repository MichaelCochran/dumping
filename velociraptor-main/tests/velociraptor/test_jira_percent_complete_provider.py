from typing import Any, Optional
import unittest

from velociraptor.interfaces.jira_interface import JiraIssueRecord, JiraResults
from velociraptor.plugins.jira_percent_complete_provider import JiraPercentCompleteProvider, JiraPercentCompleteProviderConfig
from velociraptor.types.field import Field
from velociraptor.types.record import Record
from velociraptor.types.record_graph_provider_base import RecordGraphProviderBase

class RecordStub(JiraIssueRecord):
    STORY_POINTS_DATA_ID = "story_points"
    STATUS_DATA_ID = "status.statusCategory.key"

    def __init__(self, key: int, parents: list[int], story_points: Optional[float], done: bool):
        self.values: dict[str, Any] =\
            {
              'key': key,
              'parents': parents,
              self.STORY_POINTS_DATA_ID: story_points,
              self.STATUS_DATA_ID: 'done' if done else "not_done"
            }

    def get_value(self, field: Field):
        return self.values[field.data_id]

    def set_custom_value(self, field: Field, value: Any):
        self.values[field.data_id] = value

class RecordTreeProviderStub(RecordGraphProviderBase):
    def _get_parent_keys(self, record: Record) -> list[Any]:
        assert(type(record) == RecordStub)
        return record.values['parents']

class TestJiraPercentCompleteProvider(unittest.TestCase):
    def _create_values(self, records: list[JiraIssueRecord], include_parents_in_totals: bool) -> list[JiraIssueRecord]:
        results = JiraResults(fields=None, issue_records=records, issue_graph_collection=RecordTreeProviderStub().create(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT, records))
        config = JiraPercentCompleteProviderConfig(story_points_data_id=RecordStub.STORY_POINTS_DATA_ID, include_parents_in_totals=include_parents_in_totals)
        JiraPercentCompleteProvider(config, None).process_results(results)
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
        # 26
        # 27

        self.records = [
            # Graph 1 - Single node
            RecordStub(0, [], 0, True),

            # Graph 2 - Normal tree
            RecordStub(1, [], 2, False),
            RecordStub(3, [1], 3, False), RecordStub(4, [1], None, True), RecordStub(5, [1], 8, False),
            RecordStub(9, [4], 13, True), RecordStub(10, [5], 21, False), RecordStub(11, [5], 34, True),
            RecordStub(18, [11], 55, False),

            # Graph 3 - Graph with multiple parents and cycle
            RecordStub(2, [], 1, False),
            RecordStub(6, [2], 1, False), RecordStub(7, [2], 1, False), RecordStub(8, [2, 19], 1, False),
            RecordStub(12, [6], 1, False), RecordStub(13, [7], 1, False), RecordStub(14, [7], 1, False), RecordStub(15, [8], 1, False), RecordStub(16, [8], 1, False), RecordStub(17, [8], 1, False),
            RecordStub(19, [16], 1, False), RecordStub(20, [16, 7], 1, False),

            # Graph 4 - Isolated cycle
            RecordStub(21, [23], 1, False), RecordStub(22, [21], 1, False), RecordStub(23, [22], 1, False),

            # Graph 5 - Two root nodes and missing parent
            RecordStub(24, [], 1, True),
            RecordStub(25, [24, 100], 2, False),

            # Graph 6 - One node with no story points and is not done
            RecordStub(26, [], None, False),

            # Graph 7 - One node with no story points and is done
            RecordStub(27, [], None, True)
        ]

    def test_leaves_only_graph(self):
        records = self._create_values(self.records, False)

        assert(records[0].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[0].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[0].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 0)
        assert(records[0].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[0].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)

        assert(records[1].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 4)
        assert(records[1].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[1].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 92)
        assert(records[1].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 13)
        assert(records[1].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 13/92)

        assert(records[3].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[3].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[3].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 3)
        assert(records[3].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[3].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/3)

        assert(records[4].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[4].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[4].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 13)
        assert(records[4].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 13)
        assert(records[4].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 13/13)

        assert(records[5].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 2)
        assert(records[5].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[5].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 76)
        assert(records[5].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[5].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/76)

        assert(records[9].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[9].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[9].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 13)
        assert(records[9].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 13)
        assert(records[9].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 13/13)

        assert(records[10].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[10].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[10].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 21)
        assert(records[10].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[10].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/21)

        assert(records[11].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[11].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[11].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 55)
        assert(records[11].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[11].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/55)

        assert(records[18].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[18].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[18].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 55)
        assert(records[18].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[18].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/55)

        for x in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
            assert(records[x].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == None)

        assert(records[26].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[26].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[26].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == None)
        assert(records[26].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == None)
        assert(records[26].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)

        assert(records[27].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[27].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[27].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == None)
        assert(records[27].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == None)
        assert(records[27].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)

    def test_with_parents_graph(self):
        records = self._create_values(self.records, True)

        assert(records[0].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[0].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[0].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 0)
        assert(records[0].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[0].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)

        assert(records[1].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 8)
        assert(records[1].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 3)
        assert(records[1].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 136)
        assert(records[1].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 47)
        assert(records[1].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 47/136)

        assert(records[3].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[3].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[3].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 3)
        assert(records[3].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[3].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/3)

        assert(records[4].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 2)
        assert(records[4].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 2)
        assert(records[4].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 13)
        assert(records[4].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 13)
        assert(records[4].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 13/13)

        assert(records[5].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 4)
        assert(records[5].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[5].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 118)
        assert(records[5].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 34)
        assert(records[5].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 34/118)

        assert(records[9].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[9].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[9].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 13)
        assert(records[9].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 13)
        assert(records[9].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 13/13)

        assert(records[10].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[10].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[10].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 21)
        assert(records[10].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[10].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/21)

        assert(records[11].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 2)
        assert(records[11].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 1)
        assert(records[11].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 89)
        assert(records[11].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 34)
        assert(records[11].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 34/89)

        assert(records[18].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == 1)
        assert(records[18].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == 0)
        assert(records[18].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == 55)
        assert(records[18].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == 0)
        assert(records[18].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0/55)

        for x in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
            assert(records[x].get_value(JiraPercentCompleteProvider.STORY_COUNT_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_COUNT_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.STORY_POINTS_SUM_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.COMPLETED_STORY_POINTS_SUM_FIELD) == None)
            assert(records[x].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == None)

    def test_zero_points(self):
        records = [ RecordStub(0, [], 0, False),
                    RecordStub(1, [0], 0, False),
                    RecordStub(2, [0], 0, False) ]
        records = self._create_values(records, False)

        assert(records[0].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)
        assert(records[1].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)
        assert(records[2].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)

        records = [ RecordStub(0, [], 0, True),
                    RecordStub(1, [0], 0, True),
                    RecordStub(2, [0], 0, False) ]
        records = self._create_values(records, True)

        assert(records[0].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)
        assert(records[1].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)
        assert(records[2].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 0)

        records = [ RecordStub(0, [], 0, True),
                    RecordStub(1, [0], 0, True),
                    RecordStub(2, [0], 0, True) ]
        records = self._create_values(records, True)

        assert(records[0].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)
        assert(records[1].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)
        assert(records[2].get_value(JiraPercentCompleteProvider.PERCENT_COMPLETED_STORY_POINTS_FIELD) == 1)
