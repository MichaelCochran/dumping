from dataclasses import dataclass
from enum import IntEnum
from velociraptor.types.matched_pair import MatchedPair
from velociraptor.types.keyed_record_comparator import FieldComparison, SorEnum, KeyedRecordComparison, FieldComparisonResult
from velociraptor.types.data_interface import DataInterface, UpdateRecordResult
from velociraptor.types.record import UpdateValueResult

# Enum for the status of a compare between two sources, e.g., Jira and a spreadsheet.
# * UPDATED means the value was changed in the owning system (e.g., Jira was updated).
# * INFORMED means the value was different but not updated in the system due to the
#      system not being updatable, such as a MS Project file; or if the config/args indicated
#      no update should be done.
# * NOT_OVERWRITTEN means the value was different but not updated in the system due to an
#      existing value being present but config/args indicating no update should be done.
class FieldUpdateResult(IntEnum):
    NO_UPDATE = 0
    LEFT_UPDATED = 1
    LEFT_INFORMED = 2
    LEFT_NOT_OVERWRITTEN = 3
    LEFT_UPDATE_FAILED = 4
    RIGHT_UPDATED = 5
    RIGHT_INFORMED = 6
    RIGHT_NOT_OVERWRITTEN = 7
    RIGHT_UPDATE_FAILED = 8

@dataclass
class FieldUpdate:
    comparison: FieldComparison
    result: FieldUpdateResult

class KeyedRecordUpdateResult(IntEnum):
    NEITHER_CHANGED = 0,
    LEFT_NOT_FOUND = 1,
    RIGHT_NOT_FOUND = 2,
    LEFT_CHANGED = 3,
    RIGHT_CHANGED = 4,
    BOTH_CHANGED = 5

@dataclass
class KeyedRecordUpdate:
    matched_pair: MatchedPair
    field_updates: dict[str, FieldUpdate]
    result: KeyedRecordUpdateResult

# Updates records in a data source based on the results of comparisons with matching records in a different data source and the indicated SOR
class KeyedRecordComparisonUpdater:
    @staticmethod
    def _update_value(comparison: KeyedRecordComparison, field_comparison: FieldComparison) -> UpdateValueResult:
        from_rf = field_comparison.pair.get_record_field(comparison.matched_pair, True)
        to_rf = field_comparison.pair.get_record_field(comparison.matched_pair, False)

        return to_rf.record.update_value(to_rf.field, from_rf.record.get_value(from_rf.field))

    @staticmethod
    def update(comparisons: list[KeyedRecordComparison], left_interface: DataInterface, right_interface: DataInterface) -> list[KeyedRecordUpdate]:
        update_results: list[KeyedRecordUpdate] = []
        for comparison in comparisons:
            update = KeyedRecordUpdate(comparison.matched_pair, {}, KeyedRecordUpdateResult.NEITHER_CHANGED)

            if comparison.matched_pair.l_record.record is None:
                update.result = KeyedRecordUpdateResult.LEFT_NOT_FOUND
            elif comparison.matched_pair.r_record.record is None:
                update.result = KeyedRecordUpdateResult.RIGHT_NOT_FOUND
            else:
                for id, field_comparison in comparison.field_comparisons.items():
                    # All field comparisons (including no difference, both null, and no SOR) result in an update row
                    result = FieldUpdateResult.NO_UPDATE
                    if (field_comparison.result != FieldComparisonResult.PASS and
                        field_comparison.result != FieldComparisonResult.NEITHER):
                        if field_comparison.pair.sor == SorEnum.LEFT:
                            # Check 'overwritable' before 'updatable' since anything not 'updatable' won't be overwritten anyway
                            #
                            if (field_comparison.result != FieldComparisonResult.LEFT_ONLY and
                                (not field_comparison.pair.right_field.overwritable or
                                 not right_interface.is_update_supported())):
                                result = FieldUpdateResult.RIGHT_NOT_OVERWRITTEN
                            elif (not field_comparison.pair.right_field.updatable or
                                not right_interface.is_update_supported()):
                                result = FieldUpdateResult.RIGHT_INFORMED
                            elif KeyedRecordComparisonUpdater._update_value(comparison, field_comparison) != UpdateValueResult.SUCCESS:
                                result = FieldUpdateResult.RIGHT_UPDATE_FAILED
                            else:
                                result = FieldUpdateResult.RIGHT_UPDATED

                            if (update.result == KeyedRecordUpdateResult.NEITHER_CHANGED or
                                update.result == KeyedRecordUpdateResult.LEFT_CHANGED):
                                update.result = KeyedRecordUpdateResult.LEFT_CHANGED
                            elif (update.result == KeyedRecordUpdateResult.RIGHT_CHANGED or
                                  update.result == KeyedRecordUpdateResult.BOTH_CHANGED):
                                update.result = KeyedRecordUpdateResult.BOTH_CHANGED
                            else:
                                raise Exception

                        elif field_comparison.pair.sor == SorEnum.RIGHT:
                            if (field_comparison.result != FieldComparisonResult.RIGHT_ONLY and
                                (not field_comparison.pair.left_field.overwritable or
                                 not left_interface.is_update_supported())):
                                result = FieldUpdateResult.LEFT_NOT_OVERWRITTEN
                            elif (not field_comparison.pair.left_field.updatable or
                                  not left_interface.is_update_supported()):
                                result = FieldUpdateResult.LEFT_INFORMED
                            elif KeyedRecordComparisonUpdater._update_value(comparison, field_comparison) != UpdateValueResult.SUCCESS:
                                result = FieldUpdateResult.LEFT_UPDATE_FAILED
                            else:
                                result = FieldUpdateResult.LEFT_UPDATED

                            if (update.result == KeyedRecordUpdateResult.NEITHER_CHANGED or
                                update.result == KeyedRecordUpdateResult.RIGHT_CHANGED):
                                update.result = KeyedRecordUpdateResult.RIGHT_CHANGED
                            elif (update.result == KeyedRecordUpdateResult.LEFT_CHANGED or
                                  update.result == KeyedRecordUpdateResult.BOTH_CHANGED):
                                update.result = KeyedRecordUpdateResult.BOTH_CHANGED
                            else:
                                raise Exception

                        else:
                            pass # NO_SOR

                    update.field_updates[id] = FieldUpdate(field_comparison, result)

                # Update the full record; if the update fails, indicate that each field update failed as well
                if update.matched_pair.l_record.record is not None:
                    if (left_interface.is_update_supported() and
                        left_interface.update_record(comparison.matched_pair.l_record.record) != UpdateRecordResult.SUCCESS):
                        for id, field_update in update.field_updates.items():
                            if field_update.result == FieldUpdateResult.LEFT_UPDATED:
                                field_update.result = FieldUpdateResult.LEFT_UPDATE_FAILED

                if update.matched_pair.r_record.record is not None:
                    if (right_interface.is_update_supported() and
                        right_interface.update_record(comparison.matched_pair.r_record.record) != UpdateRecordResult.SUCCESS):
                        for id, field_update in update.field_updates.items():
                            if field_update.result == FieldUpdateResult.RIGHT_UPDATED:
                                field_update.result = FieldUpdateResult.RIGHT_UPDATE_FAILED

            update_results.append(update)

        return update_results
