from django.test import TestCase

from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.patient import PatientConverter


class TestPatientConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = PatientConverter()

    @property
    def _expected_output(self):
        return [
            self.HELPER_CLASS.EXPECTED_PATIENT_ENTRY,
        ]


