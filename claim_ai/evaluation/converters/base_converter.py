from abc import ABC, abstractmethod
from typing import List

from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.evaluation.input_models import *


class AbstractConverter(ABC):

    def to_ai_input(self, fhir_claim_resource):
        raise NotImplementedError("to_ai_input not implemented")


class BaseAIConverter(AbstractConverter, ABC):
    @property
    @abstractmethod
    def medication_converter(self):
        pass

    @property
    @abstractmethod
    def group_converter(self):
        pass

    @property
    @abstractmethod
    def activity_definition_converter(self):
        pass

    @property
    @abstractmethod
    def claim_converter(self):
        pass

    @property
    @abstractmethod
    def patient_converter(self):
        pass

    @property
    @abstractmethod
    def healthcare_service_converter(self):
        pass


class AbstractAIBundleConverter(AbstractConverter):

    @abstractmethod
    def bundle_ai_output(self, evaluation_output: List[EvaluationResult], invalid_claims):
        pass
