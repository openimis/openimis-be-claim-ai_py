import logging
from abc import ABC, abstractmethod
from itertools import zip_longest
from typing import Type, List

from fhir.resources.resource import Resource

from claim_ai.evaluation.converters.base_converter import AbstractConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_converters.dataclasses import FhirClaimInformation
from claim_ai.evaluation.input_models import BaseDataFrameModel


logger = logging.getLogger(__name__)


class FHIRResourceConverter(AbstractConverter, ABC):
    @property
    def _FHIR_RESOURCE(self) -> Type[Resource]:
        raise NotImplementedError("Resource converter has to define FHIR resource")

    @property
    def _AI_MODEL(self) -> Type[BaseDataFrameModel]:
        raise NotImplementedError("Resource converter has to define AI resource")

    def to_ai_input(self, resource: dict):
        fhir_representations = self._convert_to_fhir_model(resource)
        ai_model_data = self._fhir_repr_to_ai_input(fhir_representations)
        return self._convert_input_to_ai_model(ai_model_data)

    def _convert_to_fhir_model(self, resource):
        assert self._is_fhir_valid(resource), "Validation failed for FHIR resource"
        return self._FHIR_RESOURCE(**resource)

    def _convert_input_to_ai_model(self, ai_input_data):
        assert self._is_ai_resource_valid(ai_input_data), "Validation failed for AI resource"
        return self._AI_MODEL(**ai_input_data)

    @abstractmethod
    def _fhir_repr_to_ai_input(self, fhir_repr: _FHIR_RESOURCE) -> dict:
        raise NotImplementedError()

    def _is_fhir_valid(self, fhir_resource: dict):
        return True

    def _is_ai_resource_valid(self, fhir_resource: dict):
        return True


class GenericContainedResourceConverter(FHIRResourceConverter, ABC):
    def to_ai_input(self, resource: dict):
        fhir_representations = self._convert_to_fhir_model(resource)
        main_resource_reference_field = self._get_information_from_main_resource(resource)
        pairs = self._connect_contained_with_claim_field(fhir_representations, main_resource_reference_field)
        ai_model_data = [self._fhir_repr_to_ai_input(pair) for pair in pairs]
        return [self._convert_input_to_ai_model(ai_input_data) for ai_input_data in ai_model_data]

    def _convert_to_fhir_model(self, dict_repr: dict):
        list_of_resources = self._extract_fhir_resources_from_claim_resource(dict_repr)
        assert len(list_of_resources) > 0, 'Resource not found in list of contained resources'
        fhir_objs = [
            super(GenericContainedResourceConverter, self)._convert_to_fhir_model(resource)
            for resource in list_of_resources
        ]
        return fhir_objs

    def _get_information_from_main_resource(self, claim: dict) -> List[dict]:
        return []

    def _extract_fhir_resources_from_claim_resource(self, claim_resource: dict, resource_type=None):
        if resource_type is None:
            # Even though resource_type is const, it's not available from type class
            resource_type = self._FHIR_RESOURCE.__fields__['resource_type'].default
        return [x for x in claim_resource['contained'] if x['resourceType'] == resource_type]

    @abstractmethod
    def _fhir_repr_to_ai_input(self, fhir_repr: FhirClaimInformation) -> dict:
        pass

    def _connect_contained_with_claim_field(self, fhir_representations_list, claim_field_list):
        data = []
        for contained_resource, claim_resource in zip_longest(fhir_representations_list, claim_field_list):
            data.append(
                FhirClaimInformation(
                    fhir_resource=contained_resource,
                    claim_resource=claim_resource
                )
            )
        return data


class MedicalProvision(GenericContainedResourceConverter, ABC):

    def _fhir_repr_to_ai_input(self, fhir_repr: FhirClaimInformation) -> dict:
        contained_part = fhir_repr.fhir_resource
        claim_field = fhir_repr.claim_resource

        return {
            'identifier': self._get_identifier(contained_part),
            'unit_price': self._get_unit_price(contained_part),
            'frequency': self._get_frequency(contained_part),
            'use_context': self._get_use_context(contained_part),
            'quantity': self._get_claim_item_quantity(contained_part, claim_field),
            'price_asked': self._get_claim_item_unit_price(contained_part, claim_field),
        }

    @property
    @abstractmethod
    def category(self):
        pass

    @abstractmethod
    def _get_context(self, use_context, context_url):
        raise NotImplementedError()

    @abstractmethod
    def _get_codes(self, use_context):
        raise NotImplementedError()

    def _get_claim_item_quantity(self, contained_part, claim_field):
        return int(claim_field['quantity']['value'])

    def _get_claim_item_unit_price(self, contained_part, claim_field):
        return float(claim_field['unitPrice']['value'])

    def _get_identifier(self, fhir_repr):
        return fhir_repr.id

    def _get_unit_price(self, fhir_repr):
        record = next(
            (ext.valueMoney.value for ext in fhir_repr.extension if ext.url.endswith('unit-price')), None
        )
        return float(record) if record else None

    @abstractmethod
    def _get_frequency(self, fhir_repr):
        raise NotImplementedError()

    def _get_use_context(self, fhir_repr):
        return self._get_use_context_from_provision(fhir_repr)

    def _get_use_context_from_provision(self, provided):
        # None if useContext not available
        use_context_ext = self._get_use_context_ext(provided)
        if use_context_ext:
            gender_context = self._get_context(use_context_ext, 'Gender')
            age_context = self._get_context(use_context_ext, 'Age')
            gender_context_value = self.__get_gender_context_value(gender_context) if gender_context else 0
            age_context_value = self.__get_age_context_value(age_context) if age_context else 0
            return gender_context_value + age_context_value
        else:
            return 0

    def __get_gender_context_value(self, use_context_gender):
        codes = self._get_codes(use_context_gender)
        female = 2 if 'female' in codes else 0
        male = 1 if 'male' in codes else 0
        return male + female

    def __get_age_context_value(self, use_context_age):
        codes = self._get_codes(use_context_age)
        kid = 8 if 'child' in codes else 0
        adult = 4 if 'adult' in codes else 0
        return kid + adult

    def _get_information_from_main_resource(self, claim: dict) -> List[dict]:
        activity_definitions = []
        for extension in claim['item']:
            if extension['category']['text'] == self.category:
                activity_definitions.append(extension)
        return activity_definitions

    @abstractmethod
    def _get_use_context_ext(self, provided):
        raise NotImplementedError()
