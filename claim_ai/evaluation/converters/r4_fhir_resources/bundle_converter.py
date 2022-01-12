import itertools
import logging
import traceback

from typing import List, Tuple

from fhir.resources.bundle import Bundle, BundleEntry

from claim_ai.evaluation.converters.r4_fhir_resources.response_converter import ClaimResponseConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation.converters import AiConverter
from claim_ai.evaluation.converters.base_converter import BaseAIConverter, AbstractAIBundleConverter
from claim_ai.evaluation.converters.claim_response_converter_mixin import ClaimResponseConverterMixin


logger = logging.getLogger(__name__)


class BundleConverter(AbstractAIBundleConverter):
    ai_input_converter = AiConverter()
    ai_output_converter = ClaimResponseConverter()

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

    def bundle_ai_output(self, evaluation_output: List[EvaluationResult], invalid_claims: List[Tuple[dict, str]]):
        bundle = Bundle.construct()
        bundle.type = "collection"
        evaluated = self._build_evaluated_claims_entries(evaluation_output)
        invalid_claim = self.__build_invalid_claims_entries(invalid_claims)
        bundle.entry = evaluated + invalid_claim

        return bundle

    def _build_evaluated_claims_entries(self, evaluation_output):
        entries = []
        for claim, output in itertools.groupby(evaluation_output, lambda x: x.claim):
            entry = self.__build_evaluated_entry(
                claim, list(output), self.ai_output_converter.to_ai_output
            )
            entries.append(entry)
        return entries

    def __build_invalid_claims_entries(self, invalid_claims):
        entries = []
        for claim, rejection_reason in invalid_claims:
            entry = self.__build_evaluated_entry(
                claim, list(rejection_reason), self.ai_output_converter.claim_response_error
            )
            entries.append(entry)
        return entries

    def __build_evaluated_entry(self, claim, output, resource_creation_method):
        claim_fhir_response = resource_creation_method(claim, output)
        entry = BundleEntry(**{
            'fullUrl': ClaimAiConfig.claim_response_url + '/' + str(claim['id']),
            'resource': claim_fhir_response
        })
        return entry
