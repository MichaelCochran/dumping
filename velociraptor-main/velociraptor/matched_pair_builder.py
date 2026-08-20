from velociraptor.interfaces.data_interface_collection import DataInterfaceCollection
from velociraptor.types.config_manager import CompareSourceConfig, ConfigManager
from velociraptor.types.keyed_record import KeyedRecord
from velociraptor.types.keyed_record_joiner import KeyedRecordJoiner

def __build_keyed_records(config_mgr: ConfigManager, data_interfaces: DataInterfaceCollection, source_config: CompareSourceConfig):
    data_interface = data_interfaces.get_interface_by_id(source_config.data_interface_id)
    source_id = source_config.id
    pk_id = source_config.pk_field_id
    pk_field = config_mgr.get_field_by_id(pk_id) if pk_id is not None else None
    if pk_field is not None and pk_field.source_id != source_id:
        raise Exception(f"Primary key id '{pk_id}' does not have expected source_id '{source_id}'")
    fk_id = source_config.fk_field_id
    fk_field = config_mgr.get_field_by_id(fk_id) if fk_id is not None else None
    if fk_field is not None and fk_field.source_id != source_id:
        raise Exception(f"Foreign key id '{fk_id}' does not have expected source_id '{source_id}'")

    fields = config_mgr.get_field_list_by_source_id(source_id)
    records = data_interface.get_records(fields)

    return list(map(lambda record: KeyedRecord.create(pk_field, fk_field, record), records))

def build_matched_pairs(config_mgr: ConfigManager, data_interfaces: DataInterfaceCollection):
    # TODO decouple matchedpairs, keyedrecordcomparisons and keyedrecordupdates so generic independent objects can be passed in and returned
    # And/or flatten objects (don't make each stage depend on the result from the previous, but rather more generic inputs?)

    left_keyed_records = __build_keyed_records(config_mgr, data_interfaces, config_mgr.get_left_source_config())
    right_keyed_records = __build_keyed_records(config_mgr, data_interfaces, config_mgr.get_right_source_config())
    return KeyedRecordJoiner.join(left_keyed_records, right_keyed_records)
