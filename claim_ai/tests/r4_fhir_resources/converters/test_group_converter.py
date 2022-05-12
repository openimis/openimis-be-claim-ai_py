from django.test import TestCase

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters import GroupConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestGroupConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = GroupConverter()

    @property
    def _expected_output(self):
        return [
            self.HELPER_CLASS.EXPECTED_GROUP_ENTRY,
        ]