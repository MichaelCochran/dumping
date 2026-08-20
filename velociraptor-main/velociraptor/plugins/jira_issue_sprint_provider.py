from datetime import date, datetime
from dateutil import tz
from dataclasses import dataclass
from typing import Any, Optional
from velociraptor.interfaces.jira_interface import JiraInterface, JiraResults
from velociraptor.types.dictionary_convertible import DictionaryConvertible
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.i_jira_value_provider import IJiraValueProvider
import re

@dataclass(kw_only=True)
class JiraIssueSprintProviderConfig(DictionaryConvertible):
    sprint_data_id: str

class JiraIssueSprintProvider(IJiraValueProvider):
    SPRINTS_FIELD = Field(data_id="__sprints", type=DataTypeEnum.DATE)

    def __init__(self, plugin_config: Optional[Any], jira_interface: JiraInterface):
        if plugin_config is None:
            raise Exception("'plugin_config cannot be None")
        elif isinstance(plugin_config, JiraIssueSprintProviderConfig):
            config = plugin_config
        else:
            config = JiraIssueSprintProviderConfig.convert(**plugin_config)

        self._sprint_data_field = Field(data_id=config.sprint_data_id, type=DataTypeEnum.ANY)
 
    def get_required_data_ids(self) -> list[str]:
        return [self._sprint_data_field.data_id]

    def get_produced_data_ids(self) -> list[str]:
        return [self.SPRINTS_FIELD.data_id]

    @staticmethod
    def _parse_date(data: str, key: str) -> Optional[date]:
        result = re.search(key + r"=([^,]*)", data).group(1)
        if result == "<null>":
            return None
        else:
            return datetime.fromisoformat(result).astimezone(tz.tzutc()).date()

    def process_results(self, results: JiraResults):
        for record in results.issue_records:
            record.set_custom_value(self.SPRINTS_FIELD, None)

            if (sprint_data_list:=record.get_value(self._sprint_data_field)) is not None:
                sprint_list = [
                    {
                        "start_date": self._parse_date(x, 'startDate'),
                        "end_date": self._parse_date(x, 'endDate'),
                        "activated_date": self._parse_date(x, 'activatedDate'),
                        "complete_date": self._parse_date(x, 'completeDate')
                    } for x in sprint_data_list]

                record.set_custom_value(self.SPRINTS_FIELD, sprint_list)
