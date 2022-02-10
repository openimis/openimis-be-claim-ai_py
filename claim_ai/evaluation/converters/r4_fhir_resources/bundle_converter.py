import logging
import traceback

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import BundleBuilderFactory
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.evaluation.converters import AiConverter
from claim_ai.evaluation.converters.base_converter import AbstractAIBundleConverter

logger = logging.getLogger(__name__)


class BundleConverter(AbstractAIBundleConverter):
    ai_input_converter = AiConverter()
    bundle_builder = BundleBuilderFactory()

    def to_ai_input(self, fhir_claim_resource: dict):
        claims = [entry['resource'] for entry in fhir_claim_resource['entry']]
        correctly_transformed_claims = []
        errors = []
        for claim in claims:
            try:
                correctly_transformed_claims.append((claim, self.__claim_ai_input(claim)))
            except Exception as e:
                logger.debug(traceback.format_exc())
                errors.append((claim, str(e)))
        return correctly_transformed_claims, errors

    def __claim_ai_input(self, fhir_claim_repr):
        input_models = self.ai_input_converter.to_ai_input(fhir_claim_repr)
        return [model for model in input_models]

    def bundle_ai_output(self, evaluation_output, invalid_claims):
        evaluation_type = self._get_evaluation_output_type()
        return self.bundle_builder.get_builder(evaluation_type).build_fhir_bundle(evaluation_output, invalid_claims)

    @classmethod
    def _get_evaluation_output_type(cls):
        return EvaluationResult.__name__
