from dataclasses import dataclass
from enum import IntEnum

from jira import JIRA
import pandas as pd
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.matched_pair import MatchType, MatchedPair
from velociraptor.types.keyed_record_comparator import FieldComparisonPair, KeyedRecordComparison
from velociraptor.types.data_interface import DataInterface, InsertRecordResult
from velociraptor.types.record import NewRecord

class KeyedRecordInsertResult(IntEnum):
    BOTH_EXIST = 0,
    LEFT_INSERT_INFORMED = 1,
    LEFT_INSERTED = 2,
    LEFT_INSERT_FAILED = 3,
    RIGHT_INSERT_INFORMED = 4,
    RIGHT_INSERTED = 5,
    RIGHT_INSERT_FAILED = 6

@dataclass
class KeyedRecordInsert:
    matched_pair: MatchedPair
    insert_fields: list[Field]
    result: KeyedRecordInsertResult

# Insert new records in a data source based on the absence of joined records in a different data source
class KeyedRecordJoinedPairInserter:
    @staticmethod
    def insert(pairs: list[MatchedPair], field_pairs: list[FieldComparisonPair], left_interface: DataInterface, right_interface: DataInterface) -> list[KeyedRecordInsert]:

        INSERT_ENABLED = False

        if not INSERT_ENABLED:
            return []

        insert_results: list[KeyedRecordInsert] = []
        pairs.sort(key=lambda x: ((rec:=x.r_record.record) is None, rec.get_value(Field('', '', 'key', DataTypeEnum.JIRA_KEY, False, False, False)) if rec is not None else None))
        for pair in pairs:
            insert = KeyedRecordInsert(pair, [], KeyedRecordInsertResult.BOTH_EXIST)

############ THIS SECTION INSERTS NEW JIRA RECORDS ################

#             # TODO change keyed_record_comparison_updater to use this pattern instead of checking for Record is None
#             if pair.l_record.record is None:
# #            if pair.r_result == MatchType.UNMATCHED: # Why doesn't this work???
#                 if not left_interface.is_insert_supported(): # should config flag drive this?
#                     insert.result = KeyedRecordInsertResult.LEFT_INSERT_INFORMED # TODO add configuration safety flag
#                 # Add other cases

#             elif pair.r_record.record is None:
#             # elif pair.l_result == MatchType.UNMATCHED: # Why doesn't this work?? # Left side unmatched means record should be inserted on right
#                 if not right_interface.is_insert_supported():
#                     insert.result = KeyedRecordInsertResult.RIGHT_INSERT_INFORMED # TODO add configuration safety flag
#                 else:
#                     issue_type = 'Capability'
#                     # if pair.l_record.record._data["Level"] == 0:
#                     #     continue
#                     # elif pair.l_record.record._data["Level"] == 1:
#                     #     issue_type = 'Capability'
#                     # elif pair.l_record.record._data["Level"] == 2:
#                     #     issue_type = 'Feature'
#                     # elif pair.l_record.record._data["Level"] == 3:
#                     #     issue_type = 'Story'
#                     # else:
#                     #     continue

#                     new_record: NewRecord = []
#                     for field_pair in field_pairs:
#                         if field_pair.right_field.insertable:
#                             new_record.append((field_pair.right_field, pair.l_record.record.get_value(field_pair.left_field)))
#                         else:
#                             print("Skipping field '" + field_pair.right_field.name + "': not insertable")
#                     # TODO Hardcoded
#                     new_record.append((Field('', '', 'project', '', False, False, True), {'key': 'AES'}))
#                     new_record.append((Field('', '', 'issuetype', '', False, False, True), {'name': issue_type}))
#                     # if pair.l_record.record._data["Level"] == 3:
#                     #     sp = pair.l_record.record._data["1LMX Plan SP"]
#                     #     if pd.isnull(sp): sp = None
#                     #     new_record.append((Field('', '', 'customfield_10106', '', False, False), sp))

#                     if right_interface.insert_record(new_record) == InsertRecordResult.SUCCESS:
#                         insert.result = KeyedRecordInsertResult.RIGHT_INSERTED
#                     else:
#                         insert.result = KeyedRecordInsertResult.RIGHT_INSERT_FAILED

############ THIS SECTION LINKS JIRA RECORDS ASSUMING THEY'RE IN TREE ORDER (CAPABILITY WITH ALL FEATURES UNDER WITH ALL STORIES UNDER) AND MUST BE ON A SEPARATE RUN AFTER ISSUES CREATED ################

            # if pair.r_record.record is None:
            #     continue

            # issue_type = pair.r_record.record.get_value(Field('','','issuetype', DataTypeEnum.STRING, False, False))
            # if issue_type == 'Capability':
            #     one = pair.r_record.record._data["key"]
            # elif issue_type == 'Feature':
            #     two = pair.r_record.record._data["key"]
            #     right_interface._jira_connection.create_issue_link('Parent-Child', one, pair.r_record.record._data["key"])
            # elif issue_type == 'Story':
            #     right_interface._jira_connection.create_issue_link('Parent-Child', two, pair.r_record.record._data["key"])



            insert_results.append(insert)
        return insert_results
