from abc import abstractmethod

class IJiraProvider:

    @abstractmethod
    def get_required_data_ids(self) -> list[str]:
        raise NotImplementedError
