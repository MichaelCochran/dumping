'''
----------------------------------------------------------------------------
Library   : None
Package   : None
Class     : None
Engineers : Steve Schifris, Ted Paulakis
Abstract  : This main invokes capabilities for comparing and manipilating Jira issue fields.
            Comparisons and updates can be with other Jira fields
            or with an input spreadsheet that has rows and columns corresponding to Jira issues and
            fields, respectively.
----------------------------------------------------------------------------
'''

from velociraptor.types.config_manager import ConfigManager
from velociraptor.types.keyed_record_joined_pair_inserter import KeyedRecordJoinedPairInserter
from velociraptor.interfaces.data_interface_collection import DataInterfaceCollection
from velociraptor.matched_pair_builder import build_matched_pairs
from velociraptor.velociraptor import main

def insert_data(config_mgr: ConfigManager):

    data_interfaces = DataInterfaceCollection(config_mgr)

    print("Comparing and generating outputs...")

    matched_pairs = build_matched_pairs(config_mgr, data_interfaces)

    field_pairs = config_mgr.get_field_pair_list()
    left_data_interface = data_interfaces.get_interface_by_id(config_mgr.get_left_source_config().data_interface_id)
    right_data_interface = data_interfaces.get_interface_by_id(config_mgr.get_right_source_config().data_interface_id)
    inserts = KeyedRecordJoinedPairInserter.insert(matched_pairs, field_pairs, left_data_interface, right_data_interface)
    for insert in inserts:
        print(insert.matched_pair.l_record.pk, ": ", str(insert.result))

if __name__ == "__main__":
    print("Insert Sheet processing...")
    description = "input_sheet is a Velociraptor utility" # TODO
    config_mgr = main(description)
    insert_data(config_mgr)
    print("Completed Insert Data processing.")
