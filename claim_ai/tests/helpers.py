import pandas
from .test_fhir_bundle import socket_data
from datetime import datetime

def _fix_len(iterable, expected_len, empty=None):
    new_l = list(iterable)
    while len(new_l) < expected_len:
        new_l.append(empty)
    return new_l


class AiConvertionHelper():
    LONGEST_ENTRY = 10
    TEST_INPUT = socket_data
    EXPECTED_NUMBER_OF_ENTRIES = 2  # One for each claim item
    EXPECTED_NUMBER_OF_ITEM_ENTRIES = 1
    EXPECTED_NUMBER_OF_SERVICE_ENTRIES = 1
    DATE_FORMAT = '%Y-%m-%d'
    
    EXPECTED_ITEM_ENTRY = {
        'identifier': '00B4F099-6122-4327-B033-0872FB1027D8',
        'unitPrice': 10.0,
        'frequency': 0,
        'useContext': bin(15),  # Kid, adult, male, female
        'type': 'Medication'
    }

    EXPECTED_SERVICE_ENTRY = {
        'identifier': '9FD65C19-6889-46D8-9572-A586D17CF286',
        'unitPrice': 400.0,
        'frequency': 0,
        'useContext': bin(6),  # Adult, female
        'type': 'ActivityDefinition'
    }

    EXPECTED_CLAIM_ENTRY_FOR_ITEM = {
        'identifier': 'EA07F16E-1556-4BA6-95AB-38784D058994',
        'billablePeriod_from': datetime.strptime('2020-05-03', DATE_FORMAT),
        'billablePeriod_to': datetime.strptime('2020-05-03', DATE_FORMAT),
        'created': datetime.strptime('2020-05-03', DATE_FORMAT),
        'type': 'O',
        'item.quantity': 2.0,
        'item.unitPrice': 10.0,
        'diagnosis.diagnosisReference_0': 4,
        'diagnosis.diagnosisReference_1': 4,
        'enterer': '99B9C21B-E7B9-455E-9A23-560109FBBB55'
    }

    EXPECTED_CLAIM_ENTRY_FOR_SERVICE = {
        'identifier': 'EA07F16E-1556-4BA6-95AB-38784D058994',
        'billablePeriod_from': datetime.strptime('2020-05-03', DATE_FORMAT),
        'billablePeriod_to': datetime.strptime('2020-05-03', DATE_FORMAT),
        'created': datetime.strptime('2020-05-03', DATE_FORMAT),
        'type': 'O',
        'item.quantity': 1.0,
        'item.unitPrice': 400.0,
        'diagnosis.diagnosisReference_0': 4,
        'diagnosis.diagnosisReference_1': 4,
        'enterer': '99B9C21B-E7B9-455E-9A23-560109FBBB55'
    }

    EXPECTED_NON_MUTABLE_CLAIM_ENTRY_FIELDS = {
        'identifier': 'EA07F16E-1556-4BA6-95AB-38784D058994',
        'billablePeriod_from': datetime.strptime('2020-05-03', DATE_FORMAT),
        'billablePeriod_to': datetime.strptime('2020-05-03', DATE_FORMAT),
        'created': datetime.strptime('2020-05-03', DATE_FORMAT),
        'type': 'O',
        'diagnosis.diagnosisReference_0': 4,
        'diagnosis.diagnosisReference_1': 4,
        'enterer': '99B9C21B-E7B9-455E-9A23-560109FBBB55'
    }

    EXPECTED_PATIENT_ENTRY = {
        'identifier': 'CB8497C2-44E6-4E55-97B5-A88B6C3DEDB3',
        'birthDate': '1993-06-09',
        'gender': 'female',
        'isHead': False,
        'link.type': 8,  # TODO: What should be this value, for set to now identifier type
        'povertyStatus': False,  # Default for not present in the payload
        'locationCode': '63A90675-1BC9-42C6-967B-4D6EE36D4073',
        'group': None,  # TODO: Require implementing fhir api extension
    }

    EXPECTED_HEALTHCARE_ENTRY = {
        'identifier': 'EF9E8621-42E8-4C81-BB41-00A55F4DF467',
        'location': '841419DF-29AB-48DC-B40D-E5A6DE8B1E1E',
        'category': 'COMM',
        'type': 'O'
    }

    EXPECTED_DATAFRAME_ITEM = pandas.DataFrame(
        data={
            'Medication': _fix_len(EXPECTED_ITEM_ENTRY.values(), LONGEST_ENTRY),
            'Claim': _fix_len(EXPECTED_CLAIM_ENTRY_FOR_ITEM.values(), LONGEST_ENTRY),
            'Patient': _fix_len(EXPECTED_PATIENT_ENTRY.values(), LONGEST_ENTRY),
            'HealthcareService': _fix_len(EXPECTED_HEALTHCARE_ENTRY.values(), LONGEST_ENTRY)
        }
    )

    EXPECTED_DATAFRAME_SERVICE = pandas.DataFrame(
        data={
            'ActivityDefinition': _fix_len(EXPECTED_SERVICE_ENTRY.values(), LONGEST_ENTRY),
            'Claim': _fix_len(EXPECTED_CLAIM_ENTRY_FOR_SERVICE.values(), LONGEST_ENTRY),
            'Patient': _fix_len(EXPECTED_PATIENT_ENTRY.values(), LONGEST_ENTRY),
            'HealthcareService': _fix_len(EXPECTED_HEALTHCARE_ENTRY.values(), LONGEST_ENTRY)
        }
    )
