from typing import Any, Optional
import unittest

from velociraptor.interfaces.jira_interface import JiraIssueRecord, JiraResults
from velociraptor.plugins.jira_aggregation_provider import AggregationTypeEnum, AggregationConfig, JiraAggregationProvider, JiraAggregationProviderConfig
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Record
from velociraptor.types.record_graph_provider_base import RecordGraphProviderBase

class RecordStub(JiraIssueRecord):
    value_field = Field(id="value_id", data_id="value_data_id", type=DataTypeEnum.NUMBER)

    def __init__(self, key: int, parents: list[int], value: Optional[float]):
        self.values: dict[str, Any] =\
            {
              'key': key,
              'parents': parents,
              self.value_field.data_id: value,
            }

    def get_value(self, field: Field):
        return self.values[field.data_id]
    
    def set_custom_value(self, field: Field, value: Any):
        self.values[field.data_id] = value

class RecordTreeProviderStub(RecordGraphProviderBase):
    def _get_parent_keys(self, record: Record) -> list[Any]:
        assert(type(record) == RecordStub)
        return record.values['parents']

class TestJiraAggregationProvider(unittest.TestCase):
    sum_field = Field(data_id="__sum_value", type=DataTypeEnum.NUMBER)
    count_field = Field(data_id="__count_value", type=DataTypeEnum.NUMBER)
    min_field = Field(data_id="__min_value", type=DataTypeEnum.NUMBER)
    max_field = Field(data_id="__max_value", type=DataTypeEnum.NUMBER)
    avg_field = Field(data_id="__avg_value", type=DataTypeEnum.NUMBER)
    list_field = Field(data_id="__list_value", type=DataTypeEnum.ANY)
    dlist_field = Field(data_id="__dlist_value", type=DataTypeEnum.ANY)

    def _create_values(self,
                       records: list[RecordStub],
                       include_parents_in_totals: bool,
                       set_values_none: bool = False) -> list[RecordStub]:
        fields = [
            RecordStub.value_field,
            self.list_field,
            self.dlist_field,
            self.sum_field,
            self.count_field,
            self.min_field,
            self.max_field,
            self.avg_field
        ]

        aggregations = [
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.sum_field.data_id, aggregation_type=AggregationTypeEnum.SUM),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.count_field.data_id, aggregation_type=AggregationTypeEnum.COUNT),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.min_field.data_id, aggregation_type=AggregationTypeEnum.MIN),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.max_field.data_id, aggregation_type=AggregationTypeEnum.MAX),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.avg_field.data_id, aggregation_type=AggregationTypeEnum.AVG),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.list_field.data_id, aggregation_type=AggregationTypeEnum.LIST),
            AggregationConfig(field_id=RecordStub.value_field.id, produced_data_id=self.dlist_field.data_id, aggregation_type=AggregationTypeEnum.DLIST),
        ]

        if set_values_none:
            for record in records:
                record.values[RecordStub.value_field.data_id] = None

        results = JiraResults(fields=fields, issue_records=records, issue_graph_collection=RecordTreeProviderStub().create(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT, records))
        config = JiraAggregationProviderConfig(aggregations=aggregations, include_parents_in_totals=include_parents_in_totals)
        JiraAggregationProvider(config, None).process_results(results)
        return sorted(records, key=lambda x: x.get_value(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT))

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
            RecordStub(0, [], 0),

            # Graph 2 - Normal tree
            RecordStub(1, [], 2),
            RecordStub(3, [1], 2), RecordStub(4, [1], None), RecordStub(5, [1], 8),
            RecordStub(9, [4], 13), RecordStub(10, [5], 21), RecordStub(11, [5], 34),
            RecordStub(18, [11], 55),

            # Graph 3 - Graph with multiple parents and cycle
            RecordStub(2, [], 1),
            RecordStub(6, [2], 1), RecordStub(7, [2], 1), RecordStub(8, [2, 19], 1),
            RecordStub(12, [6], 1), RecordStub(13, [7], 1), RecordStub(14, [7], 1), RecordStub(15, [8], 1), RecordStub(16, [8], 1), RecordStub(17, [8], 1),
            RecordStub(19, [16], 1), RecordStub(20, [16, 7], 1),

            # Graph 4 - Isolated cycle
            RecordStub(21, [23], 1), RecordStub(22, [21], 1), RecordStub(23, [22], 1),

            # Graph 5 - Two root nodes and missing parent
            RecordStub(24, [], 1),
            RecordStub(25, [24, 100], 2)
        ]

    def test_leaves_only_graph(self):
        records = self._create_values(self.records, False)

        assert(records[0].get_value(TestJiraAggregationProvider.sum_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[0].get_value(TestJiraAggregationProvider.min_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.max_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.avg_field) == 0/1)
        assert(sorted(records[0].get_value(TestJiraAggregationProvider.list_field)) == [0])
        assert(sorted(records[0].get_value(TestJiraAggregationProvider.dlist_field)) == [0])

        assert(records[1].get_value(TestJiraAggregationProvider.sum_field) == 91)
        assert(records[1].get_value(TestJiraAggregationProvider.count_field) == 4)
        assert(records[1].get_value(TestJiraAggregationProvider.min_field) == 2)
        assert(records[1].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[1].get_value(TestJiraAggregationProvider.avg_field) == 91/4)
        assert(sorted(records[1].get_value(TestJiraAggregationProvider.list_field)) == [2, 13, 21, 55])
        assert(sorted(records[1].get_value(TestJiraAggregationProvider.dlist_field)) == [2, 13, 21, 55])

        assert(records[3].get_value(TestJiraAggregationProvider.sum_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[3].get_value(TestJiraAggregationProvider.min_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.max_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.avg_field) == 2/1)
        assert(sorted(records[3].get_value(TestJiraAggregationProvider.list_field)) == [2])
        assert(sorted(records[3].get_value(TestJiraAggregationProvider.dlist_field)) == [2])

        assert(records[4].get_value(TestJiraAggregationProvider.sum_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[4].get_value(TestJiraAggregationProvider.min_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.max_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.avg_field) == 13/1)
        assert(sorted(records[4].get_value(TestJiraAggregationProvider.list_field)) == [13])
        assert(sorted(records[4].get_value(TestJiraAggregationProvider.dlist_field)) == [13])

        assert(records[5].get_value(TestJiraAggregationProvider.sum_field) == 76)
        assert(records[5].get_value(TestJiraAggregationProvider.count_field) == 2)
        assert(records[5].get_value(TestJiraAggregationProvider.min_field) == 21)
        assert(records[5].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[5].get_value(TestJiraAggregationProvider.avg_field) == 76/2)
        assert(sorted(records[5].get_value(TestJiraAggregationProvider.list_field)) == [21, 55])
        assert(sorted(records[5].get_value(TestJiraAggregationProvider.dlist_field)) == [21, 55])

        assert(records[9].get_value(TestJiraAggregationProvider.sum_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[9].get_value(TestJiraAggregationProvider.min_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.max_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.avg_field) == 13/1)
        assert(sorted(records[9].get_value(TestJiraAggregationProvider.list_field)) == [13])
        assert(sorted(records[9].get_value(TestJiraAggregationProvider.dlist_field)) == [13])

        assert(records[10].get_value(TestJiraAggregationProvider.sum_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[10].get_value(TestJiraAggregationProvider.min_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.max_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.avg_field) == 21/1)
        assert(sorted(records[10].get_value(TestJiraAggregationProvider.list_field)) == [21])
        assert(sorted(records[10].get_value(TestJiraAggregationProvider.dlist_field)) == [21])

        assert(records[11].get_value(TestJiraAggregationProvider.sum_field) == 55)
        assert(records[11].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[11].get_value(TestJiraAggregationProvider.min_field) == 55)
        assert(records[11].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[11].get_value(TestJiraAggregationProvider.avg_field) == 55/1)
        assert(sorted(records[11].get_value(TestJiraAggregationProvider.list_field)) == [55])
        assert(sorted(records[11].get_value(TestJiraAggregationProvider.dlist_field)) == [55])

        assert(records[18].get_value(TestJiraAggregationProvider.sum_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[18].get_value(TestJiraAggregationProvider.min_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.avg_field) == 55/1)
        assert(sorted(records[18].get_value(TestJiraAggregationProvider.list_field)) == [55])
        assert(sorted(records[18].get_value(TestJiraAggregationProvider.dlist_field)) == [55])

        for x in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
            assert(records[x].get_value(TestJiraAggregationProvider.sum_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.count_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.min_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.max_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.avg_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.list_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.dlist_field) == None)

    def test_with_parents_graph(self):
        records = self._create_values(self.records, True)

        assert(records[0].get_value(TestJiraAggregationProvider.sum_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[0].get_value(TestJiraAggregationProvider.min_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.max_field) == 0)
        assert(records[0].get_value(TestJiraAggregationProvider.avg_field) == 0/1)
        assert(sorted(records[0].get_value(TestJiraAggregationProvider.list_field)) == [0])
        assert(sorted(records[0].get_value(TestJiraAggregationProvider.dlist_field)) == [0])

        assert(records[1].get_value(TestJiraAggregationProvider.sum_field) == 135)
        assert(records[1].get_value(TestJiraAggregationProvider.count_field) == 7)
        assert(records[1].get_value(TestJiraAggregationProvider.min_field) == 2)
        assert(records[1].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[1].get_value(TestJiraAggregationProvider.avg_field) == 135/7)
        assert(sorted(records[1].get_value(TestJiraAggregationProvider.list_field)) == [2, 2, 8, 13, 21, 34, 55])
        assert(sorted(records[1].get_value(TestJiraAggregationProvider.dlist_field)) == [2, 8, 13, 21, 34, 55])

        assert(records[3].get_value(TestJiraAggregationProvider.sum_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[3].get_value(TestJiraAggregationProvider.min_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.max_field) == 2)
        assert(records[3].get_value(TestJiraAggregationProvider.avg_field) == 2/1)
        assert(sorted(records[3].get_value(TestJiraAggregationProvider.list_field)) == [2])
        assert(sorted(records[3].get_value(TestJiraAggregationProvider.dlist_field)) == [2])

        assert(records[4].get_value(TestJiraAggregationProvider.sum_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[4].get_value(TestJiraAggregationProvider.min_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.max_field) == 13)
        assert(records[4].get_value(TestJiraAggregationProvider.avg_field) == 13/1)
        assert(sorted(records[4].get_value(TestJiraAggregationProvider.list_field)) == [13])
        assert(sorted(records[4].get_value(TestJiraAggregationProvider.dlist_field)) == [13])

        assert(records[5].get_value(TestJiraAggregationProvider.sum_field) == 118)
        assert(records[5].get_value(TestJiraAggregationProvider.count_field) == 4)
        assert(records[5].get_value(TestJiraAggregationProvider.min_field) == 8)
        assert(records[5].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[5].get_value(TestJiraAggregationProvider.avg_field) == 118/4)
        assert(sorted(records[5].get_value(TestJiraAggregationProvider.list_field)) == [8, 21, 34, 55])
        assert(sorted(records[5].get_value(TestJiraAggregationProvider.dlist_field)) == [8, 21, 34, 55])

        assert(records[9].get_value(TestJiraAggregationProvider.sum_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[9].get_value(TestJiraAggregationProvider.min_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.max_field) == 13)
        assert(records[9].get_value(TestJiraAggregationProvider.avg_field) == 13/1)
        assert(sorted(records[9].get_value(TestJiraAggregationProvider.list_field)) == [13])
        assert(sorted(records[9].get_value(TestJiraAggregationProvider.dlist_field)) == [13])

        assert(records[10].get_value(TestJiraAggregationProvider.sum_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[10].get_value(TestJiraAggregationProvider.min_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.max_field) == 21)
        assert(records[10].get_value(TestJiraAggregationProvider.avg_field) == 21/1)
        assert(sorted(records[10].get_value(TestJiraAggregationProvider.list_field)) == [21])
        assert(sorted(records[10].get_value(TestJiraAggregationProvider.dlist_field)) == [21])

        assert(records[11].get_value(TestJiraAggregationProvider.sum_field) == 89)
        assert(records[11].get_value(TestJiraAggregationProvider.count_field) == 2)
        assert(records[11].get_value(TestJiraAggregationProvider.min_field) == 34)
        assert(records[11].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[11].get_value(TestJiraAggregationProvider.avg_field) == 89/2)
        assert(sorted(records[11].get_value(TestJiraAggregationProvider.list_field)) == [34, 55])
        assert(sorted(records[11].get_value(TestJiraAggregationProvider.dlist_field)) == [34, 55])

        assert(records[18].get_value(TestJiraAggregationProvider.sum_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.count_field) == 1)
        assert(records[18].get_value(TestJiraAggregationProvider.min_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.max_field) == 55)
        assert(records[18].get_value(TestJiraAggregationProvider.avg_field) == 55/1)
        assert(sorted(records[18].get_value(TestJiraAggregationProvider.list_field)) == [55])
        assert(sorted(records[18].get_value(TestJiraAggregationProvider.dlist_field)) == [55])

        for x in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
            assert(records[x].get_value(TestJiraAggregationProvider.sum_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.count_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.min_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.max_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.avg_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.list_field) == None)
            assert(records[x].get_value(TestJiraAggregationProvider.dlist_field) == None)

    def test_none_values_with_parents_graph(self):
        records = self._create_values(self.records, True, True)
        for record in records:
            if record.get_value(record.JIRA_KEY_FIELD_DEFAULT) in [2, 6, 7, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]:
                assert(record.get_value(TestJiraAggregationProvider.sum_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.count_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.min_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.max_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.avg_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.list_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.dlist_field) == None)
            else:
                assert(record.get_value(TestJiraAggregationProvider.sum_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.count_field) == 0)
                assert(record.get_value(TestJiraAggregationProvider.min_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.max_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.avg_field) == None)
                assert(record.get_value(TestJiraAggregationProvider.list_field) == [])
                assert(record.get_value(TestJiraAggregationProvider.dlist_field) == [])
