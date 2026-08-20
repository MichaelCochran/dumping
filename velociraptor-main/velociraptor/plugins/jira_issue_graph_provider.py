from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional
from velociraptor.types.dictionary_convertible import DictionaryConvertible
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.jira_issue_graph_provider_base import JiraIssueGraphProviderBase
from velociraptor.types.record import JiraKey, Record

@dataclass(kw_only=True)
class IssueLink(DictionaryConvertible):
    link_id: str
    is_parent_inward: bool

@dataclass(kw_only=True)
class JiraIssueGraphProviderConfig(DictionaryConvertible):
    child_parent_issue_links: Optional[list[IssueLink]] = field(default_factory=list)
    parent_link_epic_data_id: Optional[str] = None

    issue_link_by_link_id_dict: dict[str, IssueLink] = field(init=False, default_factory=dict)

    def _post_conversion(self, root_obj):
        if len(self.child_parent_issue_links) == 0 and self.parent_link_epic_data_id is None:
            raise Exception(f"Either 'child_parent_issue_links' must not be empty or 'parent_link_epic_data_id' must be set")
        for issue_link in self.child_parent_issue_links:
            if self.issue_link_by_link_id_dict.get(issue_link.link_id) is not None:
                raise Exception(f"Duplicate IssueLink '{issue_link.link_id}'")
            self.issue_link_by_link_id_dict[issue_link.link_id] = issue_link

class JiraIssueGraphProvider(JiraIssueGraphProviderBase):
    def __init__(self, plugin_config: Optional[Any]):
        if plugin_config is None:
            raise Exception("'JiraIssueRecordGraphProvider config is required")
        config = JiraIssueGraphProviderConfig.convert(**plugin_config)

        self._issue_link_by_link_id_dict = config.issue_link_by_link_id_dict
        self._issue_links_field = Field(data_id="issuelinks", type=DataTypeEnum.ANY)
        self._parent_link_epic_field = \
            None if config.parent_link_epic_data_id is None \
            else Field(data_id=config.parent_link_epic_data_id, type=DataTypeEnum.STRING)

    def get_required_data_ids(self) -> list[str]:
        data_ids: list[str] = []
        if len(self._issue_link_by_link_id_dict.items()) > 0:
            data_ids.append(self._issue_links_field.data_id)
        if self._parent_link_epic_field is not None:
            data_ids.append(self._parent_link_epic_field.data_id)
        return data_ids

    def _get_parent_keys(self, record: Record) -> Iterable[Any]:
        # Currently will return multiple of the same key (multiple parents) if linked by different link types
        parent_keys: list[JiraKey] = []
        if len(self._issue_link_by_link_id_dict.items()) > 0:
            for link_field_value in record.get_value(self._issue_links_field):
                issue_link = self._issue_link_by_link_id_dict.get(link_field_value.get('type', {}).get('id'))
                if issue_link is not None:
                    link_direction = "inwardIssue" if issue_link.is_parent_inward else "outwardIssue"
                    if (parent_key := link_field_value.get(link_direction, {}).get('key')) is not None:
                        parent_keys.append(JiraKey(parent_key))
        if self._parent_link_epic_field is not None:
            if (epic_parent_key := record.get_value(self._parent_link_epic_field)) is not None:
                parent_keys.append(JiraKey(epic_parent_key))
        return parent_keys