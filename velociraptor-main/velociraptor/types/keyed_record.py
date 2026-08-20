from velociraptor.types.field import Field
from velociraptor.types.record import Record

#@dataclass   # this was dangerous.   need to read full requirements of dataclass
class KeyedRecord:
    @staticmethod
    def create(pk_field: Field, fk_field: Field, record: Record):
        return KeyedRecord(record.get_value(pk_field) if pk_field is not None else None,
                           record.get_value(fk_field) if fk_field is not None else None,
                           record)

    def __init__(self, pk: str, fk: str, record: Record):
        self._pk = pk
        self._fk = fk
        self._record = record

#TODO consider making these private... should access through "getValue" only?
    @property
    def pk(self):
        return self._pk

    @property
    def fk(self):
        return self._fk

    @property
    def record(self):
        return self._record

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        value  = self.pk if self.pk is not None else "<None>"
        value += '\t'
        value += self.fk if self.fk is not None else "<None>"
#        value += '\t'
#        summary = self.getValue("summary")
#        value += summary if summary is not None else "<None>"
        return value

    def __eq__(self, other: 'KeyedRecord'):
        if isinstance(other, KeyedRecord):
            return (self.pk == other.pk and
                    self.fk == other.fk and
                    self.record == other.record)
        else: return NotImplemented

    def __lt__(self, other: 'KeyedRecord'):
        if isinstance(other, KeyedRecord):
            if self.pk is None and other.pk is not None: return False
            elif self.pk is not None and other.pk is None: return True
            elif self.pk != other.pk: return self.pk < other.pk
            elif self.fk is None and other.fk is not None: return False
            elif self.fk is not None and other.fk is None: return True
            elif self.fk != other.fk: return self.fk < other.fk
            elif self.record is None and other.record is not None: return False
            elif self.record is not None and other.record is None: return True
            elif self.record != other.record: return self.record < other.record
            else: return False # Both are None
        else: return NotImplemented

NullKeyedRecord = KeyedRecord(None, None, None)
