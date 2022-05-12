from django.test import TestCase

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters import ActivityDefinitionConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestActivityDefinitionConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = ActivityDefinitionConverter()

    @property
    def _expected_output(self):
        self.maxDiff = None
        return [
            self.HELPER_CLASS.EXPECTED_SERVICE_ENTRY_1,
            self.HELPER_CLASS.EXPECTED_SERVICE_ENTRY_2
        ]
