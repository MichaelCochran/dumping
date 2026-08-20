
import datetime
from typing import Any
import unittest

from velociraptor.interfaces.jira_interface import JiraIssueRecord, JiraResults
from velociraptor.plugins.jira_issue_sprint_provider import JiraIssueSprintProvider, JiraIssueSprintProviderConfig
from velociraptor.types.field import DataTypeEnum, Field

class RecordStub(JiraIssueRecord):
    SPRINTS_DATA_FIELD = Field(data_id="SprintField", type=DataTypeEnum.ANY)

    def __init__(self):
        pass

    def get_value(self, field: Field):
        if field.data_id == self.SPRINTS_DATA_FIELD.data_id:
            return [
                "com.atlassian.greenhopper.service.sprint.Sprint@232c8855[id=60618,rapidViewId=13199,state=CLOSED,name=PROC 23Q3-S7,startDate=2023-09-06T11:48:00.000-04:00,endDate=2023-09-20T11:48:00.000-04:00,completeDate=2023-09-20T11:07:27.651-04:00,activatedDate=2023-09-06T11:49:01.845-04:00,sequence=60618,goal=Goal1,autoStartStop=false,synced=false]",
                "com.atlassian.greenhopper.service.sprint.Sprint@6c6c1c41[id=61205,rapidViewId=13199,state=CLOSED,name=PROC 23Q3-S8,startDate=2023-09-20T11:32:00.000-04:00,endDate=2023-10-04T11:32:00.000-04:00,completeDate=2023-10-04T11:43:54.401-04:00,activatedDate=2023-09-20T11:33:13.016-04:00,sequence=61205,goal=Goal2,autoStartStop=false,synced=false]",
                "com.atlassian.greenhopper.service.sprint.Sprint@2ae151b0[id=62234,rapidViewId=13199,state=ACTIVE,name=PROC 23Q3-S9,startDate=2023-10-04T11:47:00.000-04:00,endDate=2023-10-18T11:47:00.000-04:00,completeDate=<null>,activatedDate=2023-10-04T11:47:50.625-04:00,sequence=62234,goal=,autoStartStop=false,synced=false]"
            ]
        else:
            raise ValueError("Unsupported field")

    def set_custom_value(self, field: Field, value: Any):
        if field.data_id == JiraIssueSprintProvider.SPRINTS_FIELD.data_id:
            self.sprints = value
        else:
            raise ValueError("Unsupported field")

class TestJiraIssueSprintProvider(unittest.TestCase):

    def setUp(self):
        config = JiraIssueSprintProviderConfig(sprint_data_id=RecordStub.SPRINTS_DATA_FIELD.data_id)
        self.provider = JiraIssueSprintProvider(config, None)

    def test_get_required_data_ids(self):
        assert(self.provider.get_required_data_ids() == [RecordStub.SPRINTS_DATA_FIELD.data_id])

    def test_get_produced_field_ids(self):
        assert(self.provider.get_produced_data_ids() == [JiraIssueSprintProvider.SPRINTS_FIELD.data_id])

    def test_process_results(self):
        record = RecordStub()
        self.provider.process_results(JiraResults(fields=RecordStub.SPRINTS_DATA_FIELD, issue_records=[record], issue_graph_collection=None))
        assert record.sprints[0] == { "start_date" : datetime.date(2023, 9, 6),
                                      "end_date" : datetime.date(2023, 9, 20),
                                      "activated_date" : datetime.date(2023, 9, 6),
                                      "complete_date" : datetime.date(2023, 9, 20) }
        assert record.sprints[1] == { "start_date" : datetime.date(2023, 9, 20),
                                      "end_date" : datetime.date(2023, 10, 4),
                                      "activated_date" : datetime.date(2023, 9, 20),
                                      "complete_date" : datetime.date(2023, 10, 4) }
        assert record.sprints[2] == { "start_date" : datetime.date(2023, 10, 4),
                                      "end_date" : datetime.date(2023, 10, 18),
                                      "activated_date" : datetime.date(2023, 10, 4),
                                      "complete_date" : None }
