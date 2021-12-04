from abc import abstractmethod

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import FHIRResourceConverter
from claim_ai.tests.r4_fhir_resources.utils import BASE_FHIR_PAYLOAD, ConverterHelper


class BaseConverterTestCaseMixin:
    HELPER_CLASS = ConverterHelper()
    FHIR_BUNDLE_PAYLOAD = BASE_FHIR_PAYLOAD
    CONVERTER_CLASS: FHIRResourceConverter = None

    def test_converter(self):
        self.assertEqual(
            self._convert(), self._expected_output
        )

    def _convert(self):
        instance = self.CONVERTER_CLASS
        entry = self.FHIR_BUNDLE_PAYLOAD['entry'][0]['resource']
        conversion_result = instance.to_ai_input(entry)
        # Wraps base converter output to list
        conversion_result = conversion_result if isinstance(conversion_result, list) else [conversion_result]
        return [e.to_dict() for e in conversion_result]

    @property
    @abstractmethod
    def _expected_output(self):
        pass
