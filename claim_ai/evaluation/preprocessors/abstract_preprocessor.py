from abc import ABC, abstractmethod
from typing import Tuple

import pandas

from claim_ai.apps import ClaimAiConfig
from claim_ai.utils import load_from_assembly_file


class AbstractAiInputDataFramePreprocessor(ABC):
    # Properties are required to by lazy initialized as
    # instance of class is created during the module
    # installation. Installation breaks in case of missing
    # .pkl files required for model/scaler/encoder.
    @property
    def encoder(self):
        if getattr(self, '__encoder', None) is None:
            my_data = self._load_encoder()
            self.__encoder = my_data
        return self.__encoder

    @property
    def scaler(self):
        if getattr(self, '__scaler', None) is None:
            my_data = self._load_scaler()
            self.__scaler = my_data
        return self.__scaler

    def preprocess(self, input_bundle: pandas.DataFrame) -> Tuple[pandas.Series, pandas.DataFrame]:
        input_bundle = self.initial_preprocessing(input_bundle)
        index, clean_input = self.sanity_check(input_bundle)
        clean_input = self.patch_data(clean_input)
        clean_input = self.convert_variables(clean_input)
        clean_input = self.normalize_input(clean_input)
        clean_input = self.final_preprocessing(clean_input)
        return index, clean_input

    def _load_encoder(self):
        return load_from_assembly_file(ClaimAiConfig.ai_encoder_file)

    def _load_scaler(self):
        return load_from_assembly_file(ClaimAiConfig.ai_scaler_file)

    @abstractmethod
    def sanity_check(self, input_bundle: pandas.DataFrame) -> Tuple[pandas.Series, pandas.DataFrame]:
        """ Validate data over specified conditions. As output it returns two element tuple. First
        element is series with information regarding valid entries. Second is input_bundle dataframe
        with the invalid data filtered out.
        """
        pass

    @abstractmethod
    def convert_variables(self, clean_input: pandas.DataFrame) -> pandas.DataFrame:
        """
        Converts input_bundle columns to desired format, E.g. dates to days using an encoder.
        """
        pass

    @abstractmethod
    def normalize_input(self, clean_input: pandas.DataFrame) -> pandas.DataFrame:
        """
        Uses scaler to normalize inputs.
        """
        pass

    @abstractmethod
    def patch_data(self, clean_input):
        """
        Fill missing data.
        """
        pass

    def initial_preprocessing(self, input_bundle):
        """
        Method used for applying initial changes to DataFrame input.
        """
        return input_bundle

    def final_preprocessing(self, input_bundle):
        """
        Method used for applying any additional changes to scaled and normalized DataFrame input.
        """
        return input_bundle
