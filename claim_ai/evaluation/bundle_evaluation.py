from claim_ai.evaluation.converter import FHIRConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult


class ClaimBundleEvaluation:
    fhir_converter = FHIRConverter()

    @classmethod
    def evaluate_bundle(cls, claim_bundle):
        ai_input = cls.fhir_converter.bundle_ai_input(claim_bundle)
        evaluation_result = []
        for claim, claim_inputs in ai_input:
            for item_input in claim_inputs:
                item_evaluation = EvaluationResult(claim, item_input, cls._evaluate(item_input.to_representation()))
                evaluation_result.append(item_evaluation)

        return cls._build_response_bundle(evaluation_result)

    @classmethod
    def _build_response_bundle(cls, evaluation_result):
        return cls.fhir_converter.bundle_ai_output(evaluation_result)

    @classmethod
    def _evaluate(cls, input):
        # TODO: Call AI Evaluation here, currently all claims are accepted
        return 0

