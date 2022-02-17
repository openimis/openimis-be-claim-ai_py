from abc import ABC, abstractmethod
from numbers import Number
from typing import Union

from medical.models import Item, Service

import core
from claim.models import ClaimItem, ClaimService
from claim_ai.evaluation.input_models import FhirAiInputModel, Medication, ActivityDefinition


class BaseAdjudicationBuilder(ABC):
    _ACCEPTED_RESULT_CODES = (
        "-1",  # Not Adjudicated
        "0",  # Accepted
        "1"  # Rejected
    )

    _RESULT_TEXTS = {
        "-1": 'not adjudicated',
        "0":  'accepted',
        "1": 'rejected'
    }

    def build_claim_response_item_adjudication(self, evaluated_entry, evaluation_result, sequence=1):
        return {
            "itemSequence": sequence,

            "adjudication": self.build_adjudication(
                self._get_unit_price(evaluated_entry),
                self._get_quantity(evaluated_entry),
                evaluation_result),

            "extension": self._get_extension(
                self._get_identifier(evaluated_entry),
                self._get_provision_type(evaluated_entry))
        }

    def build_adjudication(self, price, quantity, evaluation_result):
        return self._build_adjudication(price, quantity, evaluation_result)

    @abstractmethod
    def _get_provision_type(self, evaluation_result) -> str:
        pass

    @abstractmethod
    def _get_unit_price(self, evaluation_result) -> Number:
        pass

    @abstractmethod
    def _get_identifier(self, evaluation_result) -> str:
        pass

    @abstractmethod
    def _get_quantity(self, evaluation_result) -> Number:
        pass

    def _build_adjudication(self, unit_price, quantity, evaluation_result_code):
        if evaluation_result_code not in self._ACCEPTED_RESULT_CODES:
            raise ValueError(f"Invalid evaluation result code {evaluation_result_code}, should be "
                             f"one of {self._ACCEPTED_RESULT_CODES}")
        return [{
                "category": self._get_adjudication_category(),
                "reason": self._build_reason(evaluation_result_code),
                "amount": self._build_amount(unit_price),
                "value": quantity
        }]

    def _get_extension(self, item_identifier: str, provision_type):
        return [
            {
                "url": provision_type,   # "Medication" or "ActivityDefinition"
                "valueReference": {
                    "reference": F"{provision_type}/{item_identifier}"
                }
            }
        ]

    def _get_adjudication_category(self):
        return {
            "coding": [{"code": "-2"}],
            "text": "AI"
        }

    def _build_reason(self, evaluation_result_code):
        result_text = self._RESULT_TEXTS.get(evaluation_result_code) or 'undefined'
        return {
            "coding": [
                {
                    "code": evaluation_result_code  # "0": Accepted, "1": Rejected
                }
            ],
            "text": result_text  # Description of the result as "accepted" or "rejected"
        }

    def _build_amount(self, unit_price):
        return {
            "currency": core.currency if hasattr(core, 'currency') else None,
            "value": unit_price
        }


class AiInputModelAdjudicationBuilder(BaseAdjudicationBuilder):

    def _get_provision_type(self, evaluation_result: FhirAiInputModel) -> str:
        provision = self._get_provision(evaluation_result)
        return provision.type

    def _get_unit_price(self, evaluation_result) -> Number:
        provision = self._get_provision(evaluation_result)
        return provision.unit_price

    def _get_identifier(self, evaluation_result) -> str:
        provision = self._get_provision(evaluation_result)
        return provision.identifier

    def _get_quantity(self, evaluation_result) -> Number:
        provision = self._get_provision(evaluation_result)
        return provision.quantity

    def _get_provision(self, evaluation_result) -> Union[Medication, ActivityDefinition]:
        if evaluation_result.medication:
            return evaluation_result.medication
        elif evaluation_result.activity_definition:
            return evaluation_result.activity_definition
        else:
            raise ValueError(F"Neither medication nor activity definition available in entry {evaluation_result}")


class ClaimProvisionAdjudicationBuilder(BaseAdjudicationBuilder):

    def _get_provision_type(self, evaluation_result: 'ClaimProvisionEvaluationResult') -> str:
        if evaluation_result.content_type.model_class() == ClaimItem:
            return 'Medication'
        elif evaluation_result.content_type.model_class() == ClaimService:
            return 'ActivityDefinition'
        else:
            raise ValueError(F"Invalid provision type {evaluation_result.content_type.model} "
                             F"in item evaluation {evaluation_result}")

    def _get_unit_price(self, evaluation_result: 'ClaimProvisionEvaluationResult') -> Number:
        return self._get_provision(evaluation_result).price

    def _get_identifier(self, evaluation_result: 'ClaimProvisionEvaluationResult') -> str:
        return self._get_provision(evaluation_result).uuid

    def _get_quantity(self, evaluation_result: 'ClaimProvisionEvaluationResult') -> Number:
        return evaluation_result.content_object.qty_provided

    def _get_provision(self, evaluation_result: 'ClaimProvisionEvaluationResult') -> Union[Item, Service]:
        return evaluation_result.content_object.itemsvc


