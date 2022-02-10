from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders import \
    EvaluationResultClaimResponseBuilder, ClaimEvaluationResultClaimResponseBuilder
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.factories.generic import \
    GenericBuilderFactory


class ClaimResponseBuilderFactory(GenericBuilderFactory):
    @property
    def _init_kwargs(self):
        from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import AdjudicationBuilderFactory
        return {'adjudication_builder_factory': AdjudicationBuilderFactory()}

    REGISTERED_BUILDERS = {
        'dict': EvaluationResultClaimResponseBuilder,
        'SingleClaimEvaluationResult': ClaimEvaluationResultClaimResponseBuilder
    }
