import logging
import traceback
from dataclasses import dataclass
from itertools import chain

import pandas
from django.db.models import Q, Value, CharField, Prefetch, QuerySet
from typing import Iterable, Any, Union

from claim.models import ClaimItem, ClaimService, Claim
from core.schema import core
from . import BaseDataFrameModel
from .raw_sql_data_loader import RawSQLDataFrameLoader
from ...models import ClaimBundleEvaluation

logger = logging.getLogger(__name__)


class ClaimBundleEvaluationInputError(ValueError):
    pass


@dataclass
class ClaimBundleEvaluationAiInputModel(BaseDataFrameModel):
    claim_bundle_evaluation: ClaimBundleEvaluation

    def to_representation(self):
        # df = self._build_input_dataframe(self.claim_bundle_evaluation)
        df = self._load_df_from_sql(self.claim_bundle_evaluation)
        return df

    @classmethod
    def _load_df_from_sql(cls, claim_bundle_evaluation: ClaimBundleEvaluation):
        claim_ids = claim_bundle_evaluation.claims.all().values_list('claim_id', flat=True)
        return RawSQLDataFrameLoader.build_dataframe_for_claim_ids(claim_ids)

    @classmethod
    def _build_input_dataframe(cls, claim_bundle_evaluation: ClaimBundleEvaluation):
        from django.db import connection, reset_queries
        reset_queries()
        relevant_claim_ids = claim_bundle_evaluation.claims.all().values_list('claim_id', flat=True)
        claims = Claim.objects.filter(id__in=relevant_claim_ids.all())
        claims = cls._select_related_claims_data(claims)\
            .annotate(New=Value('new', CharField()))
        historical_claims = cls._get_historical_claims(claims)
        claim_provisions_df = cls._claims_to_df(claims.all(), historical_claims.all())
        return claim_provisions_df

    @classmethod
    def _claims_to_df(cls, new_claims, historical_claims):
        new_provisions = chain.from_iterable(
            map(lambda x: cls._claim_provisions_to_df_row(x), new_claims))
        historical_provisions = chain.from_iterable(
            map(lambda x: cls._claim_provisions_to_df_row(x), historical_claims))
        input_ = [*new_provisions, *historical_provisions]
        input_ = pandas.DataFrame(input_)
        return input_

    @classmethod
    def _claim_provisions_to_df_row(cls, claim: Claim):
        items = cls.__claim_itemsvc_to_df_row(claim, claim.items)
        services = cls.__claim_itemsvc_to_df_row(claim, claim.services)
        return [*items, *services]

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
    def _get_historical_claims(cls, claims: QuerySet) -> QuerySet:
        claims_ids = claims.values_list('id', flat=True)
        insuree_ids = claims.values_list('insuree_id', flat=True)
        hf_ids = claims.values_list('health_facility_id', flat=True)
        query_filter = Q(insuree_id__in=insuree_ids) | Q(health_facility_id__in=hf_ids)

        # Get only valid claims, exclude following evaluation
        qs = Claim.objects.filter(*core.filter_validity()).exclude(id__in=claims_ids)

        # Id's of claims for relevant insurees and health facilities
        historical_claims = qs.filter(query_filter).annotate(New=Value('old', CharField()))
        return historical_claims

    @classmethod
    def __items_and_services_for_claim_ids(cls, claim_ids):
        return cls.__items_by_claim_id(claim_ids), cls.__services_by_claim_id(claim_ids)

    @classmethod
    def __items_by_claim_id(cls, claim_ids):
        select_related = [

        ]
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
            .all().prefetch_related(*prefetch)

    @classmethod
    def _get_total_price(cls, claim: Claim):
        prices = [i.item.price for i in claim.items.all()] + [i.service.price for i in claim.services.all()]
        return sum(prices)

    @classmethod
    def _select_related_claims_data(cls, claim_queryset: QuerySet):
        select_related = [
            'insuree', 'health_facility', 'health_facility__location', 'admin', 'admin__health_facility',
            'insuree__family', 'insuree__gender', 'icd', 'icd_1'
        ]
        prefetch_related = [
            Prefetch('items',
                     queryset=ClaimItem.objects
                        .filter(validity_to__isnull=True).select_related('item', 'product')
                        .only('id', 'item', 'product_id', 'qty_provided', 'item__price', 'price_asked', 'item__frequency', 'item__patient_category', 'rejection_reason', 'price_valuated')),
            Prefetch('services',
                     queryset=ClaimService.objects
                        .filter(validity_to__isnull=True).select_related('service', 'product')
                     .only('id', 'service', 'product_id', 'qty_provided', 'service__price', 'price_asked', 'service__frequency', 'service__patient_category', 'service__level', 'rejection_reason', 'price_valuated'))
        ]
        claims = claim_queryset.all()
        return claims\
            .select_related(*select_related)\
            .prefetch_related(*prefetch_related)

    @classmethod
    def __claim_itemsvc_to_df_row(cls, claim, items):
        o = []
        for claim_item in items.all():
            if isinstance(claim_item, ClaimService):
                claim_item.s = claim_item.service
            else:
                claim_item.s = claim_item.item
            o.append({
                'ProvisionID': claim_item.id,  # Property not used in model prediction but can connect items to index
                'ProvisionType': 'ActivityDefinition' if claim_item.model_prefix == 'service' else 'Medication',
                'ItemUUID': claim_item.s.uuid,
                'HFUUID': claim.health_facility.uuid,
                'LocationId': claim.health_facility.location.id,
                'ICDCode': claim.icd.code,
                'ICD1Code': claim.icd_1.code if claim.icd_1 else None,
                'ProdID': claim_item.product.id if claim_item.product else None,
                'DOB': claim.insuree.dob,
                'Gender': cls._get_claim_item_value(
                        claim_item, lambda x: x.claim.insuree.gender.code, 'Gender', 'Insuree without gender.'),
                'Poverty': claim.insuree.family.poverty if claim.insuree.family else None,
                'QuantityProvided': int(claim_item.qty_provided),
                'ItemPrice': float(claim_item.s.price),
                'PriceAsked': float(claim_item.price_asked),
                'DateFrom': claim.date_from,
                'DateTo': claim.date_to or claim.date_from,
                'DateClaimed': claim.date_claimed,
                'ItemFrequency': claim_item.s.frequency,
                'ItemPatCat': claim_item.s.patient_category,
                'ItemLevel': claim_item.s.level if isinstance(claim_item, ClaimService) else 'M',
                'HFLevel': claim.health_facility.level,
                'HFCareType': claim.health_facility.care_type,  # Note: Field can be empty, its ' ' by default.
                'VisitType': claim.visit_type,
                'RejectionReason': claim_item.rejection_reason,
                'PriceValuated': float(claim_item.price_valuated or 0),
                'HfUUID': claim.admin.health_facility.uuid,
                'ClaimAdminUUID': claim.admin.uuid,
                'InsureeUUID': claim.insuree.uuid,
                'ClaimUUID': claim.uuid,
                'New': claim.New  # annotated
            })
        return o
