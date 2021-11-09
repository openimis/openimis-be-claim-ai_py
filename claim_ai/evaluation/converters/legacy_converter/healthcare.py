from claim_ai.evaluation import input_models
from claim_ai.evaluation.converters.legacy_converter.base_converter import AbstractConverter


class HealthcareServiceConverter(AbstractConverter):

    def to_ai_input(self, claim):
        contained_value = next(contained for contained in claim['contained']
                               if contained['resourceType'] == 'HealthcareService')

        healthcare = input_models.HealthcareService(
            identifier=self._get_contained_healthcare_service_identifier(contained_value),
            location=self._get_contained_healthcare_service_location(contained_value),
            category=self._get_contained_healthcare_service_category(contained_value),
            type=self._get_contained_healthcare_service_type(contained_value)
        )
        return healthcare

    def _get_contained_healthcare_service_identifier(self, healthcare_extension):
        return healthcare_extension['id'].split('/')[1]

    def _get_contained_healthcare_service_location(self, healthcare_extension):
        return healthcare_extension['location'][0]['identifier']['value']

    def _get_contained_healthcare_service_category(self, healthcare_extension):
        category = healthcare_extension['category'][0]['coding'][0]['code']
        if category == 'OF':
            return 'C'
        elif category == 'HOSP':
            return 'H'
        elif category == 'COMM':
            return 'D'
        else:
            return category

    def _get_contained_healthcare_service_type(self, healthcare_extension):
        return healthcare_extension['type'][0]['coding'][0]['code']
