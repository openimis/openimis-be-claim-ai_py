import json
import os
from datetime import datetime

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status

from api_fhir_r4.tests import GenericFhirAPITestMixin
from api_fhir_r4.tests.test_api_claim_contained import ClaimAPIContainedTestBaseMixin
from api_fhir_r4.configurations import GeneralConfiguration
from claim_ai.models import ClaimBundleEvaluation
from claim_ai.tests.r4_fhir_resources.api.test_api_claim_bundle import ClaimBundleAPITests


class ClaimBundleAPITests(ClaimBundleAPITests):
    # Using claim instead of bundle
    resource_uri = 'claim_evaluation/'

    # Bundle will still be created but it's id should be same as claim id
    _TEST_BUNDLE_UUID = ClaimBundleAPITests._TEST_CLAIM_UUID

    def _load_request_data(self):
        base = super(ClaimBundleAPITests, self)._load_request_data()
        return base['entry'][0]['resource']

    def _load_response_data(self):
        base = super(ClaimBundleAPITests, self)._load_response_data()
        return base['entry'][0]['resource']

    def _get_expected_identifier_from_create_response(self):
        return self._test_request_data['id']

    def test_get_should_return_200_claim_with_contained(self):
        super(ClaimBundleAPITests, self).test_get_should_return_200_claim_with_contained()
