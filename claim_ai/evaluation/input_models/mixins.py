import pandas


class DataFrameRepresentationMixin:

    def to_representation(self) -> pandas.DataFrame:
        # get instance attributes and transform them to dataframe
        # class ordering is preserved
        return pandas.DataFrame(
            data=[attribute for attribute in self.__dict__.values()],
            columns=[str(type(self).__name__)],
            index=[index for index in self.__dict__.keys()]
        )
