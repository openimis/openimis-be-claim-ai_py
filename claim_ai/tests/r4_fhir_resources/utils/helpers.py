import pandas
import pandas as pd
from numpy import nan

from claim_ai.tests.r4_fhir_resources.utils.test_fhir_bundle import socket_data
from datetime import datetime


def _fix_len(iterable, expected_len, empty=nan):
    new_l = list(iterable)
    while len(new_l) < expected_len:
        new_l.append(empty)
    return new_l


class ConverterHelper:
    LONGEST_ENTRY = 10
    TEST_INPUT = socket_data
    EXPECTED_NUMBER_OF_ENTRIES = 3  # One for each claim item
    EXPECTED_NUMBER_OF_ITEM_ENTRIES = 1
    EXPECTED_NUMBER_OF_SERVICE_ENTRIES = 2
    DATE_FORMAT = '%Y-%m-%d'
    
    EXPECTED_ITEM_ENTRY = {
        'ItemUUID': '182',
        'ItemPrice': 10.0,
        'ItemLevel': 'M',
        'ItemFrequency': 1,
        'ItemPatCat': 15,  # Kid, adult, male, female
        'ItemServiceType': 'Medication',
        'QtyProvided': 2,
        'PriceAsked': 10.0,
    }

    EXPECTED_SERVICE_ENTRY_1 = {
        'ItemUUID': '90',
        'ItemPrice': 400.0,
        'ItemLevel': 'D',
        'ItemFrequency': 1,
        'ItemPatCat': 6,  # Adult, female
        'ItemServiceType': 'ActivityDefinition',
        'QtyProvided': 10,
        'PriceAsked': 400.0
    }

    EXPECTED_SERVICE_ENTRY_2 = {
        'ItemUUID': '86',
        'ItemPrice': 1250.0,
        'ItemLevel': 'S',
        'ItemFrequency': 1,
        'ItemPatCat': 9,  # Child, male
        'ItemServiceType': 'ActivityDefinition',
        'QtyProvided': 55,
        'PriceAsked': 1250.0
    }

    EXPECTED_NON_MUTABLE_CLAIM_ENTRY_FIELDS = {
        'ClaimUUID': '1',
        'DateFrom': datetime.strptime('2021-03-03', DATE_FORMAT),
        'DateTo': datetime.strptime('2021-03-03', DATE_FORMAT),
        'DateClaimed': datetime.strptime('2021-03-03', DATE_FORMAT),
        'VisitType': 'O',
        'ICDID': 'A02',
        'ICDID1': 'A02',
        'ClaimAdminUUID': '16'
    }

    EXPECTED_PATIENT_ENTRY = {
        'InsureeUUID': '47',
        'DOB': datetime(1993, 6, 9, 0, 0),
        'Gender': 'F',
        'IsHead': False,
        'LocationUUID': '45'
    }

    EXPECTED_GROUP_ENTRY = {
        'FamilyUUID': '18',
        'PovertyStatus': False
    }

    EXPECTED_HEALTHCARE_ENTRY = {
        'HFUUID': '18',
        'HFLocationUUID': '18',
        'HFLevel': 'D',
        'HFCareType': 'O'
    }

    @property
    def EXPECTED_DATAFRAME(self):
        # Note: This values are later on normalized, DOB is changed to Age,
        # IsHead and PovertyStatus are removed
        columns = [
            'ClaimUUID', 'DateFrom', 'DateTo', 'DateClaimed', 'VisitType', 'ICDID',
           'ICDID1', 'ClaimAdminUUID', 'PovertyStatus', 'FamilyUUID', 'HFUUID',
           'HFLocationUUID', 'HFLevel', 'HFCareType', 'InsureeUUID', 'DOB',
           'Gender', 'IsHead', 'LocationUUID', 'ItemUUID', 'ItemPrice', 'ItemLevel',
           'ItemFrequency', 'ItemPatCat', 'QtyProvided', 'PriceAsked',
           'ItemServiceType'
        ]
        immutable_cells = {
            **self.EXPECTED_PATIENT_ENTRY,
            **self.EXPECTED_NON_MUTABLE_CLAIM_ENTRY_FIELDS,
            **self.EXPECTED_HEALTHCARE_ENTRY,
            **self.EXPECTED_GROUP_ENTRY
        }
        mutable = [
            self.EXPECTED_ITEM_ENTRY,
            self.EXPECTED_SERVICE_ENTRY_1,
            self.EXPECTED_SERVICE_ENTRY_2
        ]
        rows = [{**immutable_cells, **next_mutable} for next_mutable in mutable]
        for row in rows:
            assert set(row.keys()) == set(columns), \
                F'Not all columns covered in expected test dataframe instance: {set(row.keys()) ^ set(columns)}'
        return pd.DataFrame(rows)
