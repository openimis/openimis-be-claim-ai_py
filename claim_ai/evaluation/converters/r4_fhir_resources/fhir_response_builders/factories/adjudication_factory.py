from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders import \
    AiInputModelAdjudicationBuilder, ClaimProvisionAdjudicationBuilder
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.factories.generic import \
    GenericBuilderFactory


class AdjudicationBuilderFactory(GenericBuilderFactory):
    @property
    def _init_kwargs(self):
        return {}

    REGISTERED_BUILDERS = {
        'AiInputModel': AiInputModelAdjudicationBuilder,
        'ClaimProvisionEvaluationResult': ClaimProvisionAdjudicationBuilder
    }
