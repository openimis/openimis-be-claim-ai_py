from abc import ABC
from typing import Union, Type


class GenericBuilderFactory(ABC):
    @property
    def REGISTERED_BUILDERS(self):
        raise NotImplementedError()

    @property
    def _init_kwargs(self):
        raise NotImplementedError()

    def get_builder(self, result_type: Union[str, Type]):
        """
        Get builder for given result type. result type can be either string or obj. If it's object then it's type is
        transformed to string and used.
        """
        if isinstance(result_type, type):
            result_type = str(result_type.__name__)
        if result_type not in self.REGISTERED_BUILDERS:
            raise NotImplementedError(
                f"Builder for type {result_type} not found. "
                f"Available types are: {self.REGISTERED_BUILDERS.keys()}")

        return self.REGISTERED_BUILDERS[result_type](**self._init_kwargs)
