
import core
from claim_ai.evaluation.input_models import ProvidedItem, AiInputModel


class AdjudicationBuilder:
    def build_claim_response_item_adjudication(
            self, ai_input_entry: AiInputModel, evaluation_result, sequence=1):
        ai_item, provision_type = self.__get_provision_and_type(ai_input_entry)
        extension = self._get_extension(ai_item, provision_type)
        adjudication = self._build_adjudication(ai_item, ai_item.quantity, evaluation_result)
        return {
            "itemSequence": sequence,
            "adjudication": adjudication,
            "extension": extension
        }

    def _get_extension(self, ai_item: ProvidedItem, provision_type):
        return [
            {
                "url": provision_type,   # "Medication" or "ActivityDefinition"
                "valueReference": {
                    "reference": F"{provision_type}/{ai_item.identifier}"
                }
            }
        ]

    def _build_adjudication(self, ai_item, quantity, evaluation_result_code):
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

    def __get_provision_and_type(self, ai_input_entry):
        if ai_input_entry.medication:
            return ai_input_entry.medication, 'Medication'
        elif ai_input_entry.activity_definition:
            return ai_input_entry.activity_definition, 'Activity Definition'
        else:
            raise ValueError(F"Neither medication nor activity definition available in entry {ai_input_entry}")
