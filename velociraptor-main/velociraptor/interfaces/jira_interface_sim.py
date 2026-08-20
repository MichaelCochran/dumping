from pathlib import Path
from jira_cache import CachedIssues

from velociraptor.interfaces.jira_interface import JiraInterface
from velociraptor.types.data_interface_config import JiraInterfaceSimConfig
from velociraptor.types.data_interface import InsertRecordResult, UpdateRecordResult
from velociraptor.types.field import Field
from velociraptor.types.record import NewRecord, Record

class JiraInterfaceSim(JiraInterface):

    def __init__(self, config: JiraInterfaceSimConfig):
        super().__init__(config)
        self._issue_load_json_file = Path(config.data_directory_path) / config.issue_load_json_file

    def _connect(self, username, password, jira_options):
        # Do nothing
        pass

    def _fetch_jira_issues(self, fields: list[Field]):
        return CachedIssues.load(open(self._issue_load_json_file))

    def insert_record(self, record: NewRecord):
        if self._config.write_enabled is False:
            raise RuntimeError("Writing to Jira is not enabled")

        print("Inserted:")
        for fv in record:
            print("  ", fv[0].data_id, ": ", fv[1])
        return InsertRecordResult.SUCCESS

    def update_record(self, record: Record) -> UpdateRecordResult:
        if self._config.write_enabled is False:
            raise RuntimeError("Writing to Jira is not enabled")

        updated_data, original_issue = record.get_updated_values()
        if bool(updated_data):
            print("Updated:")
            for k, v in updated_data.items():
                print("  ", k, ": ", v)
        return UpdateRecordResult.SUCCESS
