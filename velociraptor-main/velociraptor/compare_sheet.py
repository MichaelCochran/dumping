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

from typing import Optional
from velociraptor.types.calculated_record import CalculatedRecord
from velociraptor.types.config_manager import ConfigManager
from velociraptor.types.keyed_record_comparator import KeyedRecordComparator
from velociraptor.types.matched_pair import MatchSide
from velociraptor.types.keyed_record_comparison_updater import KeyedRecordComparisonUpdater
from velociraptor.interfaces.data_interface_collection import DataInterfaceCollection
from velociraptor.matched_pair_builder import build_matched_pairs
from velociraptor.output_report import OutputReport
from velociraptor.velociraptor import main

def compare_data(config_mgr: ConfigManager):
    data_interfaces = DataInterfaceCollection(config_mgr)

    print("Comparing and generating outputs...")

    matched_pairs = build_matched_pairs(config_mgr, data_interfaces)
    field_pairs = config_mgr.get_field_pair_list()
    comparisons = KeyedRecordComparator.compare(matched_pairs, field_pairs)

    left_data_interface = data_interfaces.get_interface_by_id(config_mgr.get_left_source_config().data_interface_id)
    right_data_interface = data_interfaces.get_interface_by_id(config_mgr.get_right_source_config().data_interface_id)
    updates = KeyedRecordComparisonUpdater.update(comparisons, left_data_interface, right_data_interface)

    comparison_config = config_mgr.get_comparison_config()

    sort_field = config_mgr.get_field_by_id(comparison_config.sort_field_id)
    if sort_field.source_id == config_mgr.get_left_source_config().id:
        source_side = MatchSide.LEFT
    elif sort_field.source_id == config_mgr.get_right_source_config().id:
        source_side = MatchSide.RIGHT
    else:
        raise Exception

    # Sort the original updates object in-place
    updates.sort(key=lambda x: ((rec:=x.matched_pair.get_record(source_side)) is None, (val:=rec.get_value(sort_field) if rec is not None else None) is None, val), reverse=comparison_config.reverse)

    field_by_id_dict = config_mgr.get_field_by_id_dict()
    left_source_id = config_mgr.get_left_source_config().id
    right_source_id = config_mgr.get_right_source_config().id
    calculated_records = list[Optional[CalculatedRecord]]()
    for update in updates:
        if (l_record:=update.matched_pair.l_record.record) is None or (r_record:=update.matched_pair.r_record.record) is None:
            calculated_records.append(None)
        else:
            calculated_records.append(CalculatedRecord(field_by_id_dict, {left_source_id: l_record, right_source_id: r_record}))

    display_fields = config_mgr.get_display_field_list()
    output_report = OutputReport(config_mgr)
    output_report.generate_report(updates, calculated_records, display_fields, config_mgr.get_left_source_config().name, config_mgr.get_right_source_config().name)

    # TODO print out updates
    # print("************ LEFT UPDATES ***************\n", leftUpdateList)
    # print("\n************ RIGHT UPDATES ***************\n", rightUpdateList)

if __name__ == "__main__":
    print("Compare Sheet processing...")
    description = "compare_sheet is a Velociraptor utility that compares an input spreadsheet to the issues in \
                   a Jira project in order to determine differences and possibly take actions. Config data and command line \
                   arguments determine what fields are compared and which side (spreadsheet or Jira) is considered System \
                   of Record (SoR) which then determines updates to the non-SoR side."
    config_mgr = main(description)
    compare_data(config_mgr)
    print("Completed Compare Data processing.")
