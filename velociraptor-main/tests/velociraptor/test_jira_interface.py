
from datetime import date
import unittest

from velociraptor.interfaces.jira_interface import JiraIssueRecord
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Date, JiraKey

class IssueStub:
    def __init__(self, raw):
        self.raw = raw

class TestJiraIssueRecord(unittest.TestCase):
    def test_key(self):
        record = JiraIssueRecord(IssueStub({"key": "TEST-123"}))
        assert(record.get_value(Field(data_id="key", type=DataTypeEnum.JIRA_KEY)) == JiraKey("TEST-123"))

    def test_missing_key(self):
        record = JiraIssueRecord(IssueStub({}))
        with self.assertRaises(ValueError):
            record.get_value(Field(data_id="key", type=DataTypeEnum.JIRA_KEY))

    def test_date(self):
        record = JiraIssueRecord(IssueStub({"fields": {"good_date": "2023-12-31"}}))
        assert(record.get_value(Field(data_id="good_date", type=DataTypeEnum.DATE)) == Date(date(2023, 12, 31)))

    def test_bad_date(self):
        record = JiraIssueRecord(IssueStub({"fields": {"bad_date": "junk"}}))
        with self.assertRaises(ValueError):
            assert(record.get_value(Field(data_id="bad_date", type=DataTypeEnum.DATE)))

    def test_missing_field_id(self):
        record = JiraIssueRecord(IssueStub({"fields": {"good_date": "2023-12-31"}}))
        with self.assertRaises(ValueError):
            assert(record.get_value(Field(data_id="missing_date", type=DataTypeEnum.DATE)))

    def test_missing_fields(self):
        record = JiraIssueRecord(IssueStub({}))
        with self.assertRaises(ValueError):
            record.get_value(Field(data_id="field", type=DataTypeEnum.STRING))

    def test_missing_plugin_field_id(self):
        record = JiraIssueRecord(IssueStub({}))
        plugin_field_id = "__test"
        assert(JiraIssueRecord.is_custom_data_id(plugin_field_id))
        with self.assertRaises(ValueError):
            record.get_value(Field(data_id=plugin_field_id, type=DataTypeEnum.STRING))