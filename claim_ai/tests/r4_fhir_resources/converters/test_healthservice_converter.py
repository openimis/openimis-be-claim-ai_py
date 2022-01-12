from unittest import TestCase

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.healthcare import OrganizationConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestHealthServiceConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = OrganizationConverter()

    @property
    def _expected_output(self):
        return [
            self.HELPER_CLASS.EXPECTED_HEALTHCARE_ENTRY,
        ]