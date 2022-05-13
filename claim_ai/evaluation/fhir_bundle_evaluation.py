from enum import Enum, auto

import pandas
from claim_ai.evaluation.predictor import AiPredictor
from claim_ai.evaluation.converters import BundleConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult


class ClaimBundleEvaluationOutputFormat(Enum):
    FHIR_RESPONSE = auto()
    EVALUATION_RESULT = auto()


class ClaimBundleEvaluator:
    fhir_converter = BundleConverter()
    ai_model = AiPredictor()

    @classmethod
    def evaluate_bundle(cls, claim_bundle, output_format=ClaimBundleEvaluationOutputFormat.FHIR_RESPONSE):
        ai_input, errors = cls.fhir_converter.to_ai_input(claim_bundle)
        evaluation_result = []
        input_ = [item.to_representation(flat=True) for _, claim_input in ai_input for item in claim_input]
        if input_:
            valid, prediction = cls.ai_model.evaluate_bundle(pandas.DataFrame(input_))
            for index, (claim, claim_inputs) in enumerate(ai_input):
                if not valid[index]:
                    continue
                else:
                    for item_input in claim_inputs:
                        item_evaluation = EvaluationResult(claim, item_input, prediction[index])
                        evaluation_result.append(item_evaluation)

        if output_format == ClaimBundleEvaluationOutputFormat.FHIR_RESPONSE:
            return cls._build_response_bundle(evaluation_result, invalid_claims=errors)
        elif output_format == ClaimBundleEvaluationOutputFormat.EVALUATION_RESULT:
            return evaluation_result
        else:
            raise AttributeError(f"Invalid output format: {output_format}")

    @classmethod
    def _build_response_bundle(cls, evaluation_result, invalid_claims):
        return cls.fhir_converter.bundle_ai_output(evaluation_result, invalid_claims)
