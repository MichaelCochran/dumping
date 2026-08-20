import time
import logging
from velociraptor.types.matched_pair import MatchedPair, MatchType
from velociraptor.types.keyed_record import KeyedRecord, NullKeyedRecord

logging.getLogger(__name__)

class KeyedRecordJoiner:

# this is a left join but may need to be an outer join if not matching the other direction
    @staticmethod
    def _join_one_way(left_list: list[KeyedRecord], right_list: list[KeyedRecord]) -> list[MatchedPair]:
        matched_pair_list: list[MatchedPair] = []
        left_pk_dict: dict[str, list[KeyedRecord]] = {}
        left_fk_dict: dict[str, list[KeyedRecord]] = {}
        right_pk_dict: dict[str, list[KeyedRecord]] = {}

        for record in left_list:
#            if record.pk is not None:   # TODO adding this back doesn't hurt the unit test (though fk can't be filtered)
            left_pk_dict.setdefault(record.pk, []).append(record)
            left_fk_dict.setdefault(record.fk, []).append(record)

        for record in right_list:
#            if record.pk is not None:
            right_pk_dict.setdefault(record.pk, []).append(record)

        for fk, v in left_fk_dict.items():
            if fk is not None and (match_list:=right_pk_dict.get(fk)):
                match_type = MatchType.ONE_TO_ONE if len(match_list) == 1 else MatchType.ONE_TO_MANY
            else:
                match_list = [NullKeyedRecord]
                match_type = MatchType.UNMATCHED

            # Set the right side with PK duplicate for cases when it is a left-only match and not set in the other direction
            right_is_pk_duplicate = len(match_list) > 1

            for record in v:
                left_is_pk_duplicate = len(left_pk_dict.get(record.pk, [])) > 1 if record.pk is not None else False

                for match in match_list:
                    mp = MatchedPair(record, match)
                    mp.l_result.match_type = match_type
                    mp.l_result.is_pk_duplicate = left_is_pk_duplicate
                    mp.r_result.is_pk_duplicate = right_is_pk_duplicate
                    matched_pair_list.append(mp)

            if match_list != [NullKeyedRecord]:
                del right_pk_dict[fk]

        return matched_pair_list

    @staticmethod
    def join(left_list: list[KeyedRecord], right_list: list[KeyedRecord]) -> list[MatchedPair]:

        start = time.time()

        first_list = KeyedRecordJoiner._join_one_way(left_list, right_list)

        # print("First list")
        # print(*firstList, sep="\n")

        second_list = KeyedRecordJoiner._join_one_way(right_list, left_list)

        # print("second list")
        # print(*secondList, sep="\n")

        second_dict: dict[(int, int), MatchedPair] = {}
        for mp in second_list:
            mp.l_record, mp.r_record = mp.r_record, mp.l_record # Swap the records for consistency
            mp.l_result, mp.r_result = mp.r_result, mp.l_result

            key = id(mp.l_record), id(mp.r_record)
            if key in second_dict:
                print("Something bad happened")
            else:
                second_dict[key] = mp

        results: list[MatchedPair] = []

        first_list_no_match: list[MatchedPair] = []
        for mp1 in first_list:
            key = id(mp1.l_record), id(mp1.r_record)
            key_null = id(NullKeyedRecord), id(mp1.r_record)

            if key[0] == id(NullKeyedRecord):
                print("Weird1")
            if (mp2:=second_dict.get(key)) is not None:
                if mp2.l_result.match_type != MatchType.UNMATCHED:
                    print("ERROR!1")
                mp2.l_result = mp1.l_result
                results.append(mp2)
                del second_dict[key]
            elif (mp2:=second_dict.get(key_null)) is not None:
                if mp2.r_result.match_type != MatchType.UNMATCHED or mp2.l_record is not NullKeyedRecord or mp2.l_result.match_type != MatchType.UNMATCHED:
                    print("ERROR!2")
                mp2.l_record = mp1.l_record
                mp2.l_result = mp1.l_result
                results.append(mp2)
                del second_dict[key_null]
            else:
                first_list_no_match.append(mp1)

        second_list = list(second_dict.values())

        first_dict: dict[(int, int), MatchedPair] = {}
        for mp in first_list_no_match:
            key = id(mp.l_record), id(mp.r_record)
            if key in first_dict:
                print("Something bad happened2")
            else:
                first_dict[key] = mp

        second_list_no_match: list[MatchedPair] = []
        for mp2 in second_list:
            key = id(mp2.l_record), id(mp2.r_record)
            key_null = id(mp2.l_record), id(NullKeyedRecord)

            if key[1] == id(NullKeyedRecord):
                print("Weird3")
            if (mp1:=first_dict.get(key)) is not None:
                print("This should never happen")   #already should have ben matched above
            elif (mp1:=first_dict.get(key_null)) is not None:
                if mp1.l_result.match_type != MatchType.UNMATCHED or mp1.r_record is not NullKeyedRecord or mp1.r_result.match_type != MatchType.UNMATCHED:
                    print("ERROR!4")
                mp1.r_record = mp2.r_record
                mp1.r_result = mp2.r_result
                results.append(mp1)
                del first_dict[key_null]
            else:
                second_list_no_match.append(mp2)

        first_list_no_match = list(first_dict.values())

        results.extend(first_list_no_match)
        results.extend(second_list_no_match)

        print (time.time() - start)
        return results
