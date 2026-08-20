from velociraptor.types.data_interface import DataInterface
from velociraptor.interfaces.data_interface_factory import DataInterfaceFactory
from velociraptor.types.config_manager import ConfigManager

class DataInterfaceCollection:
    def __init__(self, config_mgr: ConfigManager):
        self.__data_interface_by_id_dict: dict[str, DataInterface] = {}

        for data_interface_config in config_mgr.get_data_interface_config_list():
            self.__data_interface_by_id_dict[data_interface_config.id] = DataInterfaceFactory.build_data_interface(data_interface_config.type, data_interface_config.config)

    def get_interface_by_id(self, id: str):
        return self.__data_interface_by_id_dict[id]
