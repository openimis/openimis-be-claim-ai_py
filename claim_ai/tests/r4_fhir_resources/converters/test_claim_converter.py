from django.test import TestCase

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.claim import ClaimConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestClaimConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = ClaimConverter()

    @property
    def _expected_output(self):
        return [
            self.HELPER_CLASS.EXPECTED_NON_MUTABLE_CLAIM_ENTRY_FIELDS,
        ]
