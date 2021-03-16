import os
from pathlib import Path

import numpy as np
from datetime import datetime

import pandas
import pickle
import joblib

from claim_ai.apps import ClaimAiConfig


class AiModel:

    def __init__(self):
        self.model = self._load_model()
        self.encoder = self._load_encoder()
        self.scaler = self._load_scaler()

    def evaluate_bundle(self, input_bundle):
        index, clean_input = self.sanity_check(input_bundle)
        clean_input = self.fill_missing_varaibles(clean_input)
        clean_input = self.convert_variables(clean_input)
        clean_input = self.normalize_input(clean_input)
        return index, self.predict(clean_input)

    def sanity_check(self, input):
        date_from = datetime(2016, 5, 15)
        date_claimed = datetime(2016, 5, 15)
        exclusion_cnd3 = (input['ClaimAdminUUID'].isnull()) | \
                         (input['VisitType'].isnull())

        exclusion_cnd5 =   (input['DateFrom'] < date_from) | \
                           (input['DOB'] > input['DateClaimed']) | \
                           (input['DateClaimed'] < date_claimed) | \
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

    def fill_missing_varaibles(self, clean_input):
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
            clean_input[i] = (clean_input[i] - datetime(2016, 1, 1)).dt.days

        # 4.2 Convert text or other types features to numeric ones
        cat_features = ['ItemUUID', 'ClaimUUID', 'ClaimAdminUUID', 'HFUUID',
                        'LocationUUID', 'HFLocationUUID', 'InsureeUUID',
                        'FamilyUUID', 'ItemLevel', 'VisitType', 'HFLevel',
                        'HFCareType', 'Gender', 'ItemServiceType']

        encoded_input = clean_input.copy()
        transform_input = clean_input[cat_features]
        try:
            # TODO: Should use encoded value instead of new categorization
            # encoded_input[cat_features] = self.encoder.transform(transform_input)
            encoded_input[cat_features] = clean_input[cat_features].astype('category')
            for f in cat_features:
                encoded_input[f] = encoded_input[f].cat.codes
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

