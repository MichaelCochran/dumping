from abc import abstractmethod
from velociraptor.types.record import NewRecord, Record
from velociraptor.types.field import Field
from enum import IntEnum

class InsertRecordResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1

class UpdateRecordResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1

class DataInterface:
    @abstractmethod
    def get_records(self, fields: list[Field]) -> list[Record]:
        raise NotImplementedError

    @abstractmethod
    def insert_record(self, record: NewRecord) -> InsertRecordResult:
        raise NotImplementedError

    @abstractmethod
    def is_insert_supported(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_record(self, record: Record) -> UpdateRecordResult:
        raise NotImplementedError

    @abstractmethod
    def update_records(self, records: list[Record]) -> list[UpdateRecordResult]:
        raise NotImplementedError

    @abstractmethod
    def is_update_supported(self) -> bool: # TODO consider driving this from config
        raise NotImplementedError
