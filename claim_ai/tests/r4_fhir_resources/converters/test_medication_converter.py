from unittest import TestCase

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.medication import MedicationConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestMedicationConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = MedicationConverter()

    @property
    def _expected_output(self):
        return [
            self.HELPER_CLASS.EXPECTED_ITEM_ENTRY,
        ]
