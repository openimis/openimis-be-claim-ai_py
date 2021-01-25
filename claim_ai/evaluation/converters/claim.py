from collections import defaultdict
from datetime import datetime

from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation import input_models
from claim_ai.evaluation.converters.base_converter import AbstractConverter


class ClaimConverter(AbstractConverter):

    def to_ai_input(self, claim):
        claim_inputs_for_items = defaultdict(lambda: {})

        for item in claim['item']:
            item_type = item['extension'][0]['url']
            item_id = self._get_item_id_by_product_service(claim, item_type, item['productOrService']['text'])
            claim_item_id = item['extension'][0]['valueReference']['identifier']['value']
            claim_inputs_for_items[item_type][item_id] = self.convert_claim_fields(claim, claim_item_id)
        return claim_inputs_for_items

    def convert_claim_fields(self, claim, item_id):
        diagnosis_0, diagnosis_1 = self._get_diagnosis_reference(claim)
        billable_from = claim['billablePeriod']['start']
        billable_to = claim['billablePeriod'].get('end', None)
        claim_data = input_models.Claim(
            identifier=claim['id'],
            billable_period_from=self._strptime(billable_from),
            billable_period_to=self._strptime(billable_to or billable_from),  # date from if not empty
            created=self._strptime(claim['created']),
            type=claim['type']['text'],
            item_quantity=self._get_claim_item_quantity(claim, item_id),
            item_unit_price=self._get_claim_item_unit_price(claim, item_id),
            diagnosis_0=diagnosis_0,
            diagnosis_1=diagnosis_1,
            enterer=self._get_enterer(claim),
        )
        return claim_data

    def _get_claim_item_quantity(self, claim, item_id):
        return next(item['quantity']['value'] for item in claim['item']
                    if item['extension'][0]['valueReference']['identifier']['value'] == item_id)

    def _get_claim_item_unit_price(self, claim, item_id):
        return next(item['unitPrice']['value'] for item in claim['item']
                    if item['extension'][0]['valueReference']['identifier']['value'] == item_id)

    def _get_diagnosis_reference(self, claim):
        diagnoses = claim['diagnosis']
        references = [
            d['diagnosisReference']['identifier'] for d in diagnoses
            if d['type'][0]['coding'][0]['code'] in ['icd_0', 'icd_1']]

        return tuple(references) if len(references) == 2 else (references[0], references[0])

    def _get_enterer(self, claim):
        return claim['enterer']['identifier']['value']

    def _get_item_id_by_product_service(self, claim, resource_type, code):
        return next((provided['id'] for provided in claim['contained']
                     if provided['resourceType'] == resource_type
                     and provided['identifier'][1]['value'] == code))

    def _strptime(self, date_string):
        return datetime.strptime(date_string, ClaimAiConfig.date_format)
