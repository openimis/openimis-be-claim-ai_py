from time import sleep

from celery import shared_task
from typing import Callable, Any

from claim_ai.evaluation.stored_resource_evaluation import ClaimBundleEvaluator
from claim_ai.models import ClaimBundleEvaluation


@shared_task
def background_bundle_evaluation(evaluation_hash):
    bundle = ClaimBundleEvaluation.objects.get(evaluation_hash=evaluation_hash)
    ClaimBundleEvaluator.evaluate_bundle(bundle)
