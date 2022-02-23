import logging
import traceback
from dataclasses import dataclass

import pandas
from django.db.models import Q, Value, CharField
from typing import Iterable, Any, Union

from claim.models import ClaimItem, ClaimService, Claim
from core.schema import core
from . import BaseDataFrameModel
from ...models import ClaimBundleEvaluation

logger = logging.getLogger(__name__)


class ClaimBundleEvaluationInputError(ValueError):
    pass


@dataclass
class ClaimBundleEvaluationAiInputModel(BaseDataFrameModel):
    claim_bundle_evaluation: ClaimBundleEvaluation

    def to_representation(self):
        return self._build_input_dataframe(self.claim_bundle_evaluation)

    @classmethod
    def _build_input_dataframe(cls, claim_bundle_evaluation: ClaimBundleEvaluation):
        claim_ids = claim_bundle_evaluation.claims.values_list('claim__id', flat=True)
        claim_provisions_df = cls._claims_to_df(claim_ids)
        return claim_provisions_df

    @classmethod
    def _claims_to_df(cls, claim_ids):
        current_items, current_services = cls.__current_items_and_services(claim_ids)
        historical_items, historical_services = cls.__historical_items_and_services(claim_ids)
        joined = [*current_items, *current_services, *historical_items, *historical_services]
        input_ = map(lambda x: cls._claim_provision_to_df_row(x), joined)
        input_ = pandas.DataFrame(input_)
        return input_

    @classmethod
    def _claim_provision_to_df_row(cls, claim_item: Union[ClaimItem, ClaimService]):
        return {
            'ProvisionID': claim_item.id,  # Property not used in model prediction but can connect items to index
            'ProvisionType': 'ActivityDefinition' if claim_item.model_prefix == 'service' else 'Medication',
            'ItemUUID': claim_item.itemsvc.uuid,
            'HFUUID': claim_item.claim.health_facility.uuid,
            'LocationId': claim_item.claim.health_facility.location.id,
            'ICDCode': claim_item.claim.icd.code,
            'ICD1Code': claim_item.claim.icd_1.code if claim_item.claim.icd_1 else None,
            'ProdID': claim_item.product.id if claim_item.product else None,
            'DOB': claim_item.claim.insuree.dob,
            'Gender': cls._get_claim_item_value(
                    claim_item, lambda x: x.claim.insuree.gender.code, 'Gender', 'Insuree without gender.'),
            'Poverty': claim_item.claim.insuree.family.poverty if claim_item.claim.insuree.family else None,
            'QuantityProvided': int(claim_item.qty_provided),
            'ItemPrice': float(claim_item.itemsvc.price),
            'PriceAsked': float(claim_item.price_asked),
            'DateFrom': claim_item.claim.date_from,
            'DateTo': claim_item.claim.date_to or claim_item.claim.date_from,
            'DateClaimed': claim_item.claim.date_claimed,
            'ItemFrequency': claim_item.itemsvc.frequency,
            'ItemPatCat': claim_item.itemsvc.patient_category,
            'ItemLevel': claim_item.itemsvc.level if isinstance(claim_item, ClaimService) else 'M',
            'HFLevel': claim_item.claim.health_facility.level,
            'HFCareType': claim_item.claim.health_facility.care_type,  # Note: Field can be empty, its ' ' by default.
            'VisitType': claim_item.claim.visit_type,
            'RejectionReason': claim_item.rejection_reason,
            'PriceValuated': float(claim_item.price_valuated or 0),
            'HfUUID': claim_item.claim.admin.health_facility.uuid,
            'ClaimAdminUUID': claim_item.claim.admin.uuid,
            'InsureeUUID': claim_item.claim.insuree.uuid,
            'ClaimUUID': claim_item.claim.uuid,
            'New': claim_item.New  # annotated
        }

    @classmethod
    def _get_claim_item_value(cls, item, func, field, err_msg):
        try:
            return func(item)
        except (AttributeError, TypeError) as e:
            logger.error(F"Exception occurred during building DF Row: {e}")
            logger.debug(traceback.format_exc())
            raise ClaimBundleEvaluationInputError(
                f'Invalid DF Row input source for column {field}, '
                f'error reason: {err_msg}') from e

    @classmethod
    def _get_historical_claim_ids(cls, claims_ids: Iterable[Any]) -> Iterable[Any]:
        historical = Claim.objects.filter(id__in=claims_ids).all()
        insuree_ids = historical.values_list('insuree_id', flat=True)
        hf_ids = historical.values_list('health_facility_id', flat=True)
        query_filter = Q(insuree_id__in=insuree_ids) | Q(health_facility_id__in=hf_ids)

        # Get only valid claims, exclude following evaluation
        qs = Claim.objects.filter(*core.filter_validity()).exclude(id__in=claims_ids)
        # Id's of claims for relevant insurees and health facilities
        qs = qs.filter(query_filter).values_list('id', flat=True)
        return qs

    @classmethod
    def __current_items_and_services(cls, claim_ids):
        return cls.__items_by_claim_id(claim_ids).annotate(New=Value('new', CharField())), \
               cls.__services_by_claim_id(claim_ids).annotate(New=Value('new', CharField()))

    @classmethod
    def __historical_items_and_services(cls, current_claim_ids):
        claim_ids = cls._get_historical_claim_ids(current_claim_ids)
        return cls.__items_by_claim_id(claim_ids).annotate(New=Value('old', CharField())),\
            cls.__services_by_claim_id(claim_ids).annotate(New=Value('old', CharField()))

    @classmethod
    def __items_and_services_for_claim_ids(cls, claim_ids):
        return cls.__items_by_claim_id(claim_ids), cls.__services_by_claim_id(claim_ids)

    @classmethod
    def __items_by_claim_id(cls, claim_ids):
        prefetch = ['claim', 'claim__insuree',
                    'claim__health_facility', 'claim__health_facility__location',
                    'claim__admin', 'claim__admin__health_facility',
                    'product', 'item', 'claim__insuree__family']
        return cls.__claim_provision_by_claim_id(claim_ids, ClaimItem, prefetch)

    @classmethod
    def __services_by_claim_id(cls, claim_ids):
        prefetch = ['claim', 'claim__insuree',
                    'claim__health_facility', 'claim__health_facility__location',
                    'claim__admin', 'claim__admin__health_facility',
                    'product', 'service', 'claim__insuree__family']
        return cls.__claim_provision_by_claim_id(claim_ids, ClaimService, prefetch)

    @classmethod
    def __claim_provision_by_claim_id(cls, claim_ids, provision_model, prefetch):
        return provision_model.objects \
            .filter(claim_id__in=claim_ids, validity_to__isnull=True) \
            .all() \
            .prefetch_related(*prefetch)

    @classmethod
    def _get_total_price(cls, claim: Claim):
        prices = [i.item.price for i in claim.items.all()] + [i.service.price for i in claim.services.all()]
        return sum(prices)
