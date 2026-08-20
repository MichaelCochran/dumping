from dataclasses import dataclass
from enum import IntEnum
from velociraptor.types.record import Record
from velociraptor.types.field import Field
from velociraptor.types.matched_pair import MatchedPair

# Enum for the Systems of Record (SORs) supported by velociraptor for field comparison.
# The SoR determines which field to use as the "master" when comparing and copying values.
class SorEnum(IntEnum):
    NO_SOR = 0
    LEFT = 1
    RIGHT = 2

class FieldComparisonResult(IntEnum):
    PASS = 0
    FAIL = 1
    LEFT_ONLY = 2
    RIGHT_ONLY = 3
    NEITHER = 4

@dataclass
class FieldComparisonPair:  # FieldPair?  Refactor out?
    id: str
    left_field: Field
    right_field: Field
    sor: SorEnum

    def get_record_field(self, matched_pair: MatchedPair, is_sor: bool):
        side = self.sor
        if side != SorEnum.LEFT and side != SorEnum.RIGHT:
            raise Exception

        if not is_sor:
            side = SorEnum.LEFT if side == SorEnum.RIGHT else SorEnum.RIGHT

        if side == SorEnum.LEFT:
            record = matched_pair.l_record.record
            field = self.left_field
        elif side == SorEnum.RIGHT:
            record = matched_pair.r_record.record
            field = self.right_field
        else:
            raise Exception

        return RecordField(record, field)

@dataclass
class FieldComparison: # FieldComparisonResult?
    pair: FieldComparisonPair
    result: FieldComparisonResult

@dataclass
class KeyedRecordComparison:
    matched_pair: MatchedPair
    field_comparisons: dict[str, FieldComparison]

@dataclass
class RecordField:
    record: Record
    field: Field

class KeyedRecordComparator:
    @staticmethod
    def compare(matched_pairs: list[MatchedPair], field_pairs: list[FieldComparisonPair]) -> list[KeyedRecordComparison]:
        comparison_results: list[KeyedRecordComparison] = []
        for mp in matched_pairs:
            comparison_result = KeyedRecordComparison(mp, {})
            if mp.l_record.record is not None and mp.r_record.record is not None: # If one of the sides is None, no point in doing a comparison
                for field_pair in field_pairs:
                    l_value = mp.l_record.record.get_value(field_pair.left_field)
                    r_value = mp.r_record.record.get_value(field_pair.right_field)

                    if l_value is None and r_value is None:
                        result = FieldComparisonResult.NEITHER
                    elif r_value is None:
                        result = FieldComparisonResult.LEFT_ONLY
                    elif l_value is None:
                        result = FieldComparisonResult.RIGHT_ONLY
                    elif l_value == r_value:
                        result = FieldComparisonResult.PASS
                    else:
                        result = FieldComparisonResult.FAIL

                    comparison_result.field_comparisons[field_pair.id] = FieldComparison(field_pair, result)

            comparison_results.append(comparison_result)

        return comparison_results
