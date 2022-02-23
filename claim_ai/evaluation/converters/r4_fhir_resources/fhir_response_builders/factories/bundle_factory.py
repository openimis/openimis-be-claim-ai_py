from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders import \
    EvaluationResultClaimResponseBundleBuilder
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders.bundle_builders import \
    ClaimBundleEvaluationClaimResponseBundleBuilder
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.factories.generic import \
    GenericBuilderFactory


class BundleBuilderFactory(GenericBuilderFactory):
    @property
    def _init_kwargs(self):
        from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import ClaimResponseBuilderFactory
        return {'claim_response_factory': ClaimResponseBuilderFactory()}

    REGISTERED_BUILDERS = {
        'EvaluationResult': EvaluationResultClaimResponseBundleBuilder,
        'ClaimBundleEvaluation': ClaimBundleEvaluationClaimResponseBundleBuilder
    }
