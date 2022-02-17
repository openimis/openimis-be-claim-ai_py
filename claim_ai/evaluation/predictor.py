from datetime import datetime

import joblib

from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation.preprocessors.v1_preprocessor import AiInputV1Preprocessor
from claim_ai.utils import load_from_module_file


class AiPredictor:
    FIRST_DATE = datetime.strptime(ClaimAiConfig.first_date, ClaimAiConfig.date_format)

    def __init__(self, preprocessor=AiInputV1Preprocessor()):
        self.preprocessor = preprocessor

    def evaluate_bundle(self, input_bundle):
        index, clean_input = self.preprocessor.preprocess(input_bundle)
        provision_identifiers = input_bundle[['ProvisionID', 'ProvisionType']]
        prediction = self.predict(clean_input)
        # Drop index is required by identifiers as order is different.
        provision_identifiers = provision_identifiers.reset_index(drop=True)[index]
        provision_identifiers['prediction'] = prediction
        return provision_identifiers

    def predict(self, normalized_input):
        return self.model.predict(normalized_input)

    @property
    def model(self):
        if getattr(self, '__model', None) is None:
            my_data = self._load_model()
            self.__model = my_data
        return self.__model

    def _load_model(self):
        if not ClaimAiConfig.ai_model_file:
            raise FileNotFoundError("Path to AI model file not found in config")
        return load_from_module_file(ClaimAiConfig.ai_model_file, joblib.load)
