from datetime import datetime

from fhir.resources.claim import Claim as ClaimFHIR

from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import \
    FHIRResourceConverter
from claim_ai.evaluation.input_models import Claim as ClaimAI


class ClaimConverter(FHIRResourceConverter):
    _FHIR_RESOURCE = ClaimFHIR
    _AI_MODEL = ClaimAI

    def _fhir_repr_to_ai_input(self, fhir_repr: _FHIR_RESOURCE) -> dict:
        return {
            'identifier': fhir_repr.id,
            'billable_period_from': self._date_to_datetime(fhir_repr.billablePeriod.start),
            'billable_period_to': self._date_to_datetime(fhir_repr.billablePeriod.end),
            'created': self._date_to_datetime(fhir_repr.created),
            'type': fhir_repr.type.coding[0].code,
            'diagnosis_0': self._get_diagnosis(fhir_repr.diagnosis, diagnosis_index=0),
            'diagnosis_1': self._get_diagnosis(fhir_repr.diagnosis, diagnosis_index=1),
            'enterer': self._get_enterer(fhir_repr),
        }

    def _strptime(self, date_string):
        return datetime.strptime(date_string, ClaimAiConfig.date_format)

    def _get_diagnosis(self, diagnosis_collection, diagnosis_index, default_diagnosis_index=0):
        if len(diagnosis_collection) > diagnosis_index:
            return diagnosis_collection[diagnosis_index].diagnosisCodeableConcept.coding[0].code
        else:
            if default_diagnosis_index is not None:
                return diagnosis_collection[default_diagnosis_index].diagnosisCodeableConcept.coding[0].code
            else:
                raise AttributeError("Diagnosis index out of range")

    def _get_enterer(self, claim):
        return claim.enterer.identifier.value

    def _date_to_datetime(self, d):
        return datetime.fromordinal(d.toordinal())
