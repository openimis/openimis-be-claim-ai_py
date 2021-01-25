from typing import List

from .base_converter import AbstractConverter
from .claim import ClaimConverter
from .patient import PatientConverter
from .healthcare import HealthcareServiceConverter
from .medical_provisions import MedicationConverter, ActivityDefinitionConverter

from ..input_models import *


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

    def convert_ai_entry(self, claim: Claim, patient: Patient, healthcare: HealthcareService,
                         item: Medication = None, service: ActivityDefinition = None):
        return AiInputModel(
            medication=item,
            activity_definition=service,
            claim=claim,
            patient=patient,
            healthcare_service=healthcare
        )
