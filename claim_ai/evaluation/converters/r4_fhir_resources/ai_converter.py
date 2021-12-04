from claim_ai.evaluation.converters.base_converter import BaseAIConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters import ClaimConverter, MedicationConverter, \
    ActivityDefinitionConverter, PatientConverter, GroupConverter, OrganizationConverter
from claim_ai.evaluation.input_models import AiInputModel


class AiConverter(BaseAIConverter):
    claim_converter = ClaimConverter()
    medication_converter = MedicationConverter()
    activity_definition_converter = ActivityDefinitionConverter()
    patient_converter = PatientConverter()
    healthcare_service_converter = OrganizationConverter()
    group_converter = GroupConverter()

    def to_ai_input(self, fhir_claim_resource: dict):
        # Fields fixed for all entries for given claim resource
        immutable_fields = self._convert_fixed_fields(fhir_claim_resource)
        items_entries = self._build_items(fhir_claim_resource, immutable_fields)
        services_entries = self._build_services(fhir_claim_resource, immutable_fields)
        return [self.__create_ai_input(provision) for provision in items_entries+services_entries]

    def _convert_fixed_fields(self, fhir_claim_resource):
        return {
            'claim': self.claim_converter.to_ai_input(fhir_claim_resource),
            # Expected one contained resource for every data type
            'group': self.group_converter.to_ai_input(fhir_claim_resource)[0],
            'healthcare_service': self.healthcare_service_converter.to_ai_input(fhir_claim_resource)[0],
            'patient': self.patient_converter.to_ai_input(fhir_claim_resource)[0],
        }

    def __create_ai_input(self, fields: dict):
        return AiInputModel(
            **fields
        )

    def _build_items(self, fhir_claim_resource, immutable_fields):
        items = self.medication_converter.to_ai_input(fhir_claim_resource)
        return self.__build_ai_model_data(items, immutable_fields, 'medication')

    def _build_services(self, fhir_claim_resource, immutable_fields):
        items = self.activity_definition_converter.to_ai_input(fhir_claim_resource)
        return self.__build_ai_model_data(items, immutable_fields, 'activity_definition')

    def __build_ai_model_data(self, list_of_provisions, immutable_fields, provision_type):
        entries = []
        for item in list_of_provisions:
            entry = immutable_fields.copy()
            entry[provision_type] = item
            entries.append(entry)
        return entries
