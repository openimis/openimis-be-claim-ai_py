import pandas as pd
from django.test import TestCase

from pandas._testing import assert_frame_equal

from claim_ai.evaluation.converters import AiConverter
from claim_ai.tests.r4_fhir_resources.converters.base_case import BaseConverterTestCaseMixin


class TestAiConverter(TestCase, BaseConverterTestCaseMixin):
    CONVERTER_CLASS = AiConverter()

    def test_converter(self):
        actual_output = self._convert()
        cols = self._expected_output.columns.tolist()
        actual_output = actual_output[cols]  # Ensure order of columns is matching
        assert_frame_equal(
            actual_output, self._expected_output
        )

    @property
    def _expected_output(self):
        self.maxDiff = None
        return self.HELPER_CLASS.EXPECTED_DATAFRAME

    def _convert(self):
        instance = self.CONVERTER_CLASS
        entry = self.FHIR_BUNDLE_PAYLOAD['entry'][0]['resource']
        conversion_result = instance.to_ai_input(entry)
        rows = [x.to_representation(flat=True) for x in conversion_result]
        return pd.DataFrame(rows)
