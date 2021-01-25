from itertools import groupby
from typing import List

from claim_ai.evaluation.converters import AiConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig


class FHIRConverter:
    converter = AiConverter()

    def bundle_ai_input(self, claim_bundle):
        claims = [entry['resource'] for entry in claim_bundle['entry']]
        output = []
        for claim in claims:
            output.append((claim, self.claim_ai_input(claim)))
        return output

    def claim_ai_input(self, fhir_claim_repr):
        input_models = self.converter.to_ai_input(fhir_claim_repr)
        return [model for model in input_models]

    def bundle_ai_output(self, evaluation_output: List[EvaluationResult]):
        response_bundle = {
            'resourceType': 'Bundle',
            'entry': []
        }

        for claim, output in groupby(evaluation_output, lambda x: x.claim):
            claim_fhir_response = self.converter.to_ai_output(claim, list(output))
            entry = {
                'fullUrl': ClaimAiConfig.claim_response_url+'/'+claim['id'],
                'resource': claim_fhir_response
            }
            response_bundle['entry'].append(entry)

        return response_bundle
