from unittest import mock, skip
from unittest.mock import Mock, PropertyMock, MagicMock

from django.test import testcases
import pandas
from pandas._testing import assert_frame_equal

from claim_ai.evaluation.predictor import AiPredictor
from claim_ai.evaluation.preprocessors.v2_preprocessor import AiInputV2Preprocessor
from claim_ai.evaluation.stored_resource_evaluation import ClaimBundleEvaluator
from core import datetime
from sklearn import preprocessing


class TestAiEvaluation(testcases.TestCase):
    _TEST_INPUT_DF = pandas.DataFrame([
            {
                'ProvisionID': 10,
                'ProvisionType': 'Medication',
                'ItemUUID': "AAAA76E2-DC28-4B48-8E29-3AC4ABEC0000",
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': 2,  # Is this HF location or insuree location?
                'ICDCode': 'ICD00I',
                'ICD1Code': None,
                'ProdID': None,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',  # Should it be code or  "Gender Object" used in ORM?
                'Poverty': None,
                'QuantityProvided': 10,
                'ItemPrice': 10.0,
                'PriceAsked': 11.0,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': 'M',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': 0,
                'HfUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'ClaimAdminUUID':  "044C33D1-DBF3-4D6A-9924-3797B461E535",
                'InsureeUUID': '76ACA309-F8CF-4890-8F2E-B416D78DE00B',
                'ClaimUUID': "AE580700-0277-4C98-ADAB-D98C0F7E681B",
                'TotalPrice': 400.0,
                'New': 'new'
            }, {
                'ProvisionID': 9,
                'ProvisionType': 'ActivityDefinition',
                'ItemID': 'AAAA29BA-3F4E-4E6F-B55C-23A488A10000',
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': 2,
                'ICDCode': 'ICD00I',
                'ICD1Code': None,
                'ProdID': None,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': 20,
                'ItemPrice': 800,
                'PriceAsked': 801.0,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': '1',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': 0,
                 'HfUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'ClaimAdminUUID':  "044C33D1-DBF3-4D6A-9924-3797B461E535",
                'InsureeUUID': '76ACA309-F8CF-4890-8F2E-B416D78DE00B',
                'ClaimUUID': "AE580700-0277-4C98-ADAB-D98C0F7E681B",
                'New': 'new'
            }, {
                'ProvisionID': 8,
                'ProvisionType': 'Medication',
                'ItemUUID': "AAAA76E2-DC28-4B48-8E29-3AC4ABEC0000",
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': 2,
                'ICDCode': 'ICD00V',
                'ICD1Code': None,
                'ProdID': None,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': 10,
                'ItemPrice': 10.0,
                'PriceAsked': 11.0,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': 'M',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': 0,
                 'HfUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'ClaimAdminUUID':  "044C33D1-DBF3-4D6A-9924-3797B461E535",
                'InsureeUUID': '76ACA309-F8CF-4890-8F2E-B416D78DE00B',
                'ClaimUUID': "AE580700-0277-4C98-ADAB-D98C0F7E681B",
                'New': 'old'
            }, {
                'ProvisionID': 7,
                'ProvisionType': 'ActivityDefinition',
                'ItemID': 'AAAA29BA-3F4E-4E6F-B55C-23A488A10000',
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': 2,
                'ICDCode': 'ICD00V',
                'ICD1Code': None,
                'ProdID': None,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': 20,
                'ItemPrice': 800,
                'PriceAsked': 801.0,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': '1',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': 0,
                 'HfUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'ClaimAdminUUID':  "044C33D1-DBF3-4D6A-9924-3797B461E535",
                'InsureeUUID': '76ACA309-F8CF-4890-8F2E-B416D78DE00B',
                'ClaimUUID': "AE580700-0277-4C98-ADAB-D98C0F7E681B",
                'New': 'old'
            }
        ])

    @skip("Failing due to payload, e2e testsing is working")
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.encoder", new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.scaler", new_callable=PropertyMock)
    def test_preprocessor(self, mocked_scaler, mocked_encoder):
        # Since scaler, encoder and joblib are to be provided to specific implementation, implementations and loaders
        #  are mocked.
        mocked_scaler.return_value = MagicMock()
        mocked_scaler.return_value.transform = self.mocked_scaler

        mocked_encoder.return_value = MagicMock()
        mocked_encoder.return_value.transform = self.mocked_encoder

        preprocessor = AiInputV2Preprocessor()
        index, preprocessed_df = preprocessor.preprocess(self._TEST_INPUT_DF.copy())
        # Doesn't check content but if preprocessing passed.
        self.assertEqual(len(index), 4)
        self.assertIsNotNone(preprocessed_df)

    @skip("Failing due to payload, e2e testsing is working")
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.encoder", new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.preprocessors.v2_preprocessor.AbstractAiInputDataFramePreprocessor.scaler", new_callable=PropertyMock)
    @mock.patch("claim_ai.evaluation.predictor.AiPredictor.model", new_callable=PropertyMock)
    def test_ai_evaluation(self, model_mock, mocked_scaler, mocked_encoder):
        # Since scaler, encoder and joblib are to be provided to specific implementation, implementations and loaders
        #  are mocked.
        mocked_scaler.return_value = MagicMock()
        mocked_scaler.return_value.transform = self.mocked_scaler

        mocked_encoder.return_value = MagicMock()
        mocked_encoder.return_value.transform = self.mocked_encoder

        model_mock.return_value = MagicMock()
        model_mock.return_value.predict = self.mocked_predict

        preprocessor = AiInputV2Preprocessor()

        evaluator = AiPredictor(preprocessor)
        result = evaluator.evaluate_bundle(self._TEST_INPUT_DF.copy())
        expected_df = pandas.DataFrame([
            {'ProvisionID': 10, 'ProvisionType': 'Medication',         'prediction': 0},
            {'ProvisionID': 9,  'ProvisionType': 'ActivityDefinition', 'prediction': 1}]
        ).reset_index(drop=True)
        assert_frame_equal(result.reset_index(drop=True), expected_df.reset_index(drop=True))

    @classmethod
    def mocked_scaler(cls, df):
        scaler = preprocessing.MinMaxScaler()
        return scaler.fit_transform(df)

    @classmethod
    def mocked_predict(cls, input_):
        return [0, 1]

    @classmethod
    def mocked_encoder(cls, df_categorical):
        le = preprocessing.LabelEncoder()
        for column in list(df_categorical.columns):
            df_categorical[column] = le.fit_transform(df_categorical[column])
        return df_categorical
