from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from claim_ai.apps import ClaimAiConfig
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult
from claim_ai.rest_api.claim_evaluation.serializers import ClaimBundleEvaluationSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class BundleEvaluationPermissions(DjangoModelPermissions):
    permissions_get = ClaimAiConfig.evaluation_perms
    permissions_post = ClaimAiConfig.create_evaluation_perms
    permissions_put = ClaimAiConfig.update_evaluation_perms
    permissions_patch = ClaimAiConfig.update_evaluation_perms
    permissions_delete = ClaimAiConfig.delete_evaluation_perms

    def __init__(self):
        self.perms_map['GET'] = self.permissions_get
        self.perms_map['POST'] = self.permissions_post
        self.perms_map['PUT'] = self.permissions_put
        self.perms_map['PATCH'] = self.permissions_patch
        self.perms_map['DELETE'] = self.permissions_delete

    def get_required_permissions(self, method, model_cls):
        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        return self.perms_map[method]


class BaseEvaluationViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    authentication_classes = [CsrfExemptSessionAuthentication] + APIView.settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = [BundleEvaluationPermissions]
    serializer_class = ClaimBundleEvaluationSerializer

    def get_queryset(self):
        return ClaimBundleEvaluation.objects.filter(is_deleted=False)

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(BaseEvaluationViewSet, self).get_serializer(*args, **kwargs)


class ClaimBundleEvaluationViewSet(BaseEvaluationViewSet):
    lookup_field = 'evaluation_hash'

    def get_queryset(self):
        return ClaimBundleEvaluation.objects.filter(is_deleted=False)

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        wait_ = self.request.query_params.get('wait_for_evaluation', 'False').lower() == 'true'
        kwargs['wait'] = wait_
        return super(ClaimBundleEvaluationViewSet, self).get_serializer(*args, **kwargs)


class ClaimEvaluationViewSet(BaseEvaluationViewSet):
    lookup_field = 'claim__uuid'

    def get_queryset(self):
        return SingleClaimEvaluationResult.objects.all()

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        # If this argument is set - instead of using shared task evaluation is done during reuqest
        wait_ = self.request.query_params.get('wait_for_evaluation', 'False').lower() == 'true'
        kwargs['wait'] = wait_
        return super(ClaimEvaluationViewSet, self).get_serializer(*args, **kwargs)
