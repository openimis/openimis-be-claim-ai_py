from typing import List
from datetime import date

from .base_converter import AbstractConverter
from .claim import ClaimConverter
from .patient import PatientConverter
from .healthcare import HealthcareServiceConverter
from .medical_provisions import MedicationConverter, ActivityDefinitionConverter
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.evaluation.input_models import *
from claim_ai.apps import ClaimAiConfig


class AiConverter(AbstractConverter):
    medication_converter = MedicationConverter()
    activity_definition_converter = ActivityDefinitionConverter()
    claim_converter = ClaimConverter()
    patient_converter = PatientConverter()
    healthcare_service_converter = HealthcareServiceConverter()

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

    def to_ai_output(self, claim: dict, entries_with_evaluation: List[EvaluationResult]):
        return {
            "resourceType": "ClaimResponse",
            "status": claim['status'],
            "type": claim['type'],
            "use": claim['use'],
            "patient": {
                "reference": claim['patient']['reference']
            },
            "created": date.today().strftime(ClaimAiConfig.date_format),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": claim['id'],
            "request": {
                "reference": F"Claim/{claim['id']}",
            },
            "outcome": "complete",
            "item": self._build_items(entries_with_evaluation)
        }

    def claim_response_error(self, claim: dict, error_reason: str):
        return {
            "resourceType": "ClaimResponse",
            "status": claim['status'],
            "type": claim['type'],
            "use": claim['use'],
            "patient": {
                "reference": claim['patient']['reference']
            },
            "created": date.today().strftime(ClaimAiConfig.date_format),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": claim['id'],
            "request": {
                "reference": F"Claim/{claim['id']}",
            },
            "outcome": "error",
            "error": [
                {
                    "coding": [{
                        "code": "-1"
                    }],
                    "text": error_reason
                }
            ]
        }

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
