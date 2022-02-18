from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from claim.models import ClaimItem, ClaimService
from claim_ai.evaluation.converters import BundleConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import ClaimResponseBuilderFactory
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders.bundle_builders import \
    ClaimBundleEvaluationClaimResponseBundleBuilder
from claim_ai.evaluation.input_models.stored_input_model import ClaimBundleEvaluationAiInputModel
from claim_ai.evaluation.predictor import AiPredictor
from claim_ai.evaluation.preprocessors.v2_preprocessor import AiInputV2Preprocessor
from claim_ai.models import ClaimBundleEvaluation, ClaimProvisionEvaluationResult


class ClaimBundleEvaluator:
    fhir_converter = ClaimBundleEvaluationClaimResponseBundleBuilder(ClaimResponseBuilderFactory())

    ai_model = AiPredictor(AiInputV2Preprocessor())
    _PROVISION_TYPES = {
        'ActivityDefinition': ClaimService,
        'Medication': ClaimItem
    }

    @classmethod
    def evaluate_bundle(cls, claim_bundle_evaluation: ClaimBundleEvaluation):
        ai_input = cls._build_input_dataframe(claim_bundle_evaluation)
        prediction = cls.ai_model.evaluate_bundle(ai_input)
        # AI input is made of new and historical, update is done using claim provision ID.
        claim_bundle_evaluation = cls._update_evaluation_with_prediction(claim_bundle_evaluation, prediction)
        return claim_bundle_evaluation

    @classmethod
    def _build_response_bundle(cls, evaluation_result):
        return cls.fhir_converter.build_valid(evaluation_result)

    @classmethod
    def _build_input_dataframe(cls, claim_bundle_evaluation: ClaimBundleEvaluation):
        input_ = ClaimBundleEvaluationAiInputModel(claim_bundle_evaluation)
        return input_.to_representation()

    @classmethod
    def _model_from_type(cls, param):
        type_ = cls._PROVISION_TYPES.get(param)
        if not type_:
            raise ValueError(F"Invalid ProvisionType: {param}. Accepted types are: {cls._PROVISION_TYPES.keys()}")
        return type_

    @classmethod
    @transaction.atomic
    def _update_evaluation_with_prediction(cls, claim_bundle_evaluation, prediction):
        evaluated_claims = claim_bundle_evaluation.claims.all()
        relevant_claim_provision_evaluation_results = \
            ClaimProvisionEvaluationResult \
                .objects \
                .filter(claim_evaluation__in=evaluated_claims) \
                .all() \
                .prefetch_related('claim_evaluation')

        for evaluation in prediction.to_dict(orient="records"):
            type_ = cls._model_from_type(evaluation['ProvisionType'])
            obj = type_.objects.get(id=evaluation['ProvisionID'])
            prediction = evaluation['prediction']

            provision_evaluation = relevant_claim_provision_evaluation_results \
                .get(content_type=ContentType.objects.get_for_model(type_).id, claim_provision=obj.id)

            provision_evaluation.evaluation = prediction
            provision_evaluation.save()

        claim_bundle_evaluation.status = ClaimBundleEvaluation.BundleEvaluationStatus.FINISHED
        user = claim_bundle_evaluation.user_created
        claim_bundle_evaluation.save(username=user.username)
        return claim_bundle_evaluation
