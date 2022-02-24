import datetime
import time
from typing import Tuple

import pandas as pd
import numpy as np

from claim_ai.evaluation.preprocessors.abstract_preprocessor import AbstractAiInputDataFramePreprocessor
# Note: This library cannot be used from forked source. It breaks on small DFs
from pandarallel import pandarallel


class AiInputV2Preprocessor(AbstractAiInputDataFramePreprocessor):
    nbworkers = 32

    CS_Rejected = 1
    CS_Entered = 2
    CS_Checked = 4
    CS_Valuated = 16

    RS_Idle = 1
    RS_NotSelected = 2
    RS_SelectedForReview = 4
    RS_Reviewed = 8
    RS_Bypassed = 16

    # RR:RejectionReason
    RR_Accepted = 0
    RR_RbyMO = -1

    # CIS:ClaimItemStatus
    CIS_Accepted = 1
    CIS_Rejected = 2

    def sanity_check(self, df_items: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        # Sanity Check
        # Definition of excluding conditions and add another column with the associated conditions

        # Incoherence in the date related fields
        # - items with DateFrom before 15-05-2016
        # - items with DOB before the DateClaimed
        # - items with DateClaimed before 15-05-2016
        # - items with DateClaimed before DateFrom
        exclusion_cnd5 = (df_items['DateFrom'] < datetime.datetime(2016, 5, 15)) | \
                         (df_items['DOB'] > df_items['DateFrom']) | \
                         (df_items['DateClaimed'] < datetime.datetime(2016, 5, 15)) | \
                         (df_items['DateClaimed'] < df_items['DateFrom'])

        # Incoherence between status and valuated price
        # exclusion_cnd6 = (df_items['RejectionReason'] == self.RR_RbyMO) & (df_items['PriceValuated'] > 0)

        # Check if ClaimAdminID has the same HFUUID as the ClaimHFUUID:
        # exclusion_cnd7 = (df_items['HFUUID']!=df_items['HfUUID'])

        conditions = [exclusion_cnd5, ~(exclusion_cnd5)]
        values = ['Condition5', 'Clean data']
        df_items['SanityCheck'] = np.select(conditions, values)
        result_df = self._create_aggregated_fields(df_items)
        selected_cols = [
            'ItemUUID', 'HFUUID', 'LocationId', 'ICDCode', 'ICD1Code',
            'Age', 'Gender', 'Poverty',
            'QuantityProvided', 'TotalPrice', 'DiffTotalPrice',
            'Duration', 'DurationClaimed',
            'ItemFrequency', 'ItemPatCat', 'ItemLevel', 'HFLevel', 'HFCareType', 'VisitType',
            'LastSameItem',
            'SameItemPerClaim', 'SameItemPerDay',
            'IsPackage',
            'ItemsPerDay', 'AmountPerDay',
            'ItemsPerWeek', 'AmountPerWeek',
            'ItemsPerMonth', 'AmountPerMonth',
            'ItemsPerQuarter', 'AmountPerQuarter',
            'ItemsPerYear', 'AmountPerYear',
            'ICDItemProba', 'ICDTotalAmountAsked',
            'ICDGenderProba', 'ItemGenderProba',
            'ICDAge_q', 'ItemAge_q', 'DiffPrice'
        ]
        index = result_df['New'] != 'old'
        df_new = result_df[index].copy()
        df_new.sort_values(by=['New'], ascending=True, inplace=True)
        df_new = result_df.loc[index, selected_cols]
        return index, df_new

    def convert_variables(self, df_items: pd.DataFrame) -> pd.DataFrame:
        cat_features = ['ItemUUID', 'HFUUID', 'ItemLevel', 'VisitType', 'HFLevel', 'Gender',
                        'HFCareType', 'ICDCode', 'ICD1Code']
        df_data_encoded = df_items.copy()
        categorical = df_data_encoded[cat_features]
        df_data_encoded[cat_features] = self.encoder.transform(categorical)
        return df_data_encoded

    def normalize_input(self, df_items: pd.DataFrame) -> pd.DataFrame:
        selected_cols = ['ItemUUID', 'HFUUID', 'LocationId', 'ICDCode', 'ICD1Code',
                         'Age', 'Gender', 'Poverty',
                         'QuantityProvided', 'TotalPrice', 'DiffTotalPrice',
                         'Duration', 'DurationClaimed',
                         'ItemFrequency', 'ItemPatCat', 'ItemLevel', 'HFLevel', 'HFCareType', 'VisitType',
                         'LastSameItem',
                         'SameItemPerClaim', 'SameItemPerDay',
                         'IsPackage',
                         'ItemsPerDay', 'AmountPerDay',
                         'ItemsPerWeek', 'AmountPerWeek',
                         'ItemsPerMonth', 'AmountPerMonth',
                         'ItemsPerQuarter', 'AmountPerQuarter',
                         'ItemsPerYear', 'AmountPerYear',
                         'ICDItemProba', 'ICDTotalAmountAsked',
                         'ICDGenderProba', 'ItemGenderProba',
                         'ICDAge_q', 'ItemAge_q', 'DiffPrice']

        return pd.DataFrame(
            data=self.scaler.transform(df_items[selected_cols]), columns=selected_cols
        )

    def patch_data(self, df_items):
        index = df_items['ICD1Code'].isna()
        df_items.loc[index, 'ICD1Code'] = df_items.loc[index, 'ICDCode']
        df_items = df_items[df_items['VisitType'].notna()]
        # index = df_items['ProdID'].isnull()
        # df_items = df_items[~index]

        return df_items

    def _create_aggregated_fields(self, df_items):
        df_items['ItemPrice'] = df_items['ItemPrice'].apply(pd.to_numeric, errors='coerce')
        # Create TotalPrice and TotalPriceAsked fields
        df_items['TotalPrice'] = df_items['QuantityProvided'] * df_items['ItemPrice']
        df_items['TotalPriceAsked'] = df_items['QuantityProvided'] * df_items['PriceAsked']
        df_items['DiffPrice'] = df_items['ItemPrice'] - df_items['PriceAsked']
        df_items['DiffTotalPrice'] = df_items['TotalPrice'] - df_items['TotalPriceAsked']
        # Calculating the Age of a patient
        df_items.loc[:, 'Age'] = (df_items['DateFrom'] - df_items['DOB']).dt.total_seconds() / (60 * 60 * 24 * 365.25)

        # Drop DOB column as no longer necessary
        df_items.drop(['DOB'], axis=1, inplace=True)

        df_items['Duration'] = (
            (df_items['DateTo'] - df_items['DateFrom'])
        ).dt.days

        df_items['DurationClaimed'] = (df_items['DateClaimed'] - df_items['DateFrom']).dt.days
        df_items['Date'] = df_items['DateFrom']
        df_items['Date'] = df_items['Date'].apply(pd.to_datetime)

        df_items['DateFrom'] = (df_items['DateFrom'] - datetime.date(2016, 1, 1)).dt.days
        df_items['DateFrom'] = df_items['DateFrom'].apply(pd.to_numeric, errors='coerce')

        fields = ['ItemPrice']
        df_items[fields] = df_items[fields].apply(pd.to_numeric, errors='coerce')

        # LAST SAME ITEM
        # Computing the LastSameItem aggregated fiel:
        # the time lapse (in days) of the same item submitted for the same InsureeUUID
        # First sorting values wrt [‘InsureeUUID’,’ItemUUID’,’DateFrom’] in descending order and followed
        # by the computation of the difference in valued in the ‘DateFrom’ field
        df_items.sort_values(by=['InsureeUUID', 'ItemUUID', 'DateFrom'], ascending=True, inplace=True)
        df_items['LastSameItem'] = df_items.groupby(['InsureeUUID', 'ItemUUID'])['DateFrom'].diff()
        # The first item related to an InsureeiId will have no value (NaN) for the LastSameItem,
        # in this case the Nan will be replaced 4000.
        df_items['LastSameItem'].fillna(4000, inplace=True)

        # SameItemPerClaim and SameItemPerDay
        df_items['SameItemPerClaim'] = df_items.groupby(['InsureeUUID', 'ClaimUUID', 'ItemUUID'])['ItemUUID'].transform('count')
        df_items['SameItemPerDay'] = df_items.groupby(['InsureeUUID', 'DateFrom', 'ItemUUID'])['ItemUUID'].transform('count')

        df_items['ItemsPerClaim'] = df_items.groupby(['InsureeUUID', 'ClaimUUID'])['ItemUUID'].transform('count')
        df_items['AmountPerClaim'] = df_items.groupby(['InsureeUUID', 'DateFrom'])['TotalPrice'].transform(sum)
        df_items['AmountAskedPerClaim'] = df_items.groupby(['InsureeUUID', 'DateFrom'])['TotalPriceAsked'].transform(sum)

        # IsPackage
        # index = df_cleandata['Justification_reason']==11
        # iqr0 = df_items.loc[index,'AmountAskedPerClaim'].quantile(0.25)
        # print(iqr0)
        index_sup = df_items['AmountPerClaim'] > 3443.65
        df_items['IsPackage'] = 0
        df_items.loc[index_sup, 'IsPackage'] = 1
        # Items and amounts per day
        keys = ['InsureeUUID', 'DateFrom']
        df_items['ItemsPerDay'] = df_items.groupby(keys)['ItemUUID'].transform('count')
        df_items['AmountPerDay'] = df_items.groupby(keys)['TotalPrice'].transform(sum)

        df_items.set_index('Date')
        cols = ['Date', 'InsureeUUID', 'ItemsPerDay', 'AmountPerDay']
        temp = df_items[cols].drop_duplicates()

        result_df = df_items.copy()
        result_df.set_index('Date', inplace=True)

        temp.set_index('Date', inplace=True)
        temp = temp.sort_index()

        workers = min(self.nbworkers, len(result_df))
        feature_name = ['InsureeUUID', 'ItemsPerDay', 'AmountPerDay']
        new_feature = ['ItemsPerWeek', 'AmountPerWeek']
        result_df = self.aggregation_function(temp, result_df, '7D', feature_name, new_feature, workers)

        feature_name = ['InsureeUUID', 'ItemsPerDay', 'AmountPerDay']
        new_feature = ['ItemsPerMonth', 'AmountPerMonth']
        result_df = self.aggregation_function(temp, result_df, '30D', feature_name, new_feature, workers)

        feature_name = ['InsureeUUID', 'ItemsPerDay', 'AmountPerDay']
        new_feature = ['ItemsPerQuarter', 'AmountPerQuarter']
        result_df = self.aggregation_function(temp, result_df, '90D', feature_name, new_feature, workers)

        feature_name = ['InsureeUUID', 'ItemsPerDay', 'AmountPerDay']
        new_feature = ['ItemsPerYear', 'AmountPerYear']
        result_df = self.aggregation_function(temp, result_df, '365D', feature_name, new_feature, workers)

        # Aggregation related to HFUUID
        result_df['ICDTotalAmountAsked'] = result_df.groupby(['HFUUID', 'ICDCode'])['TotalPriceAsked'].transform('sum')
        keys = ['HFUUID', 'ICDCode', 'ItemUUID']
        result_df['ICDItemCount'] = result_df.groupby(keys)['ItemUUID'].transform('count')
        result_df['ICDCount'] = result_df.groupby(['HFUUID', 'ICDCode'])['ICDCode'].transform('count')
        result_df['ICDItemProba'] = result_df['ICDItemCount'] / result_df['ICDCount']
        # Items related to HF|ICD |Gender and HF|Item |Gender
        keys = ['HFUUID', 'ICDCode', 'Gender']
        result_df['ICDGenderCount'] = result_df.groupby(keys)['Gender'].transform('count')
        result_df['ICDGenderProba'] = result_df['ICDGenderCount'] / result_df['ICDCount']

        keys = ['HFUUID', 'ItemUUID', 'Gender']
        result_df['ItemGenderCount'] = result_df.groupby(keys)['Gender'].transform('count')
        keys = ['HFUUID', 'ItemUUID']
        result_df['ItemCount'] = result_df.groupby(keys)['ItemUUID'].transform('count')
        result_df['ItemGenderProba'] = result_df['ItemGenderCount'] / result_df['ItemCount']
        # Items related to HF|ICD |Age and HF|Item |Age
        keys = ['HFUUID', 'ICDCode', 'Age']
        result_df['ICDAge_q1'] = result_df[keys].groupby(['HFUUID', 'ICDCode']).transform(lambda x: x.quantile(0.10))
        result_df['ICDAge_q2'] = result_df[keys].groupby(['HFUUID', 'ICDCode']).transform(lambda x: x.quantile(0.90))
        index_age = (result_df['Age'] >= result_df['ICDAge_q1']) & (result_df['Age'] <= result_df['ICDAge_q2'])
        result_df.loc[index_age, 'ICDAge_q'] = 0
        result_df.loc[~index_age, 'ICDAge_q'] = 1

        keys = ['HFUUID', 'ItemUUID', 'Age']
        result_df['ItemAge_q1'] = result_df[keys].groupby(['HFUUID', 'ItemUUID']).transform(lambda x: x.quantile(0.10))
        result_df['ItemAge_q2'] = result_df[keys].groupby(['HFUUID', 'ItemUUID']).transform(lambda x: x.quantile(0.90))
        index_age = (result_df['Age'] >= result_df['ItemAge_q1']) & (result_df['Age'] <= result_df['ItemAge_q2'])
        result_df.loc[index_age, 'ItemAge_q'] = 0
        result_df.loc[~index_age, 'ItemAge_q'] = 1
        return result_df

    @classmethod
    def aggregation_function(cls, temp, result_df, window, feature_name, new_feature, nbworkers):
        pandarallel.initialize(nb_workers=nbworkers, verbose=0)  # Logs disabled

        grouped = temp.groupby(feature_name[0]).rolling(window)[feature_name[1]].parallel_apply(np.sum, raw=True)
        df_count = pd.DataFrame(grouped).reset_index()
        df_count = df_count.rename(columns={'level_0': feature_name[0], feature_name[1]: new_feature[0]})

        grouped = temp.groupby(feature_name[0]).rolling(window)[feature_name[2]].parallel_apply(np.sum, raw=True)
        df_amount = pd.DataFrame(grouped).reset_index()
        df_amount = df_amount.rename(columns={'level_0': feature_name[0], feature_name[2]: new_feature[1]})

        df_count = df_count.merge(df_amount, on=[feature_name[0], 'Date'])

        result_df = result_df.merge(df_count, on=[feature_name[0], 'Date'])
        return result_df
