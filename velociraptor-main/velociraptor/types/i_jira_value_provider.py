from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional
from velociraptor.types.i_jira_provider import IJiraProvider

class IJiraValueProvider(IJiraProvider):

    @abstractmethod
    def __init__(self, plugin_config: Optional[Any], jira_interface: JiraInterface):
        raise NotImplementedError

    @abstractmethod
    def process_results(self, results: JiraResults):
        raise NotImplementedError
    
    @abstractmethod
    def get_produced_data_ids(self) -> list[str]:
        raise NotImplementedError
