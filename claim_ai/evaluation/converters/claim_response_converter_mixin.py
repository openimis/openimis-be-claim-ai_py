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