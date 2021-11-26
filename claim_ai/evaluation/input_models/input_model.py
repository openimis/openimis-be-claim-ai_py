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
    alias = {}

    def alias_or_default(self, name):
        return self.alias.get(name, name)


# Medication and ActivityDefinition have same fields
class ProvidedItem(BaseDataFrameModel):
    identifier = None
    unit_price = None
    frequency = None
    use_context = None
    item_level = None

    alias = {
        'identifier': 'ItemUUID',
        'unit_price': 'ItemPrice',
        'frequency': 'ItemFrequency',
        'use_context': 'ItemPatCat',
        'item_level': 'ItemLevel',
        'type': 'ItemServiceType'
    }


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

    alias = {
        'identifier': 'ClaimUUID',
        'billable_period_from': 'DateFrom',
        'billable_period_to': 'DateTo',
        'created': 'DateClaimed',
        'type': 'VisitType',
        'item_quantity': 'QtyProvided',
        'item_unit_price': 'PriceAsked',
        'diagnosis_0': 'ICDID',
        'diagnosis_1': 'ICDID1',
        'enterer': 'ClaimAdminUUID'
    }


class Patient(BaseDataFrameModel):
    identifier = None
    birth_date = None
    gender = None
    is_head = None
    poverty_status = None
    location_code = None
    group = None

    alias = {
        'identifier': 'InsureeUUID',
        'birth_date': 'DOB',
        'gender': 'Gender',
        'is_head': 'IsHead',  # This value is not present in the AiModel
        'poverty_status': 'PovertyStatus',  # This value is not present in the AiModel
        'location_code': 'LocationUUID',
        'group': 'FamilyUUID'
    }


class HealthcareService(BaseDataFrameModel):
    identifier = None
    location = None
    category = None
    type = None

    alias = {
        'identifier': 'HFUUID',
        'location': 'HFLocationUUID',
        'category': 'HFLevel',
        'type': 'HFCareType'
    }


class AiInputModel(BaseDataFrameModel):
    medication = None
    activity_definition = None
    claim = None
    patient = None
    healthcare_service = None

    def to_representation(self, flat=False):
        df = pandas.DataFrame()
        if flat:
            out = {}
            for next_entry in self.__dict__.values():
                if next_entry:
                    for k, v in next_entry.__dict__.items():
                        k = next_entry.alias_or_default(k)
                        out[k] = v
            return out

        for variable, value in self.__dict__.items():
            variable_frame = value.to_representation() if value else pandas.DataFrame()  # empty dataframe if empty
            # Remove index
            variable_frame.reset_index(inplace=True, drop=True)
            df = pandas.concat([df, variable_frame], axis=1)
        return df
