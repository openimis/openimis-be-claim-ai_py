from django.db import transaction

from claim_ai.evaluation.bundle_evaluation import ClaimBundleEvaluator, ClaimBundleEvaluationOutputFormat
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult, ClaimProvisionEvaluationResult


class ClaimBundleEvaluationManager:
    def create_idle_evaluation_bundle(self, claims, evaluation_bundle_hash=None):
        return self._create_evaluation_entries_in_db(claims, evaluation_bundle_hash)

    def query_claims_for_evaluation(self, claims_with_contained_data):
        # TODO: Use shared task to call evaluation for bundle
        fhir_bundle = self.__wrap_claims_in_bundle(claims_with_contained_data)
        return ClaimBundleEvaluator.evaluate_bundle(
            fhir_bundle,
            output_format=ClaimBundleEvaluationOutputFormat.EVALUATION_RESULT)

    @transaction.atomic
    def _create_evaluation_entries_in_db(self, claims, evaluation_bundle_hash=None):
        bundle_eval_model = ClaimBundleEvaluation(evaluation_hash=evaluation_bundle_hash)
        bundle_eval_model.save()

        for claim in claims:
            self._create_empty_claim_evaluation_result(claim, bundle_eval_model)
        return bundle_eval_model

    def _create_empty_claim_evaluation_result(self, claim, bundle_eval_model):
        claim_evaluation_information = SingleClaimEvaluationResult(
            claim=claim, bundle_evaluation=bundle_eval_model)

        claim_evaluation_information.save()
        ClaimProvisionEvaluationResult.build_base_claim_provisions_evaluation(
            claim_evaluation_information, save=True)

    def __wrap_claims_in_bundle(self, claims):
        entries = [{'resource': claim} for claim in claims]
        return {'entry': entries}
