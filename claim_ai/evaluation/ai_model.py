import os
import sys
from pathlib import Path

import numpy as np
from datetime import datetime

import pandas
import pickle
import joblib

from claim_ai.apps import ClaimAiConfig


class AiModel:

    FIRST_DATE = datetime.strptime(ClaimAiConfig.first_date, ClaimAiConfig.date_format)

    def __init__(self):
        self.model = self._load_model()
        self.encoder = self._load_encoder()
        self.scaler = self._load_scaler()

    def evaluate_bundle(self, input_bundle):
        index, clean_input = self.sanity_check(input_bundle)
        clean_input = self.fill_missing_variables(clean_input)
        clean_input = self.convert_variables(clean_input)
        clean_input = self.normalize_input(clean_input)
        return index, self.predict(clean_input)

    def sanity_check(self, input):
        exclusion_cnd3 = (input['ClaimAdminUUID'].isnull()) | \
                         (input['VisitType'].isnull())

        exclusion_cnd5 =   (input['DateFrom'] < self.FIRST_DATE) | \
                           (input['DOB'] > input['DateClaimed']) | \
                           (input['DateClaimed'] < self.FIRST_DATE) | \
                           (input['DateClaimed'] < input['DateFrom'])

        conditions = [
            exclusion_cnd3,
            exclusion_cnd5,
            ~(exclusion_cnd3 & exclusion_cnd5)
        ]

        values = ['Condition3', 'Condition5', 'Clean data']
        input['SanityCheck'] = np.select(conditions, values)
        selected_cols = ['ItemUUID', 'ClaimUUID', 'ClaimAdminUUID', 'HFUUID', 'LocationUUID', 'HFLocationUUID',
                         'InsureeUUID',
                         'FamilyUUID', 'ICDID', 'ICDID1',
                         'QtyProvided', 'PriceAsked', 'ItemPrice',
                         'ItemFrequency', 'ItemPatCat', 'ItemLevel',
                         'DateFrom', 'DateTo', 'DateClaimed', 'DOB',
                         'VisitType', 'HFLevel', 'HFCareType',
                         'Gender', 'ItemServiceType']

        index = input['SanityCheck'] == 'Clean data'
        clean_input = input.loc[index, selected_cols].copy()
        return index, clean_input

    def fill_missing_variables(self, clean_input):
        index = clean_input['ICDID1'].isnull()
        clean_input.loc[index, 'ICDID1'] = clean_input.loc[index, 'ICDID']
        return clean_input
    
    def convert_variables(self, clean_input):
        clean_input.loc[:, 'Age'] = (clean_input['DateFrom'] - clean_input['DOB']).dt.days / 365.25
        # # Drop DOB column as no longer necessary
        clean_input.drop(['DOB'], axis=1, inplace=True)

        # # Convert to number of days the columns, same date from configuration
        date_cols = ['DateFrom', 'DateTo', 'DateClaimed']
        for i in date_cols:
            clean_input[i] = (clean_input[i] - self.FIRST_DATE).dt.days

        # 4.2 Convert text or other types features to numeric ones
        cat_features = ['ItemUUID', 'ClaimUUID', 'ClaimAdminUUID', 'HFUUID',
                        'LocationUUID', 'HFLocationUUID', 'InsureeUUID',
                        'FamilyUUID', 'ItemLevel', 'VisitType', 'HFLevel',
                        'HFCareType', 'Gender', 'ItemServiceType']

        encoded_input = clean_input.copy()
        transform_input = clean_input[cat_features]
        try:
            encoded_input[cat_features] = self.encoder.transform(transform_input)
            return encoded_input
        except Exception as x:
            print('Exception: ', x)
            return encoded_input

    def normalize_input(self, encoded_input):
        selected_cols = ['ItemUUID', 'ClaimUUID', 'ClaimAdminUUID', 'HFUUID', 'LocationUUID', 'HFLocationUUID',
                         'InsureeUUID',
                         'FamilyUUID', 'ICDID', 'ICDID1',
                         'QtyProvided', 'PriceAsked', 'ItemPrice',
                         'ItemFrequency', 'ItemPatCat', 'ItemLevel',
                         'DateFrom', 'DateTo', 'DateClaimed', 'Age',
                         'VisitType', 'HFLevel', 'HFCareType',
                         'Gender', 'ItemServiceType']

        # Normalization
        return pandas.DataFrame(data=self.scaler.transform(encoded_input), columns=selected_cols)

    def predict(self, normalized_input):
        return self.model.predict(normalized_input)

    def _load_model(self):
        if not ClaimAiConfig.ai_model_file:
            raise FileNotFoundError("Path to AI model file not found in config")
        return self.__load_from_file(ClaimAiConfig.ai_model_file, joblib.load)

    def _load_encoder(self):
        return self.__load_from_file(ClaimAiConfig.ai_encoder_file)

    def _load_scaler(self):
        return self.__load_from_file(ClaimAiConfig.ai_scaler_file)

    def __load_from_file(self, path, load_func=pickle.load):
        isabs = os.path.isabs(path)
        if not isabs:
            abs_path = Path(__file__).absolute().parent.parent.parent  # path to claim_ai module folder
            path = F'{abs_path}/{path}'

        with open(path, 'rb') as f:
            return load_func(f)

