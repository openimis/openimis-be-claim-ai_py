import pandas

from .mixins import DataFrameRepresentationMixin


class BaseModel:

    def __init__(self, **fields):
        for field, value in fields.items():
            if hasattr(self, field):
                setattr(self, field, value)
            else:
                raise ValueError(F"Field {field} not available for class {self.__class__}")

    def to_representation(self) -> pandas.DataFrame:
        raise NotImplementedError("to_ai_input_representation not implemented")


class BaseDataFrameModel(DataFrameRepresentationMixin, BaseModel):
    pass


# Medication and ActivityDefinition have same fields
class ProvidedItem(BaseDataFrameModel):
    identifier = None
    unit_price = None
    frequency = None
    use_context = None


class Medication(ProvidedItem):
    def __init__(self, **fields):
        super().__init__(**fields)
        self.type = 'Medication'  # fixed


class ActivityDefinition(ProvidedItem):
    def __init__(self, **fields):
        super().__init__(**fields)
        self.type = 'ActivityDefinition'  # fixed


class Claim(BaseDataFrameModel):
    identifier = None
    billable_period_from = None
    billable_period_to = None
    created = None
    type = None
    item_quantity = None
    item_unit_price = None
    diagnosis_0 = None
    diagnosis_1 = None
    enterer = None


class Patient(BaseDataFrameModel):
    identifier = None
    birth_date = None
    gender = None
    is_head = None
    poverty_status = None
    location_code = None
    group = None


class HealthcareService(BaseDataFrameModel):
    identifier = None
    location = None
    category = None
    type = None


class AiInputModel(BaseDataFrameModel):
    medication = None
    activity_definition = None
    claim = None
    patient = None
    healthcare_service = None

    def to_representation(self):
        df = pandas.DataFrame()
        for variable, value in self.__dict__.items():

            variable_frame = value.to_representation() if value else pandas.DataFrame()  # empty dataframe if empty
            # Remove index
            variable_frame.reset_index(inplace=True, drop = True)
            df = pandas.concat([df, variable_frame], axis=1)
        return df
