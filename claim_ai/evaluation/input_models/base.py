import pandas


class BaseModel:

    def __init__(self, **fields):
        for field, value in fields.items():
            if hasattr(self, field):
                setattr(self, field, value)
            else:
                raise ValueError(F"Field {field} not available for class {self.__class__}")

    def to_representation(self) -> pandas.DataFrame:
        raise NotImplementedError("to_ai_input_representation not implemented")


class DataFrameRepresentationMixin:
    def to_representation(self) -> pandas.DataFrame:
        # get instance attributes and transform them to dataframe
        # class ordering is preserved
        return pandas.DataFrame(
            data=[attribute for attribute in self.__dict__.values()],
            columns=[str(type(self).__name__)],
            index=[self.alias_or_default(index) for index in self.__dict__.keys()]
        )


class BaseDataFrameModel(DataFrameRepresentationMixin, BaseModel):
    alias = {}

    def alias_or_default(self, name):
        return self.alias.get(name, name)

    def to_dict(self, use_alias=True):
        dict_ = {}
        for k, v in self.__dict__.items():
            k = self.alias.get(k, k) if use_alias else k
            dict_[k] = v
        return dict_
