from fhir.resources.claimresponse import ClaimResponse
from typing import List

from api_fhir_r4.utils import TimeUtils
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation.converters.r4_fhir_resources.adjudication_builder import AdjudicationBuilder


class ClaimResponseConverter:
    adjudication_builder = AdjudicationBuilder()

    def to_ai_output(self, claim: dict, entries_with_evaluation: List[EvaluationResult]):
        return self._to_input_dict(claim, entries_with_evaluation)

    def claim_response_error(self, claim: dict, error_reason: str):
        return self.__to_claim_response_error(claim, error_reason)

    def _to_input_dict(self, claim: dict, entries_with_evaluation: List[EvaluationResult]):
        return ClaimResponse(**{
            **self.__common_response_fields(claim),
            "request": {
                "reference": F"Claim/{claim['id']}",
            },
            "outcome": "complete",
            "item": self._build_items(entries_with_evaluation)
        })

    def __to_claim_response_error(self, claim, error_reason):
        return ClaimResponse(**{
            **self.__common_response_fields(claim),
            "outcome": "error",
            "error": [
                {
                    "coding": [{
                        "code": "-1"
                    }],
                    "text": error_reason
                }
            ]
        })

    def __common_response_fields(self, claim):
        return {
            "resourceType": "ClaimResponse",
            "status": claim['status'],
            "type": claim['type'],
            "use": claim['use'],
            "patient": {
                "reference": claim['patient']['reference']
            },
            "created": TimeUtils.date().isoformat(),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": claim['id'],
            "request": {
                "reference": F"Claim/{claim['id']}",
            }
        }

    def _build_items(self, entries_with_evaluation: List[EvaluationResult]):
        response_items = []
        for entry in entries_with_evaluation:
            sequence = 1
            provided = entry.input
            result = str(entry.result)  # result is in str type
            response_item = self._provision_to_claim_response_item(provided, result, sequence)
            response_items.append(response_item)
            sequence += 1

        return response_items

    def _provision_to_claim_response_item(self, provision, evaluation_result, sequence):
        return self.adjudication_builder\
            .build_claim_response_item_adjudication(provision, evaluation_result, sequence)



