from typing import Type

from fhir.resources.group import Group as GroupFHIR
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.abstract_converters import \
    GenericContainedResourceConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.dataclasses import FhirClaimInformation
from claim_ai.evaluation.input_models import BaseDataFrameModel, Group as GroupAI


class GroupConverter(GenericContainedResourceConverter):
    _FHIR_RESOURCE = GroupFHIR
    _AI_MODEL = GroupAI

    def _fhir_repr_to_ai_input(self, fhir_repr: FhirClaimInformation) -> dict:
        contained_resource: GroupConverter._FHIR_RESOURCE = fhir_repr.fhir_resource
        return {
            'poverty_status': self._get_poverty_status(contained_resource),
            'group': self._get_group_id(contained_resource)
        }

    def _get_poverty_status(self, fhir_repr: GroupFHIR):
        return next((extension.valueBoolean for extension in fhir_repr.extension
                     if extension.url.endswith('poverty-status')) or [], False)

    def _get_group_id(self, fhir_repr: GroupFHIR):
        return fhir_repr.id
