import datetime
import core

from unittest import TestCase
from unittest import mock

from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation import converter
from claim_ai.evaluation.converters import AiConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.tests import socket_data, AiConvertionHelper


class TestAiInputConverter(TestCase):
    TEST_BUNDLE = socket_data
    TEST_HELPER = AiConvertionHelper
    CONVERTER = AiConverter()

    def test_conversion(self):
        ai_converter = converter.FHIRConverter()
        claim = self.TEST_BUNDLE['entry'][0]['resource']  # Get first claim from test bundle

        test_input = self.CONVERTER.to_ai_input(claim)
        test_output = [EvaluationResult(claim, evaluation_input, 0) for evaluation_input in test_input]
        test_output[0].result = 0
        test_output[1].result = 1
        generated_output = ai_converter.bundle_ai_output(test_output, [])
        output_entry = generated_output['entry']
        output_claim_response = output_entry

        self.assertEqual(len(output_entry), 1)  # Output for single claim
        self.assertEqual(len(output_entry[0]['resource']['item']), 2)  # Claim bundle have one item and one service
        self.assertEqual(generated_output['resourceType'], 'Bundle')  # Type bundle
        self.__assertClaimResponse(claim, output_entry[0])

        accepted = output_entry[0]['resource']['item'][0]
        rejected = output_entry[0]['resource']['item'][1]
        self.__assertClaimResponseItem(accepted, claim['item'][0], accepted=True)  # First was accepted
        self.__assertClaimResponseItem(rejected, claim['item'][1], accepted=False)  # Second was rejected

    def __assertClaimResponse(self, input_claim, output_claim_response):
        resource = output_claim_response['resource']
        # first part of url is taken from config but ends with /claim_uuid
        self.assertTrue(output_claim_response['fullUrl'].endswith(input_claim['id']))
        self.assertEqual(resource['resourceType'], 'ClaimResponse')
        self.assertEqual(resource['status'], input_claim['status'])
        self.assertEqual(resource['use'], input_claim['use'])
        self.assertEqual(resource['patient']['reference'], input_claim['patient']['reference'])
        self.assertEqual(resource['insurer']['reference'], F"Organization/{ClaimAiConfig.claim_response_organization}")
        self.assertEqual(resource['id'], input_claim['id'])
        self.assertEqual(resource['outcome'], 'complete')

    def __assertClaimResponseItem(self, claim_response_item, claim_item, accepted=True):
        self.assertEqual(len(claim_response_item['adjudication']), 1)
        self.__assert_adjudication(claim_response_item['adjudication'][0], claim_item, accepted)

    def __assert_adjudication(self, claim_response_adjudication, input_claim_item, accepted=True):
        category = claim_response_adjudication['category']
        self.assertEqual(category['text'], 'AI')
        self.assertEqual(len(category['coding']), 1)
        self.assertEqual(category['coding'][0]['code'], "-2")  # Category is always "-2"

        reason = claim_response_adjudication['reason']
        self.assertEqual(reason['text'], 'accepted' if accepted else 'rejected')
        self.assertEqual(reason['coding'][0]['code'], '0' if accepted else '1')

        amount = claim_response_adjudication['amount']

        self.assertEqual(amount['currency'], core.currency if hasattr(core, 'currency') else None)
        self.assertEqual(amount['value'], input_claim_item['unitPrice']['value'])
        self.assertEqual(claim_response_adjudication['value'], input_claim_item['quantity']['value'])
        pass

