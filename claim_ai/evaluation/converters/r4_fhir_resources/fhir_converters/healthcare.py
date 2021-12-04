from fhir.resources.organization import Organization as OrganizationFHIR
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import \
    GenericContainedResourceConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.dataclasses import FhirClaimInformation
from claim_ai.evaluation.input_models import BaseDataFrameModel, HealthcareService as HealthcareService


class OrganizationConverter(GenericContainedResourceConverter):
    _FHIR_RESOURCE = OrganizationFHIR
    _AI_MODEL = HealthcareService

    def _fhir_repr_to_ai_input(self, fhir_repr: FhirClaimInformation) -> dict:
        contained_resource: OrganizationConverter._FHIR_RESOURCE = fhir_repr.fhir_resource
        return {
            'identifier': self._get_contained_healthcare_service_identifier(contained_resource),
            'location': self._get_contained_healthcare_service_location(contained_resource),
            'category': self._get_contained_healthcare_service_category(contained_resource),
            'type': self._get_contained_healthcare_service_type(contained_resource)
        }

    def _get_contained_healthcare_service_identifier(self, healthcare_extension):
        return healthcare_extension.id

    def _get_contained_healthcare_service_location(self, healthcare_extension):
        return healthcare_extension.address[0].extension[0].valueReference.identifier.value

    def _get_contained_healthcare_service_category(self, healthcare_extension):
        return next((extension.valueCodeableConcept.coding[0].code for extension in healthcare_extension.extension
                     if extension.url.endswith('organization-hf-level')) or [], None)

    def _get_contained_healthcare_service_type(self, healthcare_extension):
        return next((extension.valueCodeableConcept.coding[0].code for extension in healthcare_extension.extension
                     if extension.url.endswith('organization-hf-care-type')) or [], None)
