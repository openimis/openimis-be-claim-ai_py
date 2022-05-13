import json
import os
from datetime import datetime
from unittest import mock
from unittest.mock import PropertyMock, MagicMock

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from sklearn import preprocessing

from api_fhir_r4.tests import GenericFhirAPITestMixin
from api_fhir_r4.tests.test_api_claim_contained import ClaimAPIContainedTestBaseMixin
from api_fhir_r4.configurations import GeneralConfiguration
from claim_ai.models import ClaimBundleEvaluation


def get_base_url():
    module = 'claim_ai'
    root = settings.SITE_ROOT() or '/'
    base_url = root if root.endswith('/') else F"{root}/"
    return F"{base_url}{module}/" if base_url.startswith('/') else F"/{base_url}{module}/"


class ClaimBundleAPITests(ClaimAPIContainedTestBaseMixin, GenericFhirAPITestMixin, APITestCase):
    _TEST_BUNDLE_UUID = "AAAAEB75-85F1-4030-AB84-C767E5DCAAAA"
    _TEST_CLAIM_UUID = "AAAA1E5A-C491-4468-A540-567E569BAAAA"

    base_url = get_base_url()
    resource_uri = 'claim_bundle_evaluation/'

    @property
    def resource_url(self):
        return self.base_url + self.resource_uri
    # resource_url = base_url + resource_uri

    _test_json_request_path = "/api/test/test_bundle_payload.json"
    _test_json_response_path = "/api/test/test_bundle_response.json"

    def setUp(self):
        self._test_request_data = self._load_request_data()
        self._test_response_data = self._load_response_data()
        self._test_request_data_credentials = {
            "username": "TestUserTest2",
            "password": "TestPasswordTest2"
        }

        self._TEST_USER = self.get_or_create_user_api()

        self._GET_RESOURCE_URL = F"{self.resource_url}{self._TEST_BUNDLE_UUID}/"
        self._CREATE_RESOURCE_URL = self.resource_url
        self.create_dependencies()

    def test_get_should_required_login(self):
        url = self._GET_RESOURCE_URL
        response = self.client.get(url, data=None, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.encoder",
                new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.scaler",
                new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.stored_resource_evaluation.AiPredictor.model", new_callable=PropertyMock)
    def test_post_should_create_correctly(self, model_mock, mocked_scaler, mocked_encoder):
        mocked_scaler.return_value = MagicMock()
        mocked_scaler.return_value.transform = self.mocked_scaler

        mocked_encoder.return_value = MagicMock()
        mocked_encoder.return_value.transform = self.mocked_encoder

        model_mock.return_value = MagicMock()
        model_mock.return_value.predict = self.mocked_predict

        create_response = self._create_from_test_data()
        response_json = create_response.json()
        # Check if was created
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        # Check response
        self.assert_response(response_json)
        # Check if contained resources were created
        self._assert_contained()

    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.encoder",
                new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.scaler",
                new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.stored_resource_evaluation.AiPredictor.model", new_callable=PropertyMock)
    def test_get_should_return_200_claim_with_contained(self, model_mock, mocked_scaler, mocked_encoder):
        mocked_scaler.return_value = MagicMock()
        mocked_scaler.return_value.transform = self.mocked_scaler

        mocked_encoder.return_value = MagicMock()
        mocked_encoder.return_value.transform = self.mocked_encoder

        model_mock.return_value = MagicMock()
        model_mock.return_value.predict = self.mocked_predict
        self._create_from_test_data()
        response = self._send_request_for_evaluation_result()
        # Check if resource was received
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check resource content
        self.assert_adjudication_bundle(response)

    def assert_response(self, response_json):
        self.assertEqual(response_json['resourceType'], 'Bundle')

        evaluation_bundle_id = response_json['identifier']['value']
        database_entry = ClaimBundleEvaluation.objects.filter(evaluation_hash=evaluation_bundle_id)

        # ID of bundle should be the same as ID of response bundle
        self.assertEqual(evaluation_bundle_id, self._get_expected_identifier_from_create_response())
        self.assertTrue(database_entry.exists())

        db_claims_evaluation = database_entry.get().claims.all()
        db_claim_ids = [str(claim_eval.claim.uuid).lower() for claim_eval in db_claims_evaluation]

        claim_responses = [c['resource']for c in response_json['entry']]
        response_claims_ids = [c['id'].lower() for c in claim_responses]

        # Single claim sent for evaluation
        self.assertEqual(len(claim_responses), 1)
        self.assertListEqual(db_claim_ids, response_claims_ids)

    def _get_headers(self, **extra):
        request_params = {
            'path': GeneralConfiguration.get_base_url() + 'login/',
            'data': self._test_request_data_credentials,
            'format': 'json'
        }

        json_response = self.client.post(**request_params).json()

        return {
            "Content-Type": "application/json",
            "HTTP_AUTHORIZATION": f"Bearer {json_response['token']}",
            **extra
        }

    def assert_adjudication_bundle(self, response):
        actual_bundle = response.json()
        expected_bundle = self._test_response_data
        self.assertEqual(expected_bundle, actual_bundle)

    def _load_request_data(self):
        payload = self.__read_file_from_path(self._test_json_request_path)
        return json.loads(self._adjust_request_string(payload))

    def _load_response_data(self):
        payload = self.__read_file_from_path(self._test_json_response_path)
        return json.loads(self._adjust_expected_response_string(payload))

    def __read_file_from_path(self, filename):
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return open(dir_path + filename).read()

    def _assert_contained(self):
        self.assert_hf_created()
        self.assert_insuree_created()
        self.assert_claim_admin_created()
        self.assert_items_created()

    def _create_from_test_data(self):
        headers = self._get_headers()
        url = self.resource_url + '?wait_for_evaluation=True'
        response = self.client.post(url, data=self._test_request_data, format='json', **headers)
        return response

    def _send_request_for_evaluation_result(self):
        headers = self._get_headers()
        url = self._GET_RESOURCE_URL
        return self.client.get(url, data=None, format='json', **headers)

    def _adjust_request_string(self, payload):
        return payload

    def _adjust_expected_response_string(self, output_payload):
        return output_payload.replace("CREATED_DATE", datetime.now().date().strftime("%Y-%m-%d"))

    def _get_expected_identifier_from_create_response(self):
        return self._test_request_data['identifier']['value']

    @classmethod
    def mocked_scaler(cls, df):
        scaler = preprocessing.MinMaxScaler()
        return scaler.fit_transform(df)

    @classmethod
    def mocked_predict(cls, input_):
        return [1, 0]

    @classmethod
    def mocked_encoder(cls, df_categorical):
        le = preprocessing.LabelEncoder()
        for column in list(df_categorical.columns):
            df_categorical[column] = le.fit_transform(df_categorical[column])
        return df_categorical
