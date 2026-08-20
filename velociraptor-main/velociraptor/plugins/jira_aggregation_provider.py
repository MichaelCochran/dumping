from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from velociraptor.interfaces.jira_interface import JiraInterface, JiraIssueRecord, JiraResults
from velociraptor.types.dictionary_convertible import DictionaryConvertible
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.i_jira_value_provider import IJiraValueProvider
from velociraptor.types.i_record_graph_collection_provider import IRecordGraphCollection, IRecordNode
from velociraptor.types.record import Record

class AggregationTypeEnum(Enum):
    SUM = 1
    COUNT = 2
    MIN = 3
    MAX = 4
    AVG = 5
    LIST = 6
    DLIST = 7

@dataclass(kw_only=True)
class AggregationConfig(DictionaryConvertible):
    field_id: str
    produced_data_id: str
    aggregation_type: AggregationTypeEnum

@dataclass(kw_only=True)
class JiraAggregationProviderConfig(DictionaryConvertible):
    aggregations: list[AggregationConfig]
    include_parents_in_totals: bool = False

@dataclass
class AggregationDefinition():
    @staticmethod
    def __get_value(field_aggregation: 'AggregationDefinition', record: Record) -> Any:
        return record.get_value(field_aggregation.field_definition)

    field_definition: Field
    produced_field_definition: Field
    aggregation_type: AggregationTypeEnum
    func: Callable[['AggregationDefinition', Record], Any] = field(default=__get_value)

class AggregatedValue:
    @staticmethod
    def create(value: Any, type: AggregationTypeEnum):
        match type:
            case AggregationTypeEnum.SUM:
                return SumValue(value)
            case AggregationTypeEnum.COUNT:
                return CountValue(value)
            case AggregationTypeEnum.MIN:
                return MinValue(value)
            case AggregationTypeEnum.MAX:
                return MaxValue(value)
            case AggregationTypeEnum.AVG:
                return AvgValue(value)
            case AggregationTypeEnum.LIST:
                return ListValue(value)
            case AggregationTypeEnum.DLIST:
                return DListValue(value)
            case _:
                raise ValueError("Unsupported type")

    def __init__(self, value: Any):
        self._value = value

    def aggregate(self, other: 'AggregatedValue'):
        raise NotImplementedError

    @abstractmethod
    def get_aggregated_value(self) -> Any:
        return self._value

class SumValue(AggregatedValue):
    def aggregate(self, other: AggregatedValue):
        values = list(filter(lambda x: x is not None, [self._value, other._value]))
        if len(values) != 0:
            self._value = sum(values)

class CountValue(AggregatedValue):
    def __init__(self, value: Any):
        super().__init__(1 if value is not None else 0)

    def aggregate(self, other: AggregatedValue):
        self._value += other._value

class MinValue(AggregatedValue):
    def aggregate(self, other: AggregatedValue):
        values = list(filter(lambda x: x is not None, [self._value, other._value]))
        if len(values) != 0:
            self._value = min(values)

class MaxValue(AggregatedValue):
    def aggregate(self, other: AggregatedValue):
        values = list(filter(lambda x: x is not None, [self._value, other._value]))
        if len(values) != 0:
            self._value = max(values)

class AvgValue(AggregatedValue):
    def __init__(self, value: Any):
        value_sum = value or 0
        super().__init__((value_sum, 1) if value is not None else (value_sum, 0))

    def aggregate(self, other: AggregatedValue):
        if other._value is not None:
            self._value = (self._value[0] + other._value[0],
                           self._value[1] + other._value[1])

    @abstractmethod
    def get_aggregated_value(self) -> Any:
        if self._value[1] == 0:
            return None
        return self._value[0] / self._value[1]

class ListValue(AggregatedValue):
    def __init__(self, value: Any):
        super().__init__([value] if value is not None else [])

    def aggregate(self, other: AggregatedValue):
        self._value = self._value + other._value

class DListValue(AggregatedValue):
    def __init__(self, value: Any):
        super().__init__({value} if value is not None else set())

    def aggregate(self, other: AggregatedValue):
        self._value = self._value.union(other._value)

    @abstractmethod
    def get_aggregated_value(self) -> Any:
        return list(self._value)

