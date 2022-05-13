import itertools
import uuid
from gevent.pool import Pool

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

from claim.models import Claim, ClaimItem, ClaimService
from core.models import HistoryModel


class ClaimBundleEvaluation(HistoryModel):

    class BundleEvaluationStatus(models.IntegerChoices):
        IDLE = 0
        STARTED = 1
        FINISHED = 2
        FAILED = -1

    evaluation_hash = \
        models.CharField(max_length=36, default=uuid.uuid4, unique=True, null=False)
    status = \
        models.IntegerField(choices=BundleEvaluationStatus.choices, default=BundleEvaluationStatus.IDLE, null=False)
    evaluation_finish_time = models.TextField(null=True)


class SingleClaimEvaluationResult(models.Model):
    # One to many without direct reference in claim object
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='ai_evaluations', null=False)
    bundle_evaluation = models.ForeignKey(ClaimBundleEvaluation, on_delete=models.CASCADE, related_name='claims')


class ClaimProvisionEvaluationResult(models.Model):
    class ProvisionEvaluationResult(models.IntegerChoices):
        UNDEFINED = -1
        ACCEPTED = 0
        REJECTED = 1

    content_type_choices = \
        models.Q(app_label='claim', model='ClaimItem') \
        | models.Q(app_label='claim', model='ClaimService')

    content_type = \
        models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, limit_choices_to=content_type_choices)

    claim_provision = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'claim_provision')
    evaluation = \
        models.IntegerField(choices=ProvisionEvaluationResult.choices, default=ProvisionEvaluationResult.UNDEFINED)

    claim_evaluation = \
        models.ForeignKey(SingleClaimEvaluationResult, on_delete=models.CASCADE, related_name='evaluated_items')

    @classmethod
    def build_base_claim_provisions_evaluation(
            cls, claim_evaluation_information: SingleClaimEvaluationResult, save: bool = False):
        claim = claim_evaluation_information.claim
        items = claim.items.filter(validity_to__isnull=True).all()
        services = claim.services.filter(validity_to__isnull=True).all()

        item_ct = ContentType.objects.get_for_model(ClaimItem)
        service_ct = ContentType.objects.get_for_model(ClaimService)
        pool = Pool(5)
        result = pool.imap(cls._build_evaluation_result,
                           [(item_ct, item, claim_evaluation_information) for item in items])
        result2 = pool.imap(cls._build_evaluation_result,
                            [(service_ct, service, claim_evaluation_information) for service in services])

        out = itertools.chain(result, result2)
        #x = [a for a in out]
        if save:
            [x.save() for x in out]

        return out

    @classmethod
    def _build_evaluation_result(cls, input_):
        provision_type, item, claim_evaluation_info = input_
        return ClaimProvisionEvaluationResult(
            content_type=provision_type,
            claim_provision=item.pk,
            claim_evaluation=claim_evaluation_info
        )
