from enum import Enum
from velociraptor.types.keyed_record import KeyedRecord

class MatchSide(Enum):
    LEFT = 0,
    RIGHT = 1


class MatchType(Enum):
    # There is no MANY_TO_MANY because the match is unidirectional, with a status indicated for each side of the match
    UNMATCHED = "Unmatched" # The primary key of this side did not join the other side
    ONE_TO_ONE = "1:1" # The primary key of this side joined one record on the other side
    ONE_TO_MANY = "1:M" # The primary key of this side joined multiple records on the other side

    def __eq__(self, other: 'MatchType'):
        if isinstance(other, MatchType):
            return self.value == other.value
        else: return NotImplemented

    def __lt__(self, other: 'MatchType'):
        if isinstance(other, MatchType):
            return self.value < other.value
        else: return NotImplemented

class MatchResult:
    def __init__(self, match_type: MatchType, is_pk_duplicate: bool):
        self.match_type: MatchType = match_type # Incidates how the primary key of this side joined with the other side
        self.is_pk_duplicate: bool = is_pk_duplicate # Indicates whether the primary key is duplicated (not unique) among all records

    def __str__(self):
        ret = str(self.match_type)
        ret += "\t"
        ret += "*" if self.is_pk_duplicate else ""
        return ret

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: 'MatchResult'):
        if isinstance(other, MatchResult):
            return (self.match_type == other.match_type and
                    self.is_pk_duplicate == other.is_pk_duplicate)
        else: return NotImplemented

    def __lt__(self, other: 'MatchResult'):
        if isinstance(other, MatchResult):
            if self.match_type != other.match_type: return self.match_type < other.match_type
            else: return self.is_pk_duplicate < other.is_pk_duplicate
        else: return NotImplemented

class MatchedPair: ## TODO rename to KeyedRecordJoinedPair???
    def __init__(self, l_record: KeyedRecord, r_record: KeyedRecord):
        self.l_record = l_record
        self.r_record = r_record
        self.l_result = MatchResult(MatchType.UNMATCHED, False)
        self.r_result = MatchResult(MatchType.UNMATCHED, False)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        ret =  str(self.l_record)
        ret += '\t'
        ret +=  str(self.l_result)
        ret += '\t'
        ret += str(self.r_record)
        ret += '\t'
        ret += str(self.r_result)
        return ret

    def __eq__(self, other: 'MatchedPair'):
        if isinstance(other, MatchedPair):
            return (self.l_record == other.l_record and
                    self.r_record == other.r_record and
                    self.l_result == other.l_result and
                    self.r_result == other.r_result)
        else: return NotImplemented

    def __lt__(self, other: 'MatchedPair'):
        if isinstance(other, MatchedPair):
            if self.l_record != other.l_record: return self.l_record < other.l_record
            elif self.r_record != other.r_record: return self.r_record < other.r_record
            elif self.l_result != other.l_result: return self.l_result < other.l_result
            else: return self.r_result < other.r_result
        else: return NotImplemented

    def get_record(self, side: MatchSide):
        if side == MatchSide.LEFT:
            return self.l_record.record
        elif side == MatchSide.RIGHT:
            return self.r_record.record
        else:
            raise Exception
