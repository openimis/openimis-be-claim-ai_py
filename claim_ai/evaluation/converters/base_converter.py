from abc import ABC, abstractmethod
from typing import List

from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.evaluation.input_models import *


class AbstractConverter(ABC):

    def to_ai_input(self, input_item):
        raise NotImplementedError("to_ai_input not implemented")

    def to_ai_output(self, ai_item):
        raise NotImplementedError("to_ai_input not implemented")


class AbstractAIModelConverter(AbstractConverter):
    @abstractmethod
    def claim_response_error(self, claim: dict, error_reason: str):
        pass


class BaseAIConverter(AbstractConverter, ABC):
    @property
    @abstractmethod
    def medication_converter(self):
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

    def to_ai_input(self, fhir_claim_repr: dict) -> List[AiInputModel]:
        items = self.medication_converter.to_ai_input(fhir_claim_repr)
        services = self.activity_definition_converter.to_ai_input(fhir_claim_repr)
        claims = self.claim_converter.to_ai_input(fhir_claim_repr)
        patient = self.patient_converter.to_ai_input(fhir_claim_repr)
        healthcare_service = self.healthcare_service_converter.to_ai_input(fhir_claim_repr)

        item_entries = []
        service_entries = []

        for item in items:
            claim = claims['Medication'][item.identifier]
            entry = self.convert_ai_entry(claim, patient, healthcare_service, item=item)
            item_entries.append(entry)

        for service in services:
            claim = claims['ActivityDefinition'][service.identifier]
            entry = self.convert_ai_entry(claim, patient, healthcare_service, service=service)
            service_entries.append(entry)

        return item_entries + service_entries

    def _build_items(self, entries_with_evaluation: List[EvaluationResult]):
        response_items = []
        for entry in entries_with_evaluation:
            sequence = 0
            provided = entry.input
            result = str(entry.result)  # result is in str type
            claim = provided.claim
            if provided.medication:
                response_item = self.medication_converter\
                        .to_ai_output(provided.medication, claim, result, sequence)
                response_items.append(response_item)
                sequence += 1
            if provided.activity_definition:
                response_item = self.activity_definition_converter\
                    .to_ai_output(provided.activity_definition, claim, result, sequence)
                response_items.append(response_item)
                sequence += 1

        return response_items

    def convert_ai_entry(self, claim: Claim, patient: Patient, healthcare: HealthcareService,
                         item: Medication = None, service: ActivityDefinition = None):
        return AiInputModel(
            medication=item,
            activity_definition=service,
            claim=claim,
            patient=patient,
            healthcare_service=healthcare
        )

