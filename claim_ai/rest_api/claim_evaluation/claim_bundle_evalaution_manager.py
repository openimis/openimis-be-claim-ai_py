from django.db import transaction

from claim_ai.evaluation.stored_resource_evaluation import ClaimBundleEvaluator
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult, ClaimProvisionEvaluationResult


class ClaimBundleEvaluationManager:
    def create_idle_evaluation_bundle(self, claims, evaluation_bundle_hash=None):
        return self._create_evaluation_entries_in_db(claims, evaluation_bundle_hash)

    def query_claims_for_evaluation(self, claim_evaluation_bundle: ClaimBundleEvaluation):
        # TODO: Use shared task to call evaluation for bundle
        return self.evaluate_bundle(claim_evaluation_bundle)

    def evaluate_bundle(self, claim_evaluation_bundle: ClaimBundleEvaluation):
        return ClaimBundleEvaluator.evaluate_bundle(claim_evaluation_bundle)

    @transaction.atomic
    def _create_evaluation_entries_in_db(self, claims, evaluation_bundle_hash=None):
        kwargs = {'evaluation_hash': evaluation_bundle_hash} if evaluation_bundle_hash else {}
        bundle_eval_model = ClaimBundleEvaluation(**kwargs)
        bundle_eval_model.save()

        for claim in claims:
            self._create_empty_claim_evaluation_result(claim, bundle_eval_model)

        bundle_eval_model = ClaimBundleEvaluation.objects.get(id=bundle_eval_model.id)
        return bundle_eval_model

    def _create_empty_claim_evaluation_result(self, claim, bundle_eval_model):
        claim_evaluation_information = SingleClaimEvaluationResult(
            claim=claim, bundle_evaluation=bundle_eval_model)

        claim_evaluation_information.save()
        ClaimProvisionEvaluationResult.build_base_claim_provisions_evaluation(
            claim_evaluation_information, save=True)
