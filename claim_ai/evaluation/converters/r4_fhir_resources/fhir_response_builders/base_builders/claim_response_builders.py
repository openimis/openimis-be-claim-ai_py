from abc import ABC, abstractmethod

from fhir.resources.claimresponse import ClaimResponse

from api_fhir_r4.converters import ClaimConverter, ClaimResponseConverter
from api_fhir_r4.mapping.claimMapping import ClaimVisitTypeMapping
from api_fhir_r4.utils import TimeUtils
from claim_ai.evaluation.evaluation_result import EvaluationResult
from claim_ai.apps import ClaimAiConfig
from claim_ai.models import SingleClaimEvaluationResult, ClaimProvisionEvaluationResult


class BaseClaimResponseBuilder(ABC):
    def __init__(self, adjudication_builder_factory):
        self.adjudication_builder_factory = adjudication_builder_factory

    def build_valid_claim_response(self, claim, items):
        return ClaimResponse(**self.build_valid_claim_response_dict(claim, items))

    def build_claim_response_error(self, claim, reason):
        return ClaimResponse(**self.build_claim_response_error_dict(claim, reason))

    def build_valid_claim_response_dict(self, claim, items):
        return {
            **self.claim_response_fields(claim),
            "outcome": "complete",
            "item": self._build_claim_items(items)
        }

    def build_claim_response_error_dict(self, claim, error_reason):
        return {
            **self.claim_response_fields(claim),
            "outcome": "error",
            "error": [
                {
                    "coding": [{
                        "code": "-1"
                    }],
                    "text": error_reason
                }
            ]
        }

    def claim_response_fields(self, claim):
        return {
            "resourceType": "ClaimResponse",
            "status": self._get_claim_status(claim),
            "type": self._get_claim_type(claim),
            "use": self._get_claim_use(claim),
            "patient": {
                "reference": self._get_claim_patient_reference(claim)
            },
            "created": TimeUtils.date().isoformat(),
            "insurer": {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
            },
            "id": self._get_claim_id(claim),
            "request": {
                "reference": F"Claim/{self._get_claim_id(claim)}",
            }
        }

    def _build_claim_items(self, items):
        response_items = []
        sequence = 1
        for entry in items:
            provided = self._get_provided(entry)
            result = self._get_result(entry)  # result is in str type
            response_item = self._provision_to_claim_response_item(provided, result, sequence)
            response_items.append(response_item)
            sequence += 1

        return response_items

    def _provision_to_claim_response_item(self, provision, evaluation_result, sequence):
        builder = self.adjudication_builder_factory.get_builder(provision.__class__.__name__)
        return builder.build_claim_response_item_adjudication(provision, evaluation_result, sequence)

    @abstractmethod
    def _get_claim_status(self, claim):
        pass

    @abstractmethod
    def _get_claim_type(self, claim):
        pass

    @abstractmethod
    def _get_claim_use(self, claim):
        pass

    @abstractmethod
    def _get_claim_patient_reference(self, claim):
        pass

    @abstractmethod
    def _get_claim_id(self, claim):
        pass

    @abstractmethod
    def _get_provided(self, entry):
        pass

    @abstractmethod
    def _get_result(self, entry) -> str:
        pass


class EvaluationResultClaimResponseBuilder(BaseClaimResponseBuilder):
    def _get_claim_status(self, claim: dict):
        return claim['status']

    def _get_claim_type(self, claim: dict):
        return claim['type']

    def _get_claim_use(self, claim: dict):
        return claim['use']

    def _get_claim_patient_reference(self, claim: dict):
        return claim['patient']['reference']

    def _get_claim_id(self, claim: dict):
        return claim['id']

    def _get_provided(self, entry: EvaluationResult):
        return entry.input

    def _get_result(self, entry: EvaluationResult) -> str:
        return str(entry.result)


class ClaimEvaluationResultClaimResponseBuilder(BaseClaimResponseBuilder):
    def claim_response_fields(self, claim):
        base = ClaimResponseConverter.to_fhir_obj(claim.claim).dict()
        base['insurer'] = {
                "reference": F"Organization/{ClaimAiConfig.claim_response_organization}"
        }
        return base

    def _get_claim_status(self, claim: SingleClaimEvaluationResult):
        return claim.claim.status

    def _get_claim_type(self, claim: SingleClaimEvaluationResult):
        claim = claim.claim
        mapping = ClaimVisitTypeMapping.fhir_claim_visit_type_coding[claim.visit_type]
        return ClaimConverter.build_codeable_concept_from_coding(ClaimConverter.build_fhir_mapped_coding(mapping))

    def _get_claim_use(self, claim: SingleClaimEvaluationResult):
        return 'claim'

    def _get_claim_patient_reference(self, claim: SingleClaimEvaluationResult):
        return ClaimConverter.build_fhir_resource_reference(
            claim.claim.insuree, type='Patient', display=claim.claim.insuree.chf_id).reference

    def _get_claim_id(self, claim: SingleClaimEvaluationResult):
        return claim.claim.pk

    def _get_provided(self, entry: ClaimProvisionEvaluationResult):
        return entry

    def _get_result(self, entry: ClaimProvisionEvaluationResult) -> str:
        return str(entry.evaluation)
