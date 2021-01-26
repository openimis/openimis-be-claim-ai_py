import core

from claim_ai.evaluation import input_models
from claim_ai.evaluation.converters.base_converter import AbstractConverter
from claim_ai.evaluation.input_models import ProvidedItem, Claim


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

    def to_ai_output(self, ai_item: ProvidedItem, claim: Claim, evaluation_result, sequence=0):
        extension = self._get_extension(ai_item)
        adjudication = self._get_adjudication(ai_item, claim.item_quantity, evaluation_result)
        return {
            "itemSequence": sequence,
            "adjudication": adjudication,
            "extension": extension
        }

    def _get_extension(self, ai_item: ProvidedItem):
        return [
            {
                "url": self.provision_type,   # "Medication" or "ActivityDefinition"
                "valueReference": {
                    "reference": F"{self.provision_type}/{ai_item.identifier}"
                }
            }
        ]

    def _get_adjudication(self, ai_item, quantity, evaluation_result_code):
        result_text = 'accepted' if evaluation_result_code == '0' else 'rejected'
        return [{"category": self._get_adjudication_category(),
                "reason": {
                    "coding": [
                        {
                            "code": evaluation_result_code  # "0": Accepted, "1": Rejected
                        }
                    ],
                    "text": result_text  # Description of the result as "accepted" or "rejected"
                },
                "amount": {
                    "currency": core.currency if hasattr(core, 'currency') else None,
                    "value": ai_item.unit_price
                },
                "value": quantity
            }]

    def _get_adjudication_category(self):
        return {
            "coding": [{"code": "-2"}],
            "text": "AI"
        }

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
        gender_context = self._get_context(provided, 'useContextGender')
        age_context = self._get_context(provided, 'useContextAge')

        gender_context_value = self._get_gender_context_value(gender_context) if gender_context else 0
        age_context_value = self._get_age_context_value(age_context) if age_context else 0
        return bin(gender_context_value+age_context_value)

    def _get_context(self, provided, context_url):
        return next((context for context in provided['extension']
                     if context['url'] == context_url), None)

    def _get_gender_context_value(self, use_context_gender):
        codes = self._get_codes(use_context_gender)
        female = 2 if 'F' in codes else 0
        male = 1 if 'M' in codes else 0
        return male + female

    def _get_age_context_value(self, use_context_age):
        codes = self._get_codes(use_context_age)
        kid = 8 if 'K' in codes else 0
        adult = 4 if 'A' in codes else 0
        return kid + adult

    def _get_codes(self, use_context):
        return [coding['code'] for coding in use_context['valueUsageContext']['valueCodeableConcept']['coding']]


class MedicationConverter(BaseProvidedConverter):
    provision_type = 'Medication'
    input_model = input_models.Medication


class ActivityDefinitionConverter(BaseProvidedConverter):
    provision_type = 'ActivityDefinition'
    input_model = input_models.ActivityDefinition

    def _get_context(self, provided, context_url):
        return next((context for context in provided['useContext']
                     if context['code']['code'] == context_url), None)

    def _get_codes(self, use_context):
        return [coding['code'] for coding in use_context['valueCodeableConcept']['coding']]
