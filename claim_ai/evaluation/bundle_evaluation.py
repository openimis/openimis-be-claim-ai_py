from claim_ai.evaluation.converter import FHIRConverter
from ..test_response_bundle import adjudication_bundle


class ClaimBundleEvaluation:
    converter = FHIRConverter()

    @classmethod
    def evaluate_bundle(cls, claim_bundle):
        ai_input = cls.converter.bundle_ai_input(claim_bundle)
        evaluation_result = []
        for next_input_record in ai_input:
            evaluation_result.append(cls._evaluate(next_input_record))

        return cls._build_response_bundle(evaluation_result)

    @classmethod
    def _build_response_bundle(cls, evaluation_resutl):
        # TODO: Add real build here
        return adjudication_bundle

    @classmethod
    def _evaluate(cls, claim):
        # TODO: Call AI Evaluation here
        return True

