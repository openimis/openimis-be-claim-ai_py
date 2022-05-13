from django.urls import include, path
from rest_framework.routers import DefaultRouter
from openIMIS.openimisapps import *

from claim_ai.rest_api.claim_evaluation.views import ClaimBundleEvaluationViewSet, ClaimEvaluationViewSet

imis_modules = openimis_apps()

router = DefaultRouter()
router.register(r'claim_bundle_evaluation', ClaimBundleEvaluationViewSet, basename="bundle_evaluation")
router.register(r'claim_evaluation', ClaimEvaluationViewSet, basename="claim_evaluation")

urlpatterns = [
    path('', include(router.urls))
]
