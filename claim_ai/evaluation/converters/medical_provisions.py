from claim_ai.evaluation import input_models
from claim_ai.evaluation.converters.base_converter import AbstractConverter


class BaseProvidedConverter(AbstractConverter):

    @property
    def provision_type(self):
        raise NotImplementedError("provision_type type has to be defined")

    @property
    def input_model(self):
        raise NotImplementedError("input_model type has to be defined")

    def to_ai_input(self, claim):
        medications = []
        claim_items = self._get_medications(claim)
        for claim_item in claim_items:
            medications.append(self._convert_provided(claim_item))
        return medications

    def _get_medications(self, claim):
        return [item for item in claim['contained']
                if item['resourceType'] == self.provision_type]

    def _convert_provided(self, provided):
        return self.input_model(
            identifier=provided['id'],
            unit_price=self._get_unit_price_from_extension(provided['extension']),
            frequency=self._get_frequency_from_extension(provided['extension']),
            use_context=self._get_use_context_from_provision(provided)
        )

    def _get_unit_price_from_extension(self, extension):
        record = next(d for d in extension if d['url'] == 'unitPrice')
        return record['valueMoney']['value']

    def _get_frequency_from_extension(self, extension):
        record = next(d for d in extension if d['url'] == 'frequency')
        return record['valueInteger']

    def _get_use_context_from_provision(self, provided):
        # None if useContext not available
        record = next(
            (d['valueUsageContext']['valueCodeableConcept']['coding'][0]['code']
             for d in provided['extension']
             if d['url'] == 'useContextVenue'),
            None
        )
        return record


class MedicationConverter(BaseProvidedConverter):
    provision_type = 'Medication'
    input_model = input_models.Medication


class ActivityDefinitionConverter(BaseProvidedConverter):
    provision_type = 'ActivityDefinition'
    input_model = input_models.ActivityDefinition

    def _get_use_context_from_provision(self, provision):
        # None if useContext not available
        record = next((d['valueCodeableConcept']['coding'][0]['code']  for d in provision['useContext']
                       if d['code']['code'] == 'useContextVenue'), None)
        return record
