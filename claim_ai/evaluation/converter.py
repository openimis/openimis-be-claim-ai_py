from itertools import groupby
from typing import List

import traceback
import logging

from claim_ai.evaluation.converters.legacy_converter import AiConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig

logger = logging.getLogger(__name__)


class FHIRConverter:
    converter = AiConverter()

    def bundle_ai_input(self, claim_bundle):
        claims = [entry['resource'] for entry in claim_bundle['entry']]
        correctly_transformed_claims = []
        errors = []
        for claim in claims:
            try:
                correctly_transformed_claims.append((claim, self.claim_ai_input(claim)))
            except Exception as e:
                logger.debug(traceback.format_exc())
                errors.append((claim, str(e)))
        return correctly_transformed_claims, errors

    def claim_ai_input(self, fhir_claim_repr):
        input_models = self.converter.to_ai_input(fhir_claim_repr)
        return [model for model in input_models]

    def bundle_ai_output(self, evaluation_output: List[EvaluationResult], invalid_claims):
        response_bundle = {
            'resourceType': 'Bundle',
            'entry': []
        }

        for claim, output in groupby(evaluation_output, lambda x: x.claim):
            claim_fhir_response = self.converter.to_ai_output(claim, list(output))
            entry = {
                'fullUrl': ClaimAiConfig.claim_response_url+'/'+str(claim['id']),
                'resource': claim_fhir_response
            }
            response_bundle['entry'].append(entry)

        for invalid_claim, rejection_reason in invalid_claims:
            claim_fhir_response = self.converter.claim_response_error(invalid_claim, rejection_reason)
            entry = {
                'fullUrl': ClaimAiConfig.claim_response_url+'/'+str(invalid_claim['id']),
                'resource': claim_fhir_response
            }
            response_bundle['entry'].append(entry)

        return response_bundle
