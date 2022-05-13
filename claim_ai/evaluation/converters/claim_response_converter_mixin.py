from abc import ABC, abstractmethod
from typing import List
from datetime import date

from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.evaluation.input_models import *
from claim_ai.apps import ClaimAiConfig


class ClaimResponseConverterMixin:
    def to_ai_output(self, claim: dict, entries_with_evaluation: List[EvaluationResult]):
        return {
            "resourceType": "ClaimResponse",
            "status": claim['status'],
            "type": claim['type'],
            "use": claim['use'],
            "patient": {
                "reference": claim['patient']['reference']
            },
            "created": date.today().strftime(ClaimAiConfig.date_format),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": claim['id'],
            "request": {
                "reference": F"Claim/{claim['id']}",
            },
            "outcome": "complete",
            "item": self._build_items(entries_with_evaluation)
        }

    def _build_items(self, entries_with_evaluation):
        response_items = []
        for entry in entries_with_evaluation:
            sequence = 0
            provided = entry.input
            result = str(entry.result)  # result is in str type
            claim = provided.claim
            if provided.medication:
                response_item = self.medication_converter\
                        .to_ai_output(provided.medication, claim, result, sequence)
                response_items.append(response_item)
                sequence += 1
            if provided.activity_definition:
                response_item = self.activity_definition_converter\
                    .to_ai_output(provided.activity_definition, claim, result, sequence)
                response_items.append(response_item)
                sequence += 1

        return response_items

    def claim_response_error(self, claim: dict, error_reason: str):
        return {
            "resourceType": "ClaimResponse",
            "status": claim['status'],
            "type": claim['type'],
            "use": claim['use'],
            "patient": {
                "reference": claim['patient']['reference']
            },
            "created": date.today().strftime(ClaimAiConfig.date_format),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": claim['id'],
            "request": {
                "reference": F"Claim/{claim['id']}",
            },
            "outcome": "error",
            "error": [
                {
                    "coding": [{
                        "code": "-1"
                    }],
                    "text": error_reason
                }
            ]
        }
