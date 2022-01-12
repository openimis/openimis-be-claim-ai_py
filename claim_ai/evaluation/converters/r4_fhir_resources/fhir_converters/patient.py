from datetime import datetime
from typing import List

from fhir.resources.patient import Patient as PatientFHIR

from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import \
    GenericContainedResourceConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.dataclasses import FhirClaimInformation
from claim_ai.evaluation.input_models import BaseDataFrameModel, Patient as PatientAI


class PatientConverter(GenericContainedResourceConverter):
    _FHIR_RESOURCE = PatientFHIR
    _AI_MODEL = PatientAI

    def _fhir_repr_to_ai_input(self, fhir_repr: FhirClaimInformation) -> dict:
        contained_part: PatientConverter._FHIR_RESOURCE = fhir_repr.fhir_resource
        return {
            'identifier': self._get_claim_patient_identifier(contained_part),
            'birth_date': self._get_contained_patient_birth_date(contained_part),
            'gender': self._get_contained_patient_gender(contained_part),
            'is_head': self._get_contained_patient_is_head(contained_part),
            'location_code': self._get_contained_patient_location_code(contained_part),
        }

    def _get_claim_patient_identifier(self, fhir_repr: PatientFHIR):
        return fhir_repr.id

    def _get_contained_patient_birth_date(self, fhir_repr: PatientFHIR):
        return self._date_to_datetime(fhir_repr.birthDate)

    def _get_contained_patient_gender(self, contained_patient):
        gender = contained_patient.gender
        if gender == 'male':
            return 'M'
        elif gender == 'female':
            return 'F'
        else:
            return gender

    def _get_contained_patient_is_head(self, fhir_repr: PatientFHIR):
        # IMIS value for isHead extension url: https://openimis.atlassian.net/wiki/spaces/OP/pages/960069653/isHead"
        return next(
            extension.valueBoolean for extension in fhir_repr.extension if extension.url.endswith('patient-is-head')
        )

    def _get_contained_patient_location_code(self, fhir_repr: PatientFHIR):
        location = fhir_repr.address[0] if fhir_repr.address else None
        if location:
            loc_id = next(
                extension.valueReference.identifier.value
                    for extension in location.extension if extension.url.endswith('address-location-reference')
            )
            return loc_id
        return None

    def _date_to_datetime(self, d):
        return datetime.fromordinal(d.toordinal())
