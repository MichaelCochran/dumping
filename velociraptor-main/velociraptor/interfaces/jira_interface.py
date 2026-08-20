'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : velociraptor.interfaces
Class     : JiraInterface.py
Engineers : Steve Schifris
Abstract  : This class provides an interface to read, write, and manupulate Jira data.
----------------------------------------------------------------------------
'''

import copy
from dataclasses import dataclass
import datetime
from pathlib import Path
import time
from typing import Any, Optional

from jira import JIRA, Issue
from jira_cache import CachedIssues
from velociraptor.types.data_interface_config import JiraInterfaceConfig
from velociraptor.types.evaluator import CalculationEvaluator
from velociraptor.types.jira_issue_graph_provider_base import JiraIssueGraphProviderBase
from velociraptor.types.i_jira_value_provider import IJiraValueProvider
from velociraptor.types.field import Field, DataTypeEnum
from velociraptor.types.record import NewRecord, Record, UpdateValueResult
from velociraptor.types.data_interface import DataInterface, InsertRecordResult, UpdateRecordResult
from velociraptor.types.i_record_graph_collection_provider import IRecordGraphCollection

class JiraIssueRecord(Record):
    JIRA_KEY_FIELD_DEFAULT = Field(data_id='key', type=DataTypeEnum.JIRA_KEY)

    @staticmethod
    def is_custom_data_id(data_id: str):
        return data_id.startswith("__")

    def __init__(self, data):
        # Issue.update() changes the original record so initialize 'data' with a copy
        # Make a deepcopy of 'data.raw' since there may be a bug in deepcopying Issue:
        # https://github.com/pycontribs/jira/issues/259
        self._data: Any = copy.deepcopy(data.raw)
        self._updated_data: dict[str, Any] = {}
        self._original_issue: Issue = data
        self._custom_data: dict[str, Any] = {}

    @staticmethod
    def __get_subfield(data_id: str, value: Any):
        for token in data_id.split('.'):
            if value is None:
                break
            elif isinstance(value, list):
                value = [x[token] for x in value]
            else:
                value = value[token]

        return value

    def __get_custom_value(self, field: Field):
        data_id = field.data_id
        try:
            value = self._custom_data
            value = self.__get_subfield(data_id, value)
        except Exception:
            raise ValueError(f"Error getting data_id '{data_id}':\ndata: {self._custom_data}")
        
        return value

    def __get_value_raw(self, field: Field):
        data_id = field.data_id
        try:
            if data_id == self.JIRA_KEY_FIELD_DEFAULT.data_id:
                value = self._data[self.JIRA_KEY_FIELD_DEFAULT.data_id] # Key is in a different part of the response; add it specially
            else:
                value = self._data['fields']
                value = self.__get_subfield(data_id, value)
        except Exception:
            raise ValueError(f"Error getting data_id '{data_id}':\ndata: {self._data}")

        if value is not None:
            try:
                if field.type == DataTypeEnum.DATE:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except Exception:
                raise ValueError(f"Error converting data_id '{data_id}':\nvalue: {value}\nfield: {field}")

        return value

    def get_value(self, field: Field):
        if self.is_custom_data_id(field.data_id):
            value = self.__get_custom_value(field)
        else:
            value = self.__get_value_raw(field)

        if value is not None:
            value = self._wrap_value(field, value)

        return value

    def set_custom_value(self, field: Field, value: Any):
        self._custom_data[field.data_id] = value

    def update_value(self, field: Field, value: Any) -> UpdateValueResult:
        # if (field.type != DataTypeEnum.DATE and
        #     field.type != DataTypeEnum.STRING):
        #     return UpdateValueResult.FAILURE # Other types not supported for update

        try:
            self._updated_data[field.data_id.split('.')[0]] = self.convert_value_for_upsert(field, value)
        except Exception as e:
            print(e) # TODO log
            return UpdateValueResult.FAILURE

        return UpdateValueResult.SUCCESS

    def get_values(self):
        return self._data

    def get_updated_values(self):
        return (self._updated_data, self._original_issue)

    @staticmethod
    def convert_value_for_upsert(field: Field, value: Any):
        # if (field.type != DataTypeEnum.DATE and
        #     field.type != DataTypeEnum.STRING):
        #     raise Exception # Other types not supported for update

        data_id = field.data_id
        new_value = value

        if JiraIssueRecord.is_custom_data_id(data_id):
            raise Exception("Updates and inserts of custom values not supported")
        if data_id == JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT.data_id:
            raise Exception("Updates and inserts of Jira keys not supported") # Updates and inserts of keys not supported
        if field.type == DataTypeEnum.DATE:
            new_value = new_value.strftime('%Y-%m-%d') # Jira cannot serialize python dates to JSON so convert to string

        # Reconstruct subfields to their original complex structures
        # It is impossible to reconstruct subfields with intermediary lists to their original structures reliably without additional information
        # so assume lists are the innermost value
        for token in reversed(data_id.split('.')[1:]):
            new_value = {token:new_value}

        return new_value

@dataclass
class JiraResults:
    fields: list[Field]
    issue_records: list[JiraIssueRecord]
    issue_graph_collection: IRecordGraphCollection

class JiraInterface(DataInterface):
    # Initializes all Jira data and store in global class variables for future reference.
    def __init__(self, config: JiraInterfaceConfig):
        self._config = config

        # Common instance variables
        self._connection = None  # Connection to be used in remote calls to Jira

        jira_options = {
            'server' : self._config.server,
            'verify' : self._config.ca_bundle
        }
        self._jira_connection = self._connect(None, self._config.token, jira_options)

        self._issue_graph_provider : Optional[JiraIssueGraphProviderBase] = None
        if (issue_graph_provider_plugin_descriptor := self._config.graph_provider_plugin_descriptor) is not None:
            issue_graph_provider_class = issue_graph_provider_plugin_descriptor.load(JiraIssueGraphProviderBase)
            self._issue_graph_provider = issue_graph_provider_class(issue_graph_provider_plugin_descriptor.config)

        self._value_providers: list[IJiraValueProvider] = []

        custom_data_id_set: set[str] = set()

        # ValueProviders will be run in the order they appear in the configuration
        # Users need to resolve dependency ordering manually where plugins produce values that other plugins require
        # TODO Build a depdency graph and automatically determine execution order
        # based on dependencies (get_required_data_ids() and get_produced_data_ids())
        for plugin_descriptor in self._config.value_provider_plugin_descriptors:
            value_provider_class = plugin_descriptor.load(IJiraValueProvider)
            value_provider = value_provider_class(plugin_descriptor.config, self)

            for data_id in value_provider.get_produced_data_ids():
                if not JiraIssueRecord.is_custom_data_id(data_id):
                    raise ValueError(f"Custom data_id '{data_id}' does not meet the naming requirements for JiraValueProvider fields.")
                if data_id in custom_data_id_set:
                    raise ValueError(f"Custom data_id '{data_id}' is not unique among all JiraValueProvider fields.")
                custom_data_id_set.add(data_id)

            self._value_providers.append(value_provider)

    def get_records(self, fields: list[Field]) -> list[Record]:
        # Build set to remove field name duplicates
        # Since field name may reference sub-elements (e.g. 'field.subfield'), fetch only the top-level element
        field_names = {x.data_id.split('.')[0] for x in fields} # Build set to remove field name duplicates

        # Add required field names to query
        if self._issue_graph_provider is not None:
            field_names.update(x.split('.')[0] for x in self._issue_graph_provider.get_required_data_ids())
        for value_provider in self._value_providers:
            field_names.update(x.split('.')[0] for x in value_provider.get_required_data_ids())

        records = [JiraIssueRecord(x) for x in self._fetch_jira_issues(list(field_names))]

        issue_graph_collection: Optional[IRecordGraphCollection] = None
        if self._issue_graph_provider is not None:
            issue_graph_collection = self._issue_graph_provider.create(JiraIssueRecord.JIRA_KEY_FIELD_DEFAULT, records)

        jira_results = JiraResults(fields=fields, issue_records=records, issue_graph_collection=issue_graph_collection)

        for value_provider in self._value_providers:
            value_provider.process_results(jira_results)

        field_by_id_dict = { x.id : x for x in fields}

        evaluator = CalculationEvaluator()
        evaluator.update_value_function(lambda id: record.get_value(field_by_id_dict[id]))
        for field in fields:
            if JiraIssueRecord.is_custom_data_id(field.data_id) and field.calculation is not None:
                for record in records:
                    value = evaluator.eval_field_calculation(field)
                    record.set_custom_value(field, value)

        if (filter_expr:=self._config.filter) is not None:
            parsed_filter_expr = evaluator.parse(filter_expr)
            filtered_records: list[JiraIssueRecord] = []
            for record in records:
                value = evaluator.eval(filter_expr, parsed_filter_expr)
                if value is False:
                    # Ignore records that do not pass the filter
                    pass
                elif value is not True:
                    raise Exception("Filter did not evaluate to a boolean")
                else:
                    filtered_records.append(record)
            return filtered_records
        else:
            return records

    def insert_record(self, record: NewRecord):
        if self._config.write_enabled is False:
            raise RuntimeError("Writing to Jira is not enabled")

        try:
            field_dict: dict[str, Any] = {}
            for fv in record:
                field_dict[fv[0].data_id.split('.')[0]] = JiraIssueRecord.convert_value_for_upsert(fv[0], fv[1])
            self._jira_connection.create_issue(fields=field_dict)
            return InsertRecordResult.SUCCESS
        except Exception as e:
            print(e) # TODO log this

        return InsertRecordResult.FAILURE

    def is_insert_supported(self) -> bool:
        return self._config.write_enabled

    def update_record(self, record: Record) -> UpdateRecordResult:
        if self._config.write_enabled is False:
            raise RuntimeError("Writing to Jira is not enabled")

        if not isinstance(record, JiraIssueRecord):
            raise Exception

        updated_data, original_issue = record.get_updated_values()
        if bool(updated_data):
            try:
                original_issue.update(fields=updated_data)
                return UpdateRecordResult.SUCCESS
            except Exception as e:
                print(e) # TODO log this

        return UpdateRecordResult.FAILURE

    def update_records(self, records: list[Record]) -> list[UpdateRecordResult]:
        result: list[UpdateRecordResult] = []
        for record in records:
            result.append(self.update_record(record))
        return result

    def is_update_supported(self) -> bool:
        return self._config.write_enabled

    def get_config(self) -> JiraInterfaceConfig:
        return self._config

    def _connect(self, username, password, jira_options):
        return JIRA(options=jira_options, token_auth=password)

    def _fetch_jira_issues(self, field_names: list[str]) -> list[Issue]:
        max_results = self._config.max_issues

        start_at_index = 0
        results_total = None
        jira_issues = []
        is_last = False

        jira_fetch_start_time = time.time()

        while not is_last:
            # For documentation, see https://jira.readthedocs.io/api.html#jira.client.JIRA.search_issues.
            results = self._jira_connection.search_issues(jql_str=self._config.jql_string, maxResults=max_results,
                                                          fields=field_names, startAt=start_at_index)
            jira_issues.extend(results.iterable)
            start_at_index += len(results)
            # If the result total changes midway or more issues are fetched than the total, exit with error
            if (results_total is not None and results_total != results.total) or start_at_index > results.total:
                raise SystemExit("Error fetching issues: total number of issues changed") # TODO throw exception
            elif start_at_index == results.total:
                is_last = True
            results_total = results.total

        print("Fetched Jira issues in " + str(time.time() - jira_fetch_start_time) + "s")

        if self._config.issue_dump_json_file is not None:
            cached = CachedIssues(jira_issues)
            cached.dump(open(Path(self._config.output_directory_path) / self._config.issue_dump_json_file, 'w'))

        return jira_issues