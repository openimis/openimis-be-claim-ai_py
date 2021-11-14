from claim_ai.evaluation.converters.base_converter import AbstractConverter, BaseAIConverter
from .claim import ClaimConverter
from .patient import PatientConverter
from .healthcare import HealthcareServiceConverter
from .medical_provisions import MedicationConverter, ActivityDefinitionConverter
from ..claim_response_converter_mixin import ClaimResponseConverterMixin


class AiConverter(ClaimResponseConverterMixin, BaseAIConverter):
    medication_converter = MedicationConverter()
    activity_definition_converter = ActivityDefinitionConverter()
    claim_converter = ClaimConverter()
    patient_converter = PatientConverter()
    healthcare_service_converter = HealthcareServiceConverter()
