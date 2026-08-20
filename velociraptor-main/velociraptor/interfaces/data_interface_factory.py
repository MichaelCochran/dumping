'''
----------------------------------------------------------------------------
Library   : None
Package   : None
Class     : None
Engineers : Ted Paulakis
Abstract  : TBD
----------------------------------------------------------------------------
'''

from velociraptor.types.data_interface import DataInterface
from velociraptor.interfaces.jira_interface import JiraInterface
from velociraptor.interfaces.jira_interface_sim import JiraInterfaceSim
from velociraptor.interfaces.sheet_interface import SheetInterface
from velociraptor.types.config_manager import DataInterfaceTypeEnum
from velociraptor.types.data_interface_config import JiraInterfaceConfig, JiraInterfaceSimConfig, SheetInterfaceConfig

class DataInterfaceFactory:
    @staticmethod
    def build_data_interface(source_type: DataInterfaceTypeEnum, data_interface_config) -> DataInterface:
        if source_type == DataInterfaceTypeEnum.JIRA and isinstance(data_interface_config, JiraInterfaceConfig):
            data_interface = JiraInterface(data_interface_config)
        elif source_type == DataInterfaceTypeEnum.JIRA_SIM and isinstance(data_interface_config, JiraInterfaceSimConfig):
            data_interface = JiraInterfaceSim(data_interface_config)
        elif source_type == DataInterfaceTypeEnum.SHEET and isinstance(data_interface_config, SheetInterfaceConfig):
            data_interface = SheetInterface(data_interface_config)
        else:
            raise Exception(f"Unsupported source_type ('{source_type.name}')")

        return data_interface
