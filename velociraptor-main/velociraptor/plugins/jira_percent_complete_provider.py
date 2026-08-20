from dataclasses import dataclass
from typing import Any, Optional
from velociraptor.interfaces.jira_interface import JiraInterface, JiraResults
from velociraptor.plugins.jira_aggregation_provider import AggregationTypeEnum, AggregationDefinition, AggregationConfig, JiraAggregationProvider, JiraAggregationProviderConfig
from velociraptor.types.dictionary_convertible import DictionaryConvertible
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.i_jira_value_provider import IJiraValueProvider
from velociraptor.types.record import Record

@dataclass(kw_only=True)
class JiraPercentCompleteProviderConfig(DictionaryConvertible):
    story_points_data_id: str
    include_parents_in_totals: bool = False

class JiraPercentCompleteProvider(IJiraValueProvider):
    STORY_COUNT_FIELD = Field(data_id="__story_count", type=DataTypeEnum.NUMBER)
    COMPLETED_STORY_COUNT_FIELD = Field(data_id="__completed_story_count", type=DataTypeEnum.NUMBER)
    STORY_POINTS_SUM_FIELD = Field(data_id="__story_points_sum", type=DataTypeEnum.NUMBER)
    COMPLETED_STORY_POINTS_SUM_FIELD = Field(data_id="__completed_story_points_sum", type=DataTypeEnum.NUMBER)
    PERCENT_COMPLETED_STORY_POINTS_FIELD = Field(data_id="__percent_completed_story_points", type=DataTypeEnum.PERCENT)

    PRODUCED_FIELDS_LIST = [
        STORY_COUNT_FIELD,
        COMPLETED_STORY_COUNT_FIELD,
        STORY_POINTS_SUM_FIELD,
        COMPLETED_STORY_POINTS_SUM_FIELD,
        PERCENT_COMPLETED_STORY_POINTS_FIELD
    ]

    def __init__(self, plugin_config: Optional[Any], jira_interface: JiraInterface):
        if plugin_config is None:
            raise Exception("'plugin_config cannot be None")
        elif isinstance(plugin_config, JiraPercentCompleteProviderConfig):
            self.config = plugin_config
        else:
            self.config = JiraPercentCompleteProviderConfig.convert(**plugin_config)

        self.__status_category_key = Field(data_id="status.statusCategory.key", type=DataTypeEnum.STRING)
        self.__story_points_field = Field(data_id=self.config.story_points_data_id, type=DataTypeEnum.NUMBER)
        self.__include_parents_in_totals = self.config.include_parents_in_totals

    def get_required_data_ids(self) -> list[str]:
        return [self.__status_category_key.data_id,
                self.__story_points_field.data_id]

    def get_produced_data_ids(self) -> list[Field]:
        return [x.data_id for x in self.PRODUCED_FIELDS_LIST]

    def _get_is_complete(self, record: Record) -> bool:
        return record.get_value(self.__status_category_key) == 'done'

    def _get_percent_complete(self, record: Record) -> float:
        # Consider a story whose state is in the "done" status category to be 100% complete, otherwise 0%
        return 1 if self._get_is_complete(record) else 0

    def _calculate_completed_story_count(self, field_aggregation: AggregationDefinition, record: Record) -> Any:
        return 1 if self._get_is_complete(record) else None

    def _calculate_completed_story_points(self, field_aggregation: AggregationDefinition, record: Record) -> Any:
        if (story_points:=record.get_value(self.__story_points_field)) is None:
            return None
        return story_points * self._get_percent_complete(record)

    def process_results(self, results: JiraResults):
        if results.issue_graph_collection is None:
            raise Exception("JiraPercentCompleteProvider requires a JiraIssueGraphProvider to be configured.")

        aggregations : list[AggregationDefinition] = [
            AggregationDefinition(field_definition=None,
                                  produced_field_definition=self.STORY_COUNT_FIELD,
                                  aggregation_type=AggregationTypeEnum.COUNT,
                                  func=JiraAggregationProvider.NODE_COUNT_FUNC),
            AggregationDefinition(field_definition=self.__story_points_field,
                                  produced_field_definition=self.COMPLETED_STORY_COUNT_FIELD,
                                  aggregation_type=AggregationTypeEnum.COUNT,
                                  func=self._calculate_completed_story_count),
            AggregationDefinition(field_definition=self.__story_points_field,
                                  produced_field_definition=self.STORY_POINTS_SUM_FIELD,
                                  aggregation_type=AggregationTypeEnum.SUM),
            AggregationDefinition(field_definition=self.__story_points_field,
                                  produced_field_definition=self.COMPLETED_STORY_POINTS_SUM_FIELD,
                                  aggregation_type=AggregationTypeEnum.SUM,
                                  func=self._calculate_completed_story_points)
        ]

        JiraAggregationProvider.process_aggregations(aggregations, results.issue_records, results.issue_graph_collection, self.__include_parents_in_totals)

        for record in results.issue_records:
            story_count = record.get_value(self.STORY_COUNT_FIELD)
            story_points = record.get_value(self.STORY_POINTS_SUM_FIELD)
            completed_story_count = record.get_value(self.COMPLETED_STORY_COUNT_FIELD)
            completed_story_points = record.get_value(self.COMPLETED_STORY_POINTS_SUM_FIELD)

            # Assign percent completed based on percent of story points completed
            if completed_story_points is not None and story_points != 0 and story_points is not None:
                percent_completed_story_points = (completed_story_points / story_points)
            # If there are no story points, assign 100% if all stories are completed, otherwise assign 0%
            elif completed_story_count is not None and story_count is not None:
                percent_completed_story_points = 1 if (completed_story_count == story_count) else 0
            # Otherwise assign no value
            else:
                percent_completed_story_points = None
            record.set_custom_value(self.PERCENT_COMPLETED_STORY_POINTS_FIELD, percent_completed_story_points)