SummaryData = dict[str, AggregatedValue] # aggregated_data_id, value

class JiraAggregationProvider(IJiraValueProvider):
    NODE_COUNT_FUNC = lambda field_aggregation, record : True # Any non-None value will be included in count

    def __init__(self, plugin_config: Optional[Any], jira_interface: JiraInterface):
        if plugin_config is None:
            raise Exception("'plugin_config cannot be None")
        elif isinstance(plugin_config, JiraAggregationProviderConfig):
            config = plugin_config
        else:
            config = JiraAggregationProviderConfig.convert(**plugin_config)

        self.__aggregation_configs = config.aggregations
        self.__include_parents_in_totals = config.include_parents_in_totals

    def get_required_data_ids(self) -> list[str]:
        return [] # Nothing to specify since this plugin only references fields already fetched by Jira

    def get_produced_data_ids(self) -> list[str]:
        return [x.produced_data_id for x in self.__aggregation_configs]

    def process_results(self, results: JiraResults):
        if results.issue_graph_collection is None:
            raise Exception("JiraAggregationProvider requires a JiraIssueGraphProvider to be configured.")
        
        field_by_id_dict = { x.id : x for x in results.fields }
        aggregation_definitions : list[AggregationDefinition] = []
        for aggregation_config in self.__aggregation_configs:
            field = field_by_id_dict[aggregation_config.field_id]
            aggregated_field = Field(data_id=aggregation_config.produced_data_id, type=DataTypeEnum.ANY)
            aggregation_definitions.append(AggregationDefinition(field_definition=field,
                                                                 produced_field_definition=aggregated_field,
                                                                 aggregation_type=aggregation_config.aggregation_type))
            
            self.process_aggregations(aggregation_definitions, results.issue_records, results.issue_graph_collection, self.__include_parents_in_totals)

    @staticmethod
    def process_aggregations(aggregation_definitions: list[AggregationDefinition],
                             issue_records: list[JiraIssueRecord],
                             issue_graph_collection: IRecordGraphCollection,
                             include_parents_in_totals: bool):
        # Set default to None so that error nodes are distinguishable from nodes with zero points
        for record in issue_records:
            for aggregation in aggregation_definitions:
                record.set_custom_value(aggregation.produced_field_definition, None)

        for record_graph in issue_graph_collection.get_record_graphs():
            # Tree guarantees safety to do a recursive depth-first search to sum up story points without
            # - Cycles (infinite loop)
            # - Double-counting story points where contributed to two parents who share same parent (diamond graph)
            if not record_graph.is_tree():
                continue

            for root_node in record_graph.get_root_nodes():
                JiraAggregationProvider.__get_summary_data(root_node, aggregation_definitions, include_parents_in_totals)

    @staticmethod
    def __get_summary_data(record_node: IRecordNode, field_aggregations: list[AggregationDefinition], include_parents_in_totals: bool) -> SummaryData:
        summary_data = SummaryData({ x.produced_field_definition.data_id : AggregatedValue.create(None, x.aggregation_type) for x in field_aggregations })
        for child_node in record_node.get_child_nodes():
            child_summary_data = JiraAggregationProvider.__get_summary_data(child_node, field_aggregations, include_parents_in_totals)
            for field_aggregation in field_aggregations:
                aggregated_field_id = field_aggregation.produced_field_definition.data_id
                summary_data[aggregated_field_id].aggregate(child_summary_data[aggregated_field_id])

        record = record_node.get_record()
        if record is None:
            print(f"Warning: Issue {record_node.get_key()} is linked but was not fetched by JQL query")
            return summary_data
        elif not isinstance(record, JiraIssueRecord):
            raise Exception("Expecting JiraIssueRecord")

        for field_aggregation in field_aggregations:
            aggregated_field_id = field_aggregation.produced_field_definition.data_id
            if record_node.is_leaf_node() or include_parents_in_totals:
                summary_data[aggregated_field_id].aggregate(AggregatedValue.create(field_aggregation.func(field_aggregation, record),
                                                                                   field_aggregation.aggregation_type))

            record.set_custom_value(field_aggregation.produced_field_definition,
                                    summary_data[aggregated_field_id].get_aggregated_value())

        return summary_data