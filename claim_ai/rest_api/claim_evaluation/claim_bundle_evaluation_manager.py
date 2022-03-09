import logging

import time

from django.db import transaction, connection
from kombu.exceptions import OperationalError

from claim_ai.evaluation.stored_resource_evaluation import ClaimBundleEvaluator
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult, ClaimProvisionEvaluationResult
from claim_ai.tasks import background_bundle_evaluation

logger = logging.getLogger(__name__)


class CeleryWorkerError(Exception):
    pass


class ClaimBundleEvaluationManager:
    def __init__(self, user):
        self.user_manager = user

    def create_idle_evaluation_bundle(self, claims, evaluation_bundle_hash=None) -> ClaimBundleEvaluation:
        return self._create_evaluation_entries_in_db(claims, evaluation_bundle_hash)

    def query_claims_for_evaluation(self, claim_evaluation_bundle: ClaimBundleEvaluation):
        self._check_celery_status()
        try:
            background_bundle_evaluation.delay(evaluation_hash=claim_evaluation_bundle.evaluation_hash)
        except Exception as e:
            logger.error("Celery worker is not available, evaluation will be done in place.")

    def evaluate_bundle(self, claim_evaluation_bundle: ClaimBundleEvaluation):
        return ClaimBundleEvaluator.evaluate_bundle(claim_evaluation_bundle)

    @transaction.atomic
    def _create_evaluation_entries_in_db(self, claims, evaluation_bundle_hash=None) -> ClaimBundleEvaluation:
        kwargs = {'evaluation_hash': evaluation_bundle_hash} if evaluation_bundle_hash else {}
        bundle_eval_model = ClaimBundleEvaluation(**kwargs)
        bundle_eval_model.save(username=self.user_manager.username)

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

    def _evaluate_using_celery(self):
        pass

    def _check_celery_status(self):
        try:
            from openIMIS.celery import app as celery_app
            connection = celery_app.broker_connection().ensure_connection(max_retries=3)
            if not connection:
                raise CeleryWorkerError("Celery worker not found. Check if it's running.")
        except (IOError, OperationalError) as e:
            raise CeleryWorkerError(
                F"Celery connection has failed. Error: {e} \n Check RabbitMQ Server connection.")

