import itertools
import logging
from abc import ABC, abstractmethod

from typing import List, Tuple, TypeVar, Iterable, Generic, Any

from fhir.resources.bundle import Bundle

from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig
from claim_ai.evaluation.input_models import FhirAiInputModel
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult, ClaimProvisionEvaluationResult

logger = logging.getLogger(__name__)

V_IN = TypeVar('V_IN')  # Valid bundle input_bundle
IV_IN = TypeVar('IV_IN')  # Invalid bundle input_bundle
CLAIM_TYPE = TypeVar('CLAIM_TYPE')  # Valid bundle input_bundle
ITEM_TYPE = TypeVar('ITEM_TYPE')  # Invalid bundle input_bundle
ERROR_TYPE = TypeVar('ERROR_TYPE')  # Invalid bundle input_bundle


class BaseClaimResponseBundleBuilder(Generic[V_IN, IV_IN, CLAIM_TYPE, ITEM_TYPE, ERROR_TYPE], ABC):
    def __init__(self, claim_response_factory):
        self.claim_response_factory = claim_response_factory

    def build_fhir_bundle(self, valid_claims_output: V_IN, invalid_valid_claims: IV_IN):
        return Bundle(**self.build_fhir_bundle_dict(valid_claims_output, invalid_valid_claims))

    def build_valid(self, valid_claims_output: V_IN):
        return Bundle(**self.build_fhir_bundle_dict(valid_claims_output, None))

    def build_fhir_bundle_dict(self, valid_claims_output: V_IN, invalid_valid_claims: IV_IN):
        return {
            'type': "collection",
            'entry': self._build_entries_from_input(valid_claims_output, invalid_valid_claims)
        }

    def _build_entries_from_input(self, valid_claims_output: V_IN, invalid_valid_claims: IV_IN):
        resources = []
        for claim, claim_items in self._group_valid_input(valid_claims_output):
            resources.append({
                'fullUrl': self._build_resource_url(claim),
                'resource': self._build_valid_entry(claim, claim_items)
            })

        for claim, error_reason in self._group_invalid_input(invalid_valid_claims):
            resources.append({
                'fullUrl': self._build_resource_url(claim),
                'resource': self._build_invalid_entry(claim, error_reason)
            })

        return resources

    def _build_resource_url(self, next_element: CLAIM_TYPE):
        return ClaimAiConfig.claim_response_url + '/' + str(self._get_resource_url_identifier(next_element))

    @abstractmethod
    def _get_resource_url_identifier(self, input_element: CLAIM_TYPE) -> str:
        pass

    @abstractmethod
    def _group_valid_input(self, valid_claims_output: V_IN) \
            -> Iterable[Tuple[CLAIM_TYPE, Iterable[ITEM_TYPE]]]:
        pass

    @abstractmethod
    def _group_invalid_input(self, valid_claims_output: IV_IN)\
            -> Iterable[Tuple[CLAIM_TYPE, ERROR_TYPE]]:
        pass

    def _build_valid_entry(self, claim: CLAIM_TYPE, claim_items: Iterable[ClaimProvisionEvaluationResult]):
        builder = self.claim_response_factory.get_builder(claim.__class__.__name__)
        return builder.build_valid_claim_response(claim, claim_items)

    def _build_invalid_entry(self, claim: CLAIM_TYPE, error_reason: str):
        builder = self.claim_response_factory.get_builder(claim.__class__.__name__)
        return builder.build_claim_response_error(claim, error_reason)


class EvaluationResultClaimResponseBundleBuilder(
    BaseClaimResponseBundleBuilder[Iterable[EvaluationResult], Iterable[Tuple[dict, str]], FhirAiInputModel, dict, str]
):
    def _get_resource_url_identifier(self, input_element: dict):
        return input_element['id']

    def _group_valid_input(self, valid_claims_output):
        return itertools.groupby(valid_claims_output, lambda x: x.claim)

    def _group_invalid_input(self, valid_claims_output):
        return valid_claims_output


class ClaimBundleEvaluationClaimResponseBundleBuilder(
    BaseClaimResponseBundleBuilder[ClaimBundleEvaluation, Any, SingleClaimEvaluationResult, Any, str]
):
    def _get_resource_url_identifier(self, input_element: SingleClaimEvaluationResult):
        return input_element.claim.uuid

    def _group_valid_input(self, valid_claims_output: ClaimBundleEvaluation) \
            -> Iterable[Tuple[SingleClaimEvaluationResult, Iterable[ClaimProvisionEvaluationResult]]]:
        return [(x, x.evaluated_items.all()) for x in valid_claims_output.claims.all()]

    def _group_invalid_input(self, valid_claims_output:  List[Tuple[dict, str]]) \
            -> Iterable[Tuple[SingleClaimEvaluationResult, str]]:
        return []
