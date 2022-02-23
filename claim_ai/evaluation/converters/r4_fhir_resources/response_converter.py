from typing import Union, Iterable

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import ClaimResponseBuilderFactory
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.models import SingleClaimEvaluationResult, ClaimProvisionEvaluationResult


class ClaimResponseConverter:
    builder = ClaimResponseBuilderFactory()

    def to_ai_output(self, claim, entries_with_evaluation):
        return self._build_claim_response(claim, entries_with_evaluation)

    def claim_response_error(self, claim: dict, error_reason: str):
        return self._build_claim_response_error(claim, error_reason)

    @classmethod
    def _build_claim_response(
            cls, evaluation_result: Union[dict, SingleClaimEvaluationResult],
            items: Union[EvaluationResult, Iterable[ClaimProvisionEvaluationResult]]):
        builder = cls.builder.get_builder(type(evaluation_result).__name__)
        return builder.build_valid_claim_response(evaluation_result, items)

    @classmethod
    def _build_claim_response_error(cls, evaluation_result: Union[dict, SingleClaimEvaluationResult], reason: str):
        builder = cls.builder.get_builder(type(evaluation_result))
        return builder.build_claim_response_error(evaluation_result, reason)
