from dataclasses import dataclass, field
from typing import Optional
from velociraptor.types.plugin_descriptor import PluginDescriptor

from velociraptor.types.dictionary_convertible import DictionaryConvertible


@dataclass(kw_only=True)
class SheetInterfaceConfig(DictionaryConvertible):
    input_file: str
    data_directory_path: Optional[str] = None
    query_string: Optional[str] = None
    filter: Optional[str] = None

@dataclass(kw_only=True)
class JiraInterfaceConfig(DictionaryConvertible):
    server: str
    jql_string: str
    filter: Optional[str] = None
    write_enabled: Optional[bool] = False
    ca_bundle: str = "{$REQUESTS_CA_BUNDLE}"
    token: str = "{$JIRA_TOKEN}"
    max_issues: int = 2000
    issue_dump_json_file: Optional[str] = None
    output_directory_path: Optional[str] = None
    graph_provider_plugin_descriptor: Optional[PluginDescriptor] = None
    value_provider_plugin_descriptors: list[PluginDescriptor] = field(default_factory=list)

@dataclass(kw_only=True)
class JiraInterfaceSimConfig(JiraInterfaceConfig):
    issue_load_json_file: str
    data_directory_path: Optional[str] = None
