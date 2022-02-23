import numpy as np
import pandas

from claim_ai.evaluation.preprocessors.abstract_preprocessor import AbstractAiInputDataFramePreprocessor


class AiInputV1Preprocessor(AbstractAiInputDataFramePreprocessor):
    def sanity_check(self, input_bundle):
        exclusion_cnd3 = (input_bundle['ClaimAdminUUID'].isnull()) | \
                         (input_bundle['VisitType'].isnull())

        exclusion_cnd5 = (input_bundle['DateFrom'] < self.FIRST_DATE) | \
                         (input_bundle['DOB'] > input_bundle['DateClaimed']) | \
                         (input_bundle['DateClaimed'] < self.FIRST_DATE) | \
                         (input_bundle['DateClaimed'] < input_bundle['DateFrom'])

        conditions = [
            exclusion_cnd3,
            exclusion_cnd5,
            ~(exclusion_cnd3 & exclusion_cnd5)
        ]

        values = ['Condition3', 'Condition5', 'Clean data']
        input_bundle['SanityCheck'] = np.select(conditions, values)
        input_bundle.rename(columns={'ItemUUID': 'ItemID',
                              'ClaimUUID': 'ClaimID', 'ClaimAdminUUID': 'ClaimAdminId',
                              'HFUUID': 'HFID', 'LocationUUID': 'LocationId', 'HFLocationUUID': 'HFLocationId',
                              'InsureeUUID': 'InsureeID', 'FamilyUUID': 'FamilyID'}, inplace=True)

        selected_cols = ['ItemID', 'ClaimID', 'ClaimAdminId', 'HFID',
                         'LocationId', 'HFLocationId', 'InsureeID', 'FamilyID', 'ICDID', 'ICDID1',
                         'QtyProvided', 'PriceAsked', 'ItemPrice',
                         'ItemFrequency', 'ItemPatCat', 'ItemLevel',
                         'DateFrom', 'DateTo', 'DateClaimed', 'DOB',
                         'VisitType', 'HFLevel', 'HFCareType',
                         'Gender', 'ItemServiceType']

        index = input_bundle['SanityCheck'] == 'Clean data'
        clean_input = input_bundle.loc[index, selected_cols].copy()
        return index, clean_input

    def patch_data(self, clean_input):
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
        cat_features = ['ItemLevel', 'VisitType', 'HFLevel', 'HFCareType', 'Gender', 'ItemServiceType']

        encoded_input = clean_input.copy()
        transform_input = clean_input[cat_features]
        try:
            encoded_input[cat_features] = self.encoder.transform(transform_input)
            return encoded_input
        except Exception as x:
            print('Exception: ', x)
            return encoded_input

    def normalize_input(self, encoded_input):
        selected_cols = ['ItemID', 'ClaimID', 'ClaimAdminId', 'HFID',
                         'LocationId', 'HFLocationId', 'InsureeID', 'FamilyID', 'ICDID', 'ICDID1',
                         'QtyProvided', 'PriceAsked', 'ItemPrice',
                         'ItemFrequency', 'ItemPatCat', 'ItemLevel',
                         'DateFrom', 'DateTo', 'DateClaimed', 'Age',
                         'VisitType', 'HFLevel', 'HFCareType',
                         'Gender', 'ItemServiceType']

        # Normalization
        # TODO: Scaler raises exception if input DF is empty
        return pandas.DataFrame(data=self.scaler.transform(encoded_input[selected_cols]), columns=selected_cols)
